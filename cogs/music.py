"""
Advanced Music Cog for Discord Bot
Provides comprehensive music playback, streaming, and management capabilities.
"""

import asyncio
import json
import logging
import os
import re
from collections import defaultdict, deque, Counter
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import aiohttp
import discord
import spotipy
from discord.ext import commands, tasks
import yt_dlp
from youtube_search import YoutubeSearch

from .music_config import (
    AUDIO_QUALITY, EQUALIZER_PRESETS, MOOD_PLAYLISTS, DECADE_PLAYLISTS,
    GENRES, LOOP_MODES, PLAY_STATUS, SPECIAL_EFFECTS, COMMAND_HELP,
    ERROR_MESSAGES, SUCCESS_MESSAGES, EMBED_COLORS, MAX_QUEUE_SIZE,
    MAX_FAVORITES, MAX_PLAYLISTS, DEFAULT_SETTINGS, API_ENDPOINTS, SOURCE_PATTERNS
)

logger = logging.getLogger(__name__)


class Song:
    """Represents a song in the queue."""
    
    def __init__(self, title: str, url: str, duration: int, requester: discord.User,
                 source: str = 'youtube', thumbnail: str = None, artist: str = None,
                 album: str = None, explicit: bool = False, genre: str = None,
                 year: int = None, preview_url: str = None):
        self.title = title
        self.url = url
        self.duration = duration
        self.requester = requester
        self.source = source
        self.thumbnail = thumbnail
        self.artist = artist
        self.album = album
        self.explicit = explicit
        self.genre = genre
        self.year = year
        self.preview_url = preview_url
        self.added_at = datetime.now()
        self.play_count = 0
        
    def to_dict(self) -> dict:
        """Convert song to dictionary."""
        return {
            'title': self.title,
            'url': self.url,
            'duration': self.duration,
            'requester_id': self.requester.id,
            'source': self.source,
            'thumbnail': self.thumbnail,
            'artist': self.artist,
            'album': self.album,
            'explicit': self.explicit,
            'genre': self.genre,
            'year': self.year,
            'preview_url': self.preview_url,
            'added_at': self.added_at.isoformat(),
        }
    
    def get_display_name(self) -> str:
        """Get display name with artist if available."""
        if self.artist:
            return f"{self.artist} - {self.title}"
        return self.title


class MusicPlayer:
    """Manages music playback state for a guild."""
    
    def __init__(self, guild_id: int):
        self.guild_id = guild_id
        self.queue: deque[Song] = deque()
        self.history: deque[Song] = deque(maxlen=100)
        self.current_song: Optional[Song] = None
        self.is_playing = False
        self.is_paused = False
        self.volume = 100
        self.speed = 1.0
        self.loop_mode = 'none'  # none, one, all
        self.current_position = 0
        self.start_time = None
        self.equalizer = list(EQUALIZER_PRESETS['flat']['values'])
        self.bass_boost = False
        self.nightcore_enabled = False
        self.slowed_enabled = False
        self.reverse_enabled = False
        self.radio_mode = False
        self.radio_seed: Optional[Song] = None
        self.radio_mode_type = 'artist'  # artist, genre, decade
        
        # User data
        self.favorite_songs: List[Song] = []
        self.playlists: Dict[str, List[Song]] = {}
        self.blacklist_songs = set()
        self.blacklist_artists = set()
        self.voting_skip = {'yes': set(), 'no': set()}
        self.user_preferences: Dict[int, dict] = defaultdict(lambda: {
            'favorite_genres': [],
            'preferred_quality': '320',
            'allow_explicit': True,
            'auto_play': True,
        })
        
        # Statistics and analytics
        self.listening_history: Dict[int, List[dict]] = defaultdict(list)
        self.user_stats: Dict[int, dict] = defaultdict(lambda: {
            'total_songs_played': 0,
            'total_listening_time': 0,
            'top_artists': defaultdict(int),
            'top_genres': defaultdict(int),
            'top_songs': defaultdict(int),
            'listening_streak': 0,
            'last_listen_date': None,
        })
        
        # Server statistics
        self.server_stats = {
            'total_plays': 0,
            'unique_users': set(),
            'peak_hour': defaultdict(int),
            'daily_plays': defaultdict(int),
            'top_songs': defaultdict(int),
            'top_artists': defaultdict(int),
        }
        
        # Session data
        self.session_start = datetime.now()
        self.total_session_time = 0
    
    def add_to_queue(self, song: Song):
        """Add song to queue."""
        # Check blacklist
        if song.title in self.blacklist_songs or (song.artist and song.artist in self.blacklist_artists):
            return False
            
        # Check duplicate prevention (optional)
        self.queue.append(song)
        self.listening_history[song.requester.id].append({
            'song': song.to_dict(),
            'timestamp': datetime.now().isoformat(),
        })
        return True
    
    def remove_from_queue(self, index: int) -> Optional[Song]:
        """Remove song from queue at index."""
        if 0 <= index < len(self.queue):
            queue_list = list(self.queue)
            song = queue_list.pop(index)
            self.queue = deque(queue_list)
            return song
        return None
    
    def move_song(self, from_index: int, to_index: int) -> bool:
        """Move song in queue."""
        if 0 <= from_index < len(self.queue) and 0 <= to_index < len(self.queue):
            queue_list = list(self.queue)
            song = queue_list.pop(from_index)
            queue_list.insert(to_index, song)
            self.queue = deque(queue_list)
            return True
        return False
    
    def insert_song(self, index: int, song: Song) -> bool:
        """Insert song at specific position."""
        if 0 <= index <= len(self.queue):
            queue_list = list(self.queue)
            queue_list.insert(index, song)
            self.queue = deque(queue_list)
            return True
        return False
    
    def shuffle_queue(self):
        """Shuffle the queue."""
        import random
        queue_list = list(self.queue)
        random.shuffle(queue_list)
        self.queue = deque(queue_list)
    
    def clear_queue(self):
        """Clear the entire queue."""
        self.queue.clear()
    
    def sort_queue(self, sort_by: str):
        """Sort queue by various criteria."""
        queue_list = list(self.queue)
        if sort_by == 'artist':
            queue_list.sort(key=lambda x: x.artist or 'Unknown')
        elif sort_by == 'duration':
            queue_list.sort(key=lambda x: x.duration)
        elif sort_by == 'date_added':
            queue_list.sort(key=lambda x: x.added_at)
        elif sort_by == 'title':
            queue_list.sort(key=lambda x: x.title)
        self.queue = deque(queue_list)
    
    def get_next_song(self) -> Optional[Song]:
        """Get next song from queue."""
        # Handle loop modes
        if self.loop_mode == 'one' and self.current_song:
            return self.current_song
        
        # Get next from queue
        if self.queue:
            song = self.queue.popleft()
            
            # Radio mode - add similar songs automatically
            if self.radio_mode and not self.queue:
                similar_song = self._get_radio_recommendation()
                if similar_song:
                    self.queue.append(similar_song)
            
            return song
        
        # Auto-fill queue when low
        if len(self.queue) < 3:
            auto_song = self._get_auto_recommendation()
            if auto_song:
                self.queue.append(auto_song)
        
        return None
    
    def save_queue_as_playlist(self, playlist_name: str) -> bool:
        """Save current queue as a playlist."""
        if len(self.playlists) >= MAX_PLAYLISTS:
            return False
        
        if playlist_name not in self.playlists:
            self.playlists[playlist_name] = list(self.queue)
            return True
        return False
    
    def load_playlist(self, playlist_name: str) -> bool:
        """Load a saved playlist into queue."""
        if playlist_name in self.playlists:
            self.queue.extend(self.playlists[playlist_name])
            return True
        return False
    
    def _get_radio_recommendation(self) -> Optional[Song]:
        """Get radio mode recommendation."""
        if not self.radio_seed:
            return None
        
        # This would normally use recommendation algorithms
        # For now, return a placeholder that would be filled by actual API calls
        return Song(
            title=f"Similar to {self.radio_seed.title}",
            url="",  # Would be filled by API
            duration=180,  # 3 minutes default
            requester=self.current_song.requester if self.current_song else None,
            source='radio',
            artist=self.radio_seed.artist,
        )
    
    def _get_auto_recommendation(self) -> Optional[Song]:
        """Get automatic recommendation based on user's taste."""
        # Placeholder for auto-recommendation logic
        return None
    
    def enable_radio_mode(self, seed_song: Song, mode: str = 'artist'):
        """Enable radio mode."""
        self.radio_mode = True
        self.radio_seed = seed_song
        self.radio_mode_type = mode
    
    def disable_radio_mode(self):
        """Disable radio mode."""
        self.radio_mode = False
        self.radio_seed = None
    
    def record_play(self, song: Song, user_id: int):
        """Record a song play for statistics."""
        # User statistics
        stats = self.user_stats[user_id]
        stats['total_songs_played'] += 1
        stats['total_listening_time'] += song.duration
        stats['top_songs'][song.title] += 1
        
        if song.artist:
            stats['top_artists'][song.artist] += 1
        if song.genre:
            stats['top_genres'][song.genre] += 1
        
        # Update listening streak
        today = datetime.now().date()
        if stats['last_listen_date']:
            last_date = datetime.fromisoformat(stats['last_listen_date']).date()
            if (today - last_date).days == 1:
                stats['listening_streak'] += 1
            elif (today - last_date).days > 1:
                stats['listening_streak'] = 1
        else:
            stats['listening_streak'] = 1
        
        stats['last_listen_date'] = today.isoformat()
        
        # Server statistics
        self.server_stats['total_plays'] += 1
        self.server_stats['unique_users'].add(user_id)
        self.server_stats['top_songs'][song.title] += 1
        
        if song.artist:
            self.server_stats['top_artists'][song.artist] += 1
        
        # Hourly tracking
        hour = datetime.now().hour
        self.server_stats['peak_hour'][hour] += 1
        
        # Daily tracking
        date_str = today.isoformat()
        self.server_stats['daily_plays'][date_str] += 1
        
        song.play_count += 1
    
    def get_top_songs(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Get top songs by play count."""
        return sorted(self.server_stats['top_songs'].items(), key=lambda x: x[1], reverse=True)[:limit]
    
    def get_top_artists(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Get top artists by play count."""
        return sorted(self.server_stats['top_artists'].items(), key=lambda x: x[1], reverse=True)[:limit]
    
    def get_user_recommendations(self, user_id: int, limit: int = 10) -> List[dict]:
        """Get personalized recommendations for user."""
        stats = self.user_stats[user_id]
        
        # Get top genres and artists
        top_genres = sorted(stats['top_genres'].items(), key=lambda x: x[1], reverse=True)[:5]
        top_artists = sorted(stats['top_artists'].items(), key=lambda x: x[1], reverse=True)[:5]
        
        recommendations = []
        
        # Genre-based recommendations
        for genre, count in top_genres:
            recommendations.append({
                'type': 'genre',
                'value': genre,
                'weight': count,
                'search_query': f"{genre} music"
            })
        
        # Artist-based recommendations
        for artist, count in top_artists:
            recommendations.append({
                'type': 'artist',
                'value': artist,
                'weight': count,
                'search_query': f"songs by {artist}"
            })
        
        return sorted(recommendations, key=lambda x: x['weight'], reverse=True)[:limit]
    
    def get_server_insights(self) -> dict:
        """Get comprehensive server music insights."""
        insights = {
            'total_plays': self.server_stats['total_plays'],
            'unique_listeners': len(self.server_stats['unique_users']),
            'peak_hour': max(self.server_stats['peak_hour'].items(), key=lambda x: x[1])[0] if self.server_stats['peak_hour'] else None,
            'total_songs_played': len(self.server_stats['top_songs']),
            'total_artists_played': len(self.server_stats['top_artists']),
        }
        
        # Most popular song and artist
        if self.server_stats['top_songs']:
            insights['most_popular_song'] = max(self.server_stats['top_songs'].items(), key=lambda x: x[1])
        
        if self.server_stats['top_artists']:
            insights['most_popular_artist'] = max(self.server_stats['top_artists'].items(), key=lambda x: x[1])
        
        # Average plays per listener
        if insights['unique_listeners'] > 0:
            insights['avg_plays_per_listener'] = round(insights['total_plays'] / insights['unique_listeners'], 2)
        
        # Session duration
        session_duration = datetime.now() - self.session_start
        insights['session_duration'] = str(session_duration).split('.')[0]  # Remove microseconds
        
        return insights


class LyricsManager:
    """Manage lyrics fetching from multiple sources."""
    
    @staticmethod
    async def get_lyrics_ovh(artist: str, song: str) -> Optional[str]:
        """Get lyrics from Lyrics.ovh API."""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{API_ENDPOINTS['lyrics_ovh']}/{artist}/{song}"
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get('lyrics')
        except Exception as e:
            logger.error(f"Error fetching lyrics from Lyrics.ovh: {e}")
        return None
    
    @staticmethod
    async def get_lyrics_genius(song_title: str, artist: str) -> Optional[str]:
        """Get lyrics from Genius API."""
        genius_token = os.getenv('GENIUS_TOKEN')
        if not genius_token:
            return None
        
        try:
            headers = {"Authorization": f"Bearer {genius_token}"}
            search_url = f"{API_ENDPOINTS['genius']}/search"
            params = {"q": f"{song_title} {artist}"}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, headers=headers, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data['response']['hits']:
                            song_url = data['response']['hits'][0]['result']['url']
                            
                            async with session.get(song_url) as lyrics_resp:
                                if lyrics_resp.status == 200:
                                    return await lyrics_resp.text()
        except Exception as e:
            logger.error(f"Error fetching lyrics from Genius: {e}")
        return None
    
    @classmethod
    async def get_lyrics(cls, song_title: str, artist: str = None) -> Optional[str]:
        """Get lyrics from available sources."""
        if artist:
            lyrics = await cls.get_lyrics_ovh(artist, song_title)
            if lyrics:
                return lyrics
        
        lyrics = await cls.get_lyrics_genius(song_title, artist or '')
        if lyrics:
            return lyrics
        
        return None


class SearchManager:
    """Manage searching across multiple music sources."""
    
    @staticmethod
    def detect_source(url: str) -> str:
        """Detect music source from URL."""
        url = url.lower()
        
        for source, patterns in SOURCE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, url):
                    return source
        
        return 'youtube'  # Default fallback
    
    @staticmethod
    async def search_youtube(query: str, max_results: int = 5) -> List[dict]:
        """Search YouTube for music."""
        try:
            results = YoutubeSearch(query, max_results=max_results).to_dict()
            formatted_results = []
            
            for result in results:
                formatted_results.append({
                    'title': result.get('title'),
                    'url': f"https://www.youtube.com/watch?v={result.get('id')}",
                    'thumbnail': result.get('thumbnails', [None])[0],
                    'channel': result.get('channel'),
                    'source': 'youtube',
                    'duration': 180,  # Placeholder - would extract from result
                })
            
            return formatted_results
        except Exception as e:
            logger.error(f"Error searching YouTube: {e}")
            return []
    
    @staticmethod
    async def search_spotify(query: str, search_type: str = 'track', max_results: int = 5) -> List[dict]:
        """Search Spotify for music."""
        try:
            client_id = os.getenv('SPOTIFY_CLIENT_ID')
            client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
            
            if not client_id or not client_secret:
                logger.warning("Spotify credentials not configured")
                return []
            
            from spotipy.oauth2 import SpotifyClientCredentials
            auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
            sp = spotipy.Spotify(auth_manager=auth_manager)
            
            results = sp.search(q=query, type=search_type, limit=max_results)
            formatted_results = []
            
            if search_type == 'track':
                for item in results['tracks']['items']:
                    formatted_results.append({
                        'title': item['name'],
                        'artist': item['artists'][0]['name'] if item['artists'] else 'Unknown',
                        'url': item['external_urls']['spotify'],
                        'thumbnail': item['album']['images'][0]['url'] if item['album']['images'] else None,
                        'album': item['album']['name'],
                        'duration': item['duration_ms'] // 1000,
                        'explicit': item['explicit'],
                        'source': 'spotify'
                    })
            
            return formatted_results
        except Exception as e:
            logger.error(f"Error searching Spotify: {e}")
            return []
    
    @staticmethod
    async def get_song_info(url: str) -> Optional[dict]:
        """Get song info from URL using yt-dlp."""
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'quiet': True,
                'no_warnings': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return {
                    'title': info.get('title', 'Unknown'),
                    'url': url,
                    'duration': info.get('duration', 0),
                    'thumbnail': info.get('thumbnail', ''),
                    'artist': info.get('uploader', 'Unknown'),
                    'source': SearchManager.detect_source(url),
                }
        except Exception as e:
            logger.error(f"Error getting song info: {e}")
            return None


class MusicCog(commands.Cog):
    """Advanced music playback cog with comprehensive features."""
    
    def __init__(self, bot):
        self.bot = bot
        self.players: Dict[int, MusicPlayer] = {}
        self.voice_clients: Dict[int, discord.VoiceClient] = {}
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'default_search': 'ytsearch',
            'socket_timeout': 30,
        }
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Advanced features
        self.search_cache: Dict[str, List[dict]] = {}
        self.popular_searches: Counter = Counter()
        self.user_recommendations: Dict[int, List[dict]] = defaultdict(list)
        
        # Background tasks
        self.cache_cleanup.start()
    
    async def cog_load(self):
        """Initialize the cog."""
        self.session = aiohttp.ClientSession()
    
    async def cog_unload(self):
        """Clean up the cog."""
        if self.session:
            await self.session.close()
        self.cache_cleanup.cancel()
    
    @tasks.loop(hours=6)
    async def cache_cleanup(self):
        """Clean up old cache entries."""
        current_time = datetime.now()
        # Remove cache entries older than 6 hours
        for query in list(self.search_cache.keys()):
            # This is a simplified cleanup - in production you'd track cache timestamps
            if len(self.search_cache) > 100:  # Limit cache size
                del self.search_cache[query]
    
    def get_player(self, guild_id: int) -> MusicPlayer:
        """Get or create player for guild."""
        if guild_id not in self.players:
            self.players[guild_id] = MusicPlayer(guild_id)
        return self.players[guild_id]
    
    def check_permissions(self, ctx) -> bool:
        """Check if user has DJ permissions."""
        # Check if user is in voice channel with bot
        if not ctx.author.voice:
            return False
        
        player = self.get_player(ctx.guild.id)
        if not player.current_song:
            return False
        
        # Check if user is in same voice channel as bot
        bot_voice = ctx.guild.voice_client
        if not bot_voice or not bot_voice.channel:
            return False
        
        return ctx.author.voice.channel == bot_voice.channel
    
    # Core Playback Commands
    
    @commands.hybrid_command(name='play', description='Play a song from YouTube, Spotify, or other sources')
    async def play(self, ctx, *, query: str):
        """Play a song from various sources."""
        if not ctx.author.voice:
            await ctx.send(ERROR_MESSAGES['not_in_voice'], ephemeral=True)
            return
        
        async with ctx.typing():
            player = self.get_player(ctx.guild.id)
            
            try:
                # Detect if input is URL or search query
                if query.startswith(('http://', 'https://')):
                    # Direct URL
                    song_info = await SearchManager.get_song_info(query)
                    if not song_info:
                        await ctx.send(ERROR_MESSAGES['search_failed'], ephemeral=True)
                        return
                else:
                    # Search query
                    cache_key = f"yt_{query.lower()}"
                    if cache_key in self.search_cache:
                        search_results = self.search_cache[cache_key]
                    else:
                        search_results = await SearchManager.search_youtube(query)
                        if search_results:
                            self.search_cache[cache_key] = search_results
                            self.popular_searches[query] += 1
                    
                    if not search_results:
                        await ctx.send(ERROR_MESSAGES['no_results'], ephemeral=True)
                        return
                    
                    # Use first result
                    song_info = search_results[0]
                
                # Create song object
                song = Song(
                    title=song_info['title'],
                    url=song_info['url'],
                    duration=song_info.get('duration', 0),
                    requester=ctx.author,
                    source=song_info.get('source', 'youtube'),
                    thumbnail=song_info.get('thumbnail'),
                    artist=song_info.get('artist'),
                    album=song_info.get('album'),
                    explicit=song_info.get('explicit', False)
                )
                
                # Add to queue
                if player.add_to_queue(song):
                    # Create success embed
                    embed = discord.Embed(
                        title="✅ Added to Queue",
                        color=EMBED_COLORS['success']
                    )
                    embed.add_field(name="Title", value=song.get_display_name(), inline=False)
                    embed.add_field(name="Duration", value=self._format_duration(song.duration), inline=True)
                    embed.add_field(name="Queue Position", value=f"#{len(player.queue)}", inline=True)
                    embed.add_field(name="Source", value=song.source.capitalize(), inline=True)
                    
                    if song.thumbnail:
                        embed.set_thumbnail(url=song.thumbnail)
                    
                    await ctx.send(embed=embed, ephemeral=True)
                    
                    # Start playing if not already playing
                    if not player.is_playing:
                        await self._play_next(ctx)
                else:
                    await ctx.send("❌ This song is blacklisted!", ephemeral=True)
                    
            except Exception as e:
                logger.error(f"Error playing song: {e}")
                await ctx.send(f"❌ An error occurred: {str(e)[:100]}", ephemeral=True)
    
    @commands.hybrid_command(name='pause', description='Pause the current song')
    async def pause(self, ctx):
        """Pause the current song."""
        if not self.check_permissions(ctx):
            await ctx.send(ERROR_MESSAGES['user_not_in_bot_channel'], ephemeral=True)
            return
        
        player = self.get_player(ctx.guild.id)
        
        if not player.is_playing:
            await ctx.send(ERROR_MESSAGES['no_song_playing'], ephemeral=True)
            return
        
        player.is_paused = True
        
        embed = discord.Embed(
            title="⏸️ Paused",
            description=f"**{player.current_song.get_display_name()}**",
            color=EMBED_COLORS['warning']
        )
        await ctx.send(embed=embed, ephemeral=True)
    
    @commands.hybrid_command(name='resume', description='Resume the paused song')
    async def resume(self, ctx):
        """Resume the paused song."""
        if not self.check_permissions(ctx):
            await ctx.send(ERROR_MESSAGES['user_not_in_bot_channel'], ephemeral=True)
            return
        
        player = self.get_player(ctx.guild.id)
        
        if not player.current_song or not player.is_paused:
            await ctx.send("❌ No paused song to resume!", ephemeral=True)
            return
        
        player.is_paused = False
        
        embed = discord.Embed(
            title="▶️ Resumed",
            description=f"**{player.current_song.get_display_name()}**",
            color=EMBED_COLORS['success']
        )
        await ctx.send(embed=embed, ephemeral=True)
    
    @commands.hybrid_command(name='skip', description='Skip the current song')
    async def skip(self, ctx):
        """Skip the current song."""
        if not self.check_permissions(ctx):
            await ctx.send(ERROR_MESSAGES['user_not_in_bot_channel'], ephemeral=True)
            return
        
        player = self.get_player(ctx.guild.id)
        
        if not player.is_playing:
            await ctx.send(ERROR_MESSAGES['no_song_playing'], ephemeral=True)
            return
        
        # Check voting system
        if len(player.queue) > 0:
            player.voting_skip['yes'].add(ctx.author.id)
            required_votes = DEFAULT_SETTINGS['skip_votes']
            
            if len(player.voting_skip['yes']) >= required_votes:
                # Enough votes - skip song
                await self._skip_song(ctx)
                return
            else:
                # Show voting status
                votes_needed = required_votes - len(player.voting_skip['yes'])
                embed = discord.Embed(
                    title="🗳️ Vote to Skip",
                    description=f"{len(player.voting_skip['yes'])}/{required_votes} votes\n{votes_needed} more needed",
                    color=EMBED_COLORS['info']
                )
                await ctx.send(embed=embed, ephemeral=True)
                return
        
        # No voting needed for empty queue
        await self._skip_song(ctx)
    
    @commands.hybrid_command(name='stop', description='Stop music and clear queue')
    async def stop(self, ctx):
        """Stop playing music."""
        if not self.check_permissions(ctx):
            await ctx.send(ERROR_MESSAGES['user_not_in_bot_channel'], ephemeral=True)
            return
        
        player = self.get_player(ctx.guild.id)
        
        if not player.is_playing:
            await ctx.send(ERROR_MESSAGES['no_song_playing'], ephemeral=True)
            return
        
        # Clean up voice connection
        if ctx.guild.voice_client:
            await ctx.guild.voice_client.disconnect()
        
        # Reset player state
        player.is_playing = False
        player.is_paused = False
        player.clear_queue()
        player.current_song = None
        player.voting_skip = {'yes': set(), 'no': set()}
        
        embed = discord.Embed(
            title="⏹️ Stopped",
            description="Music stopped and queue cleared.",
            color=EMBED_COLORS['error']
        )
        await ctx.send(embed=embed, ephemeral=True)
    
    async def _skip_song(self, ctx):
        """Internal skip song method."""
        player = self.get_player(ctx.guild.id)
        current = player.current_song
        
        embed = discord.Embed(
            title="⏭️ Skipped",
            description=f"**{current.get_display_name()}**",
            color=EMBED_COLORS['success']
        )
        await ctx.send(embed=embed, ephemeral=True)
        
        player.voting_skip = {'yes': set(), 'no': set()}
        await self._play_next(ctx)
    
    @commands.hybrid_command(name='queue', description='Show the current music queue')
    async def queue_command(self, ctx, page: int = 1):
        """Display the music queue."""
        player = self.get_player(ctx.guild.id)
        
        if not player.queue and not player.current_song:
            await ctx.send(ERROR_MESSAGES['empty_queue'], ephemeral=True)
            return
        
        # Pagination
        page_size = 10
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        queue_list = list(player.queue)
        total_pages = (len(queue_list) + page_size - 1) // page_size
        
        if page < 1 or page > total_pages:
            await ctx.send(f"❌ Invalid page. Total pages: {max(total_pages, 1)}", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🎵 Music Queue",
            color=EMBED_COLORS['queue']
        )
        
        # Current song
        if player.current_song:
            song = player.current_song
            current_pos = self._format_duration(player.current_position)
            total_dur = self._format_duration(song.duration)
            progress = self._create_progress_bar(player.current_position, song.duration)
            
            embed.add_field(
                name="🎵 Now Playing",
                value=f"**{song.get_display_name()}**\n{progress}\n{current_pos}/{total_dur}\n"
                      f"Requested by {song.requester.mention}",
                inline=False
            )
        
        # Queue items
        if queue_list:
            queue_str = ""
            for i in range(start_idx, min(end_idx, len(queue_list))):
                song = queue_list[i]
                queue_str += f"{i+1}. **{song.get_display_name()}** [{self._format_duration(song.duration)}]\n"
            
            embed.add_field(
                name=f"📋 Queue (Page {page}/{max(total_pages, 1)})",
                value=queue_str,
                inline=False
            )
        
        # Queue stats
        total_duration = sum(song.duration for song in queue_list)
        total_songs = len(queue_list) + (1 if player.current_song else 0)
        
        embed.add_field(
            name="📊 Queue Stats",
            value=f"Total Songs: {total_songs}\n"
                  f"Queue Duration: {self._format_duration(total_duration)}\n"
                  f"Loop Mode: {player.loop_mode.title()}\n"
                  f"Radio Mode: {'On' if player.radio_mode else 'Off'}",
            inline=True
        )
        
        await ctx.send(embed=embed, ephemeral=True)
    
    @commands.hybrid_command(name='nowplaying', aliases=['np'], description='Show now playing song')
    async def nowplaying(self, ctx):
        """Show the currently playing song."""
        player = self.get_player(ctx.guild.id)
        
        if not player.current_song:
            await ctx.send(ERROR_MESSAGES['no_song_playing'], ephemeral=True)
            return
        
        song = player.current_song
        progress = self._create_progress_bar(player.current_position, song.duration)
        
        embed = discord.Embed(
            title="🎵 Now Playing",
            color=EMBED_COLORS['now_playing']
        )
        
        # Main info
        embed.add_field(name="Title", value=song.get_display_name(), inline=False)
        embed.add_field(name="Artist", value=song.artist or "Unknown", inline=True)
        embed.add_field(name="Album", value=song.album or "Unknown", inline=True)
        embed.add_field(name="Source", value=song.source.capitalize(), inline=True)
        embed.add_field(name="Duration", value=self._format_duration(song.duration), inline=True)
        
        # Progress
        embed.add_field(
            name="Progress",
            value=f"{progress}\n{self._format_duration(player.current_position)} / {self._format_duration(song.duration)}",
            inline=False
        )
        
        # Additional info
        quality_indicators = []
        if song.explicit:
            quality_indicators.append("🔞 Explicit")
        if song.genre:
            quality_indicators.append(f"🎵 {song.genre}")
        if song.year:
            quality_indicators.append(f"📅 {song.year}")
        
        if quality_indicators:
            embed.add_field(name="Details", value=" • ".join(quality_indicators), inline=False)
        
        # Requester and position
        position_info = f"Requested by {song.requester.mention}"
        if player.radio_mode:
            position_info += f"\n📻 Radio Mode: {player.radio_mode_type.title()}"
        
        embed.add_field(name="Info", value=position_info, inline=False)
        
        # Thumbnail
        if song.thumbnail:
            embed.set_thumbnail(url=song.thumbnail)
        
        embed.timestamp = datetime.utcnow()
        await ctx.send(embed=embed, ephemeral=True)
    
    # Queue Management Commands
    
    @commands.hybrid_command(name='remove', description='Remove a song from the queue')
    async def remove(self, ctx, position: int):
        """Remove a song from the queue."""
        if not self.check_permissions(ctx):
            await ctx.send(ERROR_MESSAGES['user_not_in_bot_channel'], ephemeral=True)
            return
        
        player = self.get_player(ctx.guild.id)
        
        if position < 1 or position > len(player.queue):
            await ctx.send(f"❌ Invalid position! Queue has {len(player.queue)} songs.", ephemeral=True)
            return
        
        song = player.remove_from_queue(position - 1)
        
        if song:
            embed = discord.Embed(
                title="🗑️ Removed from Queue",
                description=f"**{song.get_display_name()}**",
                color=EMBED_COLORS['error']
            )
            embed.add_field(name="Position", value=f"#{position}", inline=True)
            embed.add_field(name="Duration", value=self._format_duration(song.duration), inline=True)
            await ctx.send(embed=embed, ephemeral=True)
    
    @commands.hybrid_command(name='move', description='Move a song in the queue')
    async def move(self, ctx, from_pos: int, to_pos: int):
        """Move a song in the queue."""
        if not self.check_permissions(ctx):
            await ctx.send(ERROR_MESSAGES['user_not_in_bot_channel'], ephemeral=True)
            return
        
        player = self.get_player(ctx.guild.id)
        
        if player.move_song(from_pos - 1, to_pos - 1):
            embed = discord.Embed(
                title="↪️ Song Moved",
                description=f"Moved from position {from_pos} to {to_pos}",
                color=EMBED_COLORS['success']
            )
            await ctx.send(embed=embed, ephemeral=True)
        else:
            await ctx.send("❌ Invalid positions!", ephemeral=True)
    
    @commands.hybrid_command(name='insert', description='Insert a song at specific position')
    async def insert(self, ctx, position: int, *, query: str):
        """Insert a song at specific position."""
        if not self.check_permissions(ctx):
            await ctx.send(ERROR_MESSAGES['user_not_in_bot_channel'], ephemeral=True)
            return
        
        player = self.get_player(ctx.guild.id)
        
        async with ctx.typing():
            try:
                # Get song info (similar to play command)
                if query.startswith(('http://', 'https://')):
                    song_info = await SearchManager.get_song_info(query)
                else:
                    search_results = await SearchManager.search_youtube(query)
                    if not search_results:
                        await ctx.send(ERROR_MESSAGES['search_failed'], ephemeral=True)
                        return
                    song_info = search_results[0]
                
                song = Song(
                    title=song_info['title'],
                    url=song_info['url'],
                    duration=song_info.get('duration', 0),
                    requester=ctx.author,
                    source=song_info.get('source', 'youtube'),
                    thumbnail=song_info.get('thumbnail'),
                    artist=song_info.get('artist')
                )
                
                if player.insert_song(position - 1, song):
                    embed = discord.Embed(
                        title="➕ Song Inserted",
                        description=f"**{song.get_display_name()}** inserted at position {position}",
                        color=EMBED_COLORS['success']
                    )
                    await ctx.send(embed=embed, ephemeral=True)
                else:
                    await ctx.send("❌ Invalid position!", ephemeral=True)
                    
            except Exception as e:
                logger.error(f"Error inserting song: {e}")
                await ctx.send(f"❌ An error occurred: {str(e)[:100]}", ephemeral=True)
    
    @commands.hybrid_command(name='shuffle', description='Shuffle the queue')
    async def shuffle(self, ctx):
        """Shuffle the queue."""
        if not self.check_permissions(ctx):
            await ctx.send(ERROR_MESSAGES['user_not_in_bot_channel'], ephemeral=True)
            return
        
        player = self.get_player(ctx.guild.id)
        
        if not player.queue:
            await ctx.send(ERROR_MESSAGES['empty_queue'], ephemeral=True)
            return
        
        player.shuffle_queue()
        
        embed = discord.Embed(
            title="🔀 Queue Shuffled",
            description=f"Shuffled {len(player.queue)} songs",
            color=EMBED_COLORS['success']
        )
        await ctx.send(embed=embed, ephemeral=True)
    
    @commands.hybrid_command(name='clear', description='Clear the entire queue')
    async def clear_queue(self, ctx):
        """Clear the entire queue."""
        if not self.check_permissions(ctx):
            await ctx.send(ERROR_MESSAGES['user_not_in_bot_channel'], ephemeral=True)
            return
        
        player = self.get_player(ctx.guild.id)
        
        if not player.queue:
            await ctx.send(ERROR_MESSAGES['empty_queue'], ephemeral=True)
            return
        
        queue_size = len(player.queue)
        player.clear_queue()
        
        embed = discord.Embed(
            title="🧹 Queue Cleared",
            description=f"Removed {queue_size} songs from queue",
            color=EMBED_COLORS['warning']
        )
        await ctx.send(embed=embed, ephemeral=True)
    
    @commands.hybrid_command(name='sort', description='Sort queue by criteria')
    async def sort_queue(self, ctx, sort_by: str):
        """Sort queue by various criteria."""
        if not self.check_permissions(ctx):
            await ctx.send(ERROR_MESSAGES['user_not_in_bot_channel'], ephemeral=True)
            return
        
        player = self.get_player(ctx.guild.id)
        
        if not player.queue:
            await ctx.send(ERROR_MESSAGES['empty_queue'], ephemeral=True)
            return
        
        valid_sort_options = ['artist', 'duration', 'date_added', 'title']
        if sort_by not in valid_sort_options:
            await ctx.send(f"❌ Invalid sort option! Use: {', '.join(valid_sort_options)}", ephemeral=True)
            return
        
        player.sort_queue(sort_by)
        
        embed = discord.Embed(
            title="📋 Queue Sorted",
            description=f"Queue sorted by {sort_by.replace('_', ' ').title()}",
            color=EMBED_COLORS['success']
        )
        await ctx.send(embed=embed, ephemeral=True)
    
    # Audio Control Commands
    
    @commands.hybrid_command(name='volume', description='Set the volume (0-200%)')
    async def volume(self, ctx, level: int):
        """Set the volume level."""
        if level < 0 or level > 200:
            await ctx.send("❌ Volume must be between 0 and 200!", ephemeral=True)
            return
        
        player = self.get_player(ctx.guild.id)
        player.volume = level
        
        embed = discord.Embed(
            title="🔊 Volume Changed",
            description=f"Volume set to {level}%",
            color=EMBED_COLORS['success']
        )
        embed.add_field(name="Volume Bar", value=self._create_volume_bar(level), inline=False)
        await ctx.send(embed=embed, ephemeral=True)
    
    @commands.hybrid_command(name='loop', description='Set loop mode (none/one/all)')
    async def loop(self, ctx, mode: str = None):
        """Set the loop mode."""
        if not self.check_permissions(ctx):
            await ctx.send(ERROR_MESSAGES['user_not_in_bot_channel'], ephemeral=True)
            return
        
        player = self.get_player(ctx.guild.id)
        
        if mode is None:
            # Cycle through modes
            mode_order = ['none', 'one', 'all']
            current_index = mode_order.index(player.loop_mode)
            mode = mode_order[(current_index + 1) % len(mode_order)]
        elif mode not in ['none', 'one', 'all']:
            await ctx.send("❌ Invalid mode! Use: none, one, or all", ephemeral=True)
            return
        
        player.loop_mode = mode
        
        mode_display = {
            'none': '➡️ Loop Disabled',
            'one': '🔂 Loop Current Song',
            'all': '🔁 Loop Entire Queue'
        }
        
        embed = discord.Embed(
            title=mode_display[mode],
            color=EMBED_COLORS['success']
        )
        await ctx.send(embed=embed, ephemeral=True)
    
    @commands.hybrid_command(name='seek', description='Seek to specific position (mm:ss)')
    async def seek(self, ctx, position: str):
        """Seek to a specific position in the song."""
        if not self.check_permissions(ctx):
            await ctx.send(ERROR_MESSAGES['user_not_in_bot_channel'], ephemeral=True)
            return
        
        player = self.get_player(ctx.guild.id)
        
        if not player.current_song:
            await ctx.send(ERROR_MESSAGES['no_song_playing'], ephemeral=True)
            return
        
        # Parse position (supports mm:ss or seconds)
        try:
            if ':' in position:
                parts = position.split(':')
                if len(parts) == 2:
                    minutes, seconds = map(int, parts)
                    seek_position = minutes * 60 + seconds
                else:
                    raise ValueError("Invalid time format")
            else:
                seek_position = int(position)
        except ValueError:
            await ctx.send("❌ Invalid time format! Use mm:ss or seconds", ephemeral=True)
            return
        
        if seek_position > player.current_song.duration:
            await ctx.send(f"❌ Position exceeds song duration ({self._format_duration(player.current_song.duration)})", ephemeral=True)
            return
        
        player.current_position = seek_position
        
        embed = discord.Embed(
            title="⏩ Seeked",
            description=f"Jumped to {self._format_duration(seek_position)}",
            color=EMBED_COLORS['success']
        )
        await ctx.send(embed=embed, ephemeral=True)
    
    @commands.hybrid_command(name='speed', description='Set playback speed (0.5x to 2.0x)')
    async def speed(self, ctx, speed: float):
        """Set playback speed."""
        if speed < 0.5 or speed > 2.0:
            await ctx.send("❌ Speed must be between 0.5 and 2.0!", ephemeral=True)
            return
        
        player = self.get_player(ctx.guild.id)
        player.speed = speed
        
        # Disable special effects if speed is changed
        player.nightcore_enabled = False
        player.slowed_enabled = False
        
        embed = discord.Embed(
            title="⚡ Playback Speed",
            description=f"Speed set to {speed}x",
            color=EMBED_COLORS['success']
        )
        await ctx.send(embed=embed, ephemeral=True)
    
    @commands.hybrid_command(name='equalizer', description='Set audio equalizer preset')
    async def equalizer(self, ctx, preset: str = None):
        """Set equalizer preset."""
        if preset is None:
            presets = ", ".join(f"`{p}`" for p in EQUALIZER_PRESETS.keys())
            await ctx.send(f"Available presets: {presets}", ephemeral=True)
            return
        
        if preset not in EQUALIZER_PRESETS:
            await ctx.send(f"❌ Unknown preset! Available: {', '.join(EQUALIZER_PRESETS.keys())}", ephemeral=True)
            return
        
        player = self.get_player(ctx.guild.id)
        player.equalizer = list(EQUALIZER_PRESETS[preset]['values'])
        
        embed = discord.Embed(
            title="🎚️ Equalizer Changed",
            description=f"Preset set to **{preset}** - {EQUALIZER_PRESETS[preset]['description']}",
            color=EMBED_COLORS['success']
        )
        await ctx.send(embed=embed, ephemeral=True)
    
    @commands.hybrid_command(name='nightcore', description='Toggle nightcore effect')
    async def nightcore(self, ctx):
        """Toggle nightcore effect."""
        if not self.check_permissions(ctx):
            await ctx.send(ERROR_MESSAGES['user_not_in_bot_channel'], ephemeral=True)
            return
        
        player = self.get_player(ctx.guild.id)
        player.nightcore_enabled = not player.nightcore_enabled
        player.speed = 1.25 if player.nightcore_enabled else 1.0
        
        # Disable slowed if nightcore is enabled
        if player.nightcore_enabled:
            player.slowed_enabled = False
        
        status = "✅ Enabled" if player.nightcore_enabled else "❌ Disabled"
        embed = discord.Embed(
            title="🌙 Nightcore Effect",
            description=f"Nightcore {status} (Speed: {player.speed}x)",
            color=EMBED_COLORS['success']
        )
        await ctx.send(embed=embed, ephemeral=True)
    
    @commands.hybrid_command(name='slowed', description='Toggle slowed effect')
    async def slowed(self, ctx):
        """Toggle slowed effect."""
        if not self.check_permissions(ctx):
            await ctx.send(ERROR_MESSAGES['user_not_in_bot_channel'], ephemeral=True)
            return
        
        player = self.get_player(ctx.guild.id)
        player.slowed_enabled = not player.slowed_enabled
        player.speed = 0.8 if player.slowed_enabled else 1.0
        
        # Disable nightcore if slowed is enabled
        if player.slowed_enabled:
            player.nightcore_enabled = False
        
        status = "✅ Enabled" if player.slowed_enabled else "❌ Disabled"
        embed = discord.Embed(
            title="🐌 Slowed Effect",
            description=f"Slowed {status} (Speed: {player.speed}x)",
            color=EMBED_COLORS['success']
        )
        await ctx.send(embed=embed, ephemeral=True)
    
    # User Library Commands
    
    @commands.hybrid_command(name='favorite', description='Add current song to favorites')
    async def favorite(self, ctx):
        """Add current song to favorites."""
        player = self.get_player(ctx.guild.id)
        
        if not player.current_song:
            await ctx.send(ERROR_MESSAGES['no_song_playing'], ephemeral=True)
            return
        
        song = player.current_song
        
        if len(player.favorite_songs) >= MAX_FAVORITES:
            await ctx.send(f"❌ Maximum favorites reached ({MAX_FAVORITES})!", ephemeral=True)
            return
        
        if song in player.favorite_songs:
            player.favorite_songs.remove(song)
            embed = discord.Embed(
                title="💔 Removed from Favorites",
                description=f"**{song.get_display_name()}** removed from favorites",
                color=EMBED_COLORS['warning']
            )
        else:
            player.favorite_songs.append(song)
            embed = discord.Embed(
                title="❤️ Added to Favorites",
                description=f"**{song.get_display_name()}** added to favorites",
                color=EMBED_COLORS['success']
            )
        
        embed.add_field(name="Total Favorites", value=f"{len(player.favorite_songs)}/{MAX_FAVORITES}", inline=True)
        await ctx.send(embed=embed, ephemeral=True)
    
    @commands.hybrid_command(name='favorites', description='View your favorite songs')
    async def favorites(self, ctx, page: int = 1):
        """View user's favorite songs."""
        player = self.get_player(ctx.guild.id)
        
        if not player.favorite_songs:
            await ctx.send("❌ No favorite songs found!", ephemeral=True)
            return
        
        page_size = 10
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        favorites = player.favorite_songs
        total_pages = (len(favorites) + page_size - 1) // page_size
        
        if page < 1 or page > total_pages:
            await ctx.send(f"❌ Invalid page. Total pages: {total_pages}", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="❤️ Your Favorites",
            color=EMBED_COLORS['success']
        )
        
        favorites_str = ""
        for i in range(start_idx, min(end_idx, len(favorites))):
            song = favorites[i]
            favorites_str += f"{i+1}. **{song.get_display_name()}** [{self._format_duration(song.duration)}]\n"
        
        embed.add_field(
            name=f"Favorite Songs (Page {page}/{total_pages})",
            value=favorites_str,
            inline=False
        )
        
        embed.add_field(
            name="Total",
            value=f"{len(favorites)} songs",
            inline=True
        )
        
        await ctx.send(embed=embed, ephemeral=True)
    
    @commands.hybrid_command(name='playlist', description='Manage playlists')
    async def playlist(self, ctx, action: str, *, name: str = None):
        """Manage playlists."""
        player = self.get_player(ctx.guild.id)
        user_id = ctx.author.id
        
        if action == 'create':
            if not name:
                await ctx.send("❌ Please provide a playlist name!", ephemeral=True)
                return
            
            if len(player.playlists) >= MAX_PLAYLISTS:
                await ctx.send(f"❌ Maximum playlists reached ({MAX_PLAYLISTS})!", ephemeral=True)
                return
            
            if player.save_queue_as_playlist(name):
                embed = discord.Embed(
                    title="📋 Playlist Created",
                    description=f"Created playlist **{name}** with {len(player.queue)} songs",
                    color=EMBED_COLORS['success']
                )
                await ctx.send(embed=embed, ephemeral=True)
            else:
                await ctx.send(f"❌ Playlist **{name}** already exists!", ephemeral=True)
        
        elif action == 'load':
            if not name:
                await ctx.send("❌ Please provide a playlist name!", ephemeral=True)
                return
            
            if player.load_playlist(name):
                embed = discord.Embed(
                    title="📋 Playlist Loaded",
                    description=f"Loaded **{name}** ({len(player.playlists[name])} songs)",
                    color=EMBED_COLORS['success']
                )
                await ctx.send(embed=embed, ephemeral=True)
                
                # Start playing if not already playing
                if not player.is_playing:
                    await self._play_next(ctx)
            else:
                await ctx.send(f"❌ Playlist **{name}** not found!", ephemeral=True)
        
        elif action == 'list':
            if not player.playlists:
                await ctx.send("❌ No playlists found!", ephemeral=True)
                return
            
            playlists_str = ""
            total_songs = 0
            for playlist_name, songs in player.playlists.items():
                playlists_str += f"• **{playlist_name}** ({len(songs)} songs)\n"
                total_songs += len(songs)
            
            embed = discord.Embed(
                title="📋 Your Playlists",
                description=playlists_str,
                color=EMBED_COLORS['info']
            )
            embed.add_field(name="Total Playlists", value=str(len(player.playlists)), inline=True)
            embed.add_field(name="Total Songs", value=str(total_songs), inline=True)
            await ctx.send(embed=embed, ephemeral=True)
        
        elif action == 'delete':
            if not name:
                await ctx.send("❌ Please provide a playlist name!", ephemeral=True)
                return
            
            if name in player.playlists:
                playlist_size = len(player.playlists[name])
                del player.playlists[name]
                embed = discord.Embed(
                    title="🗑️ Playlist Deleted",
                    description=f"Deleted **{name}** ({playlist_size} songs)",
                    color=EMBED_COLORS['error']
                )
                await ctx.send(embed=embed, ephemeral=True)
            else:
                await ctx.send(f"❌ Playlist **{name}** not found!", ephemeral=True)
        
        elif action == 'info':
            if not name:
                await ctx.send("❌ Please provide a playlist name!", ephemeral=True)
                return
            
            if name in player.playlists:
                songs = player.playlists[name]
                total_duration = sum(song.duration for song in songs)
                
                embed = discord.Embed(
                    title=f"📋 Playlist: {name}",
                    color=EMBED_COLORS['info']
                )
                embed.add_field(name="Songs", value=str(len(songs)), inline=True)
                embed.add_field(name="Duration", value=self._format_duration(total_duration), inline=True)
                
                # Show first few songs
                songs_list = "\n".join(f"{i+1}. {song.get_display_name()}" for i, song in enumerate(songs[:5]))
                if len(songs) > 5:
                    songs_list += f"\n... and {len(songs) - 5} more"
                
                embed.add_field(name="Songs", value=songs_list or "Empty", inline=False)
                await ctx.send(embed=embed, ephemeral=True)
            else:
                await ctx.send(f"❌ Playlist **{name}** not found!", ephemeral=True)
        
        else:
            await ctx.send("❌ Invalid action! Use: create, load, list, delete, info", ephemeral=True)
    
    # Statistics and Analytics Commands
    
    @commands.hybrid_command(name='history', description='Show your listening history')
    async def history(self, ctx, page: int = 1):
        """Show listening history."""
        player = self.get_player(ctx.guild.id)
        
        history = player.listening_history.get(ctx.author.id, [])
        
        if not history:
            await ctx.send("❌ No listening history found!", ephemeral=True)
            return
        
        page_size = 10
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        total_pages = (len(history) + page_size - 1) // page_size
        
        if page < 1 or page > total_pages:
            await ctx.send(f"❌ Invalid page. Total pages: {total_pages}", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🎵 Your Listening History",
            color=EMBED_COLORS['info']
        )
        
        history_str = ""
        for i in range(start_idx, min(end_idx, len(history))):
            entry = history[i]
            song_data = entry['song']
            timestamp = entry['timestamp']
            
            # Format timestamp
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                time_str = dt.strftime('%m/%d %H:%M')
            except:
                time_str = timestamp[:10]
            
            title = song_data.get('title', 'Unknown')
            artist = song_data.get('artist', 'Unknown')
            history_str += f"{i+1}. **{title}** by {artist} - {time_str}\n"
        
        embed.add_field(
            name=f"Recent Activity (Page {page}/{total_pages})",
            value=history_str or "No history",
            inline=False
        )
        
        # Add summary stats
        stats = player.user_stats.get(ctx.author.id, {})
        embed.add_field(
            name="Your Stats",
            value=f"Total Songs: {stats.get('total_songs_played', 0)}\n"
                  f"Listening Time: {self._format_duration(stats.get('total_listening_time', 0))}\n"
                  f"Streak: {stats.get('listening_streak', 0)} days",
            inline=True
        )
        
        await ctx.send(embed=embed, ephemeral=True)
    
    @commands.hybrid_command(name='stats', description='Show music statistics for the server')
    async def stats(self, ctx):
        """Show server music statistics."""
        player = self.get_player(ctx.guild.id)
        
        # Get insights
        insights = player.get_server_insights()
        top_songs = player.get_top_songs(5)
        top_artists = player.get_top_artists(5)
        
        embed = discord.Embed(
            title="📊 Server Music Statistics",
            color=EMBED_COLORS['stats']
        )
        
        # Basic stats
        embed.add_field(
            name="📈 Overview",
            value=f"Total Plays: {insights['total_plays']}\n"
                  f"Unique Listeners: {insights['unique_listeners']}\n"
                  f"Songs Played: {insights['total_songs_played']}\n"
                  f"Artists Played: {insights['total_artists_played']}\n"
                  f"Session Time: {insights['session_duration']}",
            inline=True
        )
        
        # Peak information
        if insights.get('peak_hour') is not None:
            peak_time = f"{insights['peak_hour']}:00"
        else:
            peak_time = "No data"
        
        embed.add_field(
            name="⏰ Activity",
            value=f"Peak Hour: {peak_time}\n"
                  f"Avg Plays/User: {insights.get('avg_plays_per_listener', 0)}\n"
                  f"Radio Mode: {'On' if player.radio_mode else 'Off'}",
            inline=True
        )
        
        # Top songs
        if top_songs:
            songs_str = "\n".join(f"{i+1}. **{song}** ({count} plays)" 
                                for i, (song, count) in enumerate(top_songs))
            embed.add_field(name="🏆 Top Songs", value=songs_str, inline=False)
        
        # Top artists
        if top_artists:
            artists_str = "\n".join(f"{i+1}. **{artist}** ({count} plays)" 
                                  for i, (artist, count) in enumerate(top_artists))
            embed.add_field(name="🎤 Top Artists", value=artists_str, inline=False)
        
        embed.timestamp = datetime.utcnow()
        await ctx.send(embed=embed, ephemeral=True)
    
    @commands.hybrid_command(name='my-stats', description='Show your personal music statistics')
    async def my_stats(self, ctx):
        """Show personal music statistics."""
        player = self.get_player(ctx.guild.id)
        user_id = ctx.author.id
        
        if user_id not in player.user_stats:
            await ctx.send("❌ No listening statistics found for you!", ephemeral=True)
            return
        
        stats = player.user_stats[user_id]
        recommendations = player.get_user_recommendations(user_id, 3)
        
        embed = discord.Embed(
            title="📈 Your Music Statistics",
            color=EMBED_COLORS['stats']
        )
        
        # Basic stats
        embed.add_field(
            name="📊 Activity",
            value=f"Total Songs: {stats['total_songs_played']}\n"
                  f"Listening Time: {self._format_duration(stats['total_listening_time'])}\n"
                  f"Listening Streak: {stats['listening_streak']} days\n"
                  f"Favorite Songs: {len(player.favorite_songs)}",
            inline=True
        )
        
        # Top artists and genres
        if stats['top_artists']:
            top_artist = max(stats['top_artists'].items(), key=lambda x: x[1])
            embed.add_field(
                name="🎤 Favorite Artist",
                value=f"**{top_artist[0]}** ({top_artist[1]} plays)",
                inline=True
            )
        
        if stats['top_genres']:
            top_genre = max(stats['top_genres'].items(), key=lambda x: x[1])
            embed.add_field(
                name="🎵 Favorite Genre",
                value=f"**{top_genre[0]}** ({top_genre[1]} plays)",
                inline=True
            )
        
        # Top songs
        if stats['top_songs']:
            top_songs = sorted(stats['top_songs'].items(), key=lambda x: x[1], reverse=True)[:3]
            songs_str = "\n".join(f"{i+1}. **{song}** ({count} plays)" 
                                for i, (song, count) in enumerate(top_songs))
            embed.add_field(name="🏆 Top Songs", value=songs_str, inline=False)
        
        # Recommendations
        if recommendations:
            rec_str = "\n".join(f"• {rec['value']} ({rec['type']})" for rec in recommendations)
            embed.add_field(name="💡 Recommendations", value=rec_str, inline=False)
        
        embed.timestamp = datetime.utcnow()
        await ctx.send(embed=embed, ephemeral=True)
    
    # Discovery and Recommendations Commands
    
    @commands.hybrid_command(name='recommendations', description='Get personalized music recommendations')
    async def recommendations(self, ctx, limit: int = 5):
        """Get personalized recommendations."""
        player = self.get_player(ctx.guild.id)
        user_id = ctx.author.id
        
        recommendations = player.get_user_recommendations(user_id, limit)
        
        if not recommendations:
            await ctx.send("❌ Not enough listening data for recommendations. Start playing some music!", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="💡 Your Music Recommendations",
            description="Based on your listening history",
            color=EMBED_COLORS['recommendations']
        )
        
        # Group by type
        genre_recs = [r for r in recommendations if r['type'] == 'genre']
        artist_recs = [r for r in recommendations if r['type'] == 'artist']
        
        if genre_recs:
            genre_str = "\n".join(f"🎵 **{rec['value']}** music" for rec in genre_recs)
            embed.add_field(name="By Genre", value=genre_str, inline=True)
        
        if artist_recs:
            artist_str = "\n".join(f"🎤 **{rec['value']}**" for rec in artist_recs)
            embed.add_field(name="By Artist", value=artist_str, inline=True)
        
        embed.add_field(
            name="💡 Tip",
            value="Use these recommendations with the `!play` command to discover new music!",
            inline=False
        )
        
        await ctx.send(embed=embed, ephemeral=True)
    
    @commands.hybrid_command(name='similar', description='Get songs similar to current song')
    async def similar(self, ctx):
        """Get songs similar to current song."""
        player = self.get_player(ctx.guild.id)
        
        if not player.current_song:
            await ctx.send(ERROR_MESSAGES['no_song_playing'], ephemeral=True)
            return
        
        song = player.current_song
        embed = discord.Embed(
            title="🔗 Similar Songs",
            description=f"Based on **{song.get_display_name()}**",
            color=EMBED_COLORS['recommendations']
        )
        
        # Generate similar song suggestions
        suggestions = []
        
        if song.artist:
            suggestions.append(f"🎤 More by {song.artist}")
        
        if song.genre:
            suggestions.append(f"🎵 More {song.genre} music")
        
        if song.year:
            decade = (song.year // 10) * 10
            suggestions.append(f"📅 {decade}s hits")
        
        suggestions.append("🎵 Hot right now")
        suggestions.append("💎 Indie discoveries")
        
        suggestions_text = "\n".join(f"• {suggestion}" for suggestion in suggestions[:5])
        embed.add_field(name="Try these searches:", value=suggestions_text, inline=False)
        
        await ctx.send(embed=embed, ephemeral=True)
    
    @commands.hybrid_command(name='radio', description='Enable/disable radio mode')
    async def radio(self, ctx, mode: str = 'artist'):
        """Toggle radio mode."""
        player = self.get_player(ctx.guild.id)
        
        if not player.current_song:
            await ctx.send("❌ Need a current song to start radio mode!", ephemeral=True)
            return
        
        if not self.check_permissions(ctx):
            await ctx.send(ERROR_MESSAGES['user_not_in_bot_channel'], ephemeral=True)
            return
        
        if player.radio_mode:
            player.disable_radio_mode()
            embed = discord.Embed(
                title="📻 Radio Disabled",
                description="Radio mode has been turned off",
                color=EMBED_COLORS['warning']
            )
        else:
            valid_modes = ['artist', 'genre', 'decade']
            if mode not in valid_modes:
                await ctx.send(f"❌ Invalid mode! Use: {', '.join(valid_modes)}", ephemeral=True)
                return
            
            player.enable_radio_mode(player.current_song, mode)
            embed = discord.Embed(
                title="📻 Radio Enabled",
                description=f"Radio mode: **{mode}** based on {player.current_song.get_display_name()}",
                color=EMBED_COLORS['success']
            )
        
        await ctx.send(embed=embed, ephemeral=True)
    
    @commands.hybrid_command(name='mood', description='Get mood-based playlist')
    async def mood(self, ctx, mood: str):
        """Get mood-based playlist."""
        if mood not in MOOD_PLAYLISTS:
            moods = ", ".join(f"`{m}`" for m in MOOD_PLAYLISTS.keys())
            await ctx.send(f"Available moods: {moods}", ephemeral=True)
            return
        
        mood_info = MOOD_PLAYLISTS[mood]
        
        embed = discord.Embed(
            title=f"{mood_info['emoji']} {mood.capitalize()} Vibes",
            description=mood_info['description'],
            color=EMBED_COLORS['info']
        )
        
        # Show search suggestions
        search_suggestions = "\n".join(f"• {keyword}" for keyword in mood_info['keywords'][:5])
        embed.add_field(name="Try searching:", value=search_suggestions, inline=False)
        
        # Quick search buttons
        view = discord.ui.View()
        
        class MoodButton(discord.ui.Button):
            def __init__(self, label, query):
                super().__init__(style=discord.ButtonStyle.primary, label=label)
                self.query = query
            
            async def callback(self, interaction: discord.Interaction):
                await interaction.response.send_message(f"Searching for: {self.query}", ephemeral=True)
                # Would trigger play command here
        
        if mood_info['keywords']:
            for keyword in mood_info['keywords'][:3]:
                view.add_item(MoodButton(f"Play {keyword}", keyword))
        
        await ctx.send(embed=embed, view=view, ephemeral=True)
    
    @commands.hybrid_command(name='decade', description='Get decade-based playlist')
    async def decade(self, ctx, decade: str):
        """Get decade-based playlist."""
        if decade not in DECADE_PLAYLISTS:
            decades = ", ".join(f"`{d}`" for d in DECADE_PLAYLISTS.keys())
            await ctx.send(f"Available decades: {decades}", ephemeral=True)
            return
        
        decade_info = DECADE_PLAYLISTS[decade]
        
        embed = discord.Embed(
            title=f"{decade_info['emoji']} {decade} Music",
            description=decade_info['description'],
            color=EMBED_COLORS['info']
        )
        
        embed.add_field(
            name="Quick Search",
            value=f"Try: `{decade_info['search_query']}`",
            inline=False
        )
        
        view = discord.ui.View()
        
        class DecadeButton(discord.ui.Button):
            def __init__(self, label, query):
                super().__init__(style=discord.ButtonStyle.primary, label=label)
                self.query = query
            
            async def callback(self, interaction: discord.Interaction):
                await interaction.response.send_message(f"Searching {decade}: {self.query}", ephemeral=True)
                # Would trigger play command here
        
        view.add_item(DecadeButton("Play Hits", decade_info['search_query']))
        view.add_item(DecadeButton("Play Mix", f"{decade} music mix"))
        
        await ctx.send(embed=embed, view=view, ephemeral=True)
    
    # Search and Discovery Commands
    
    @commands.hybrid_command(name='lyrics', description='Show lyrics for current song')
    async def lyrics(self, ctx):
        """Show lyrics for current song."""
        player = self.get_player(ctx.guild.id)
        
        if not player.current_song:
            await ctx.send(ERROR_MESSAGES['no_song_playing'], ephemeral=True)
            return
        
        song = player.current_song
        
        async with ctx.typing():
            lyrics = await LyricsManager.get_lyrics(song.title, song.artist)
            
            if not lyrics:
                await ctx.send("❌ Lyrics not found for this song.", ephemeral=True)
                return
            
            # Split lyrics into chunks if too long
            max_length = 1024
            if len(lyrics) > max_length:
                lyrics = lyrics[:max_length] + "\n... (truncated)"
            
            embed = discord.Embed(
                title=f"🎤 {song.get_display_name()}",
                description=f"```\n{lyrics}\n```",
                color=EMBED_COLORS['lyrics']
            )
            
            embed.add_field(name="Source", value="Lyrics.ovh / Genius", inline=True)
            if song.album:
                embed.add_field(name="Album", value=song.album, inline=True)
            
            await ctx.send(embed=embed, ephemeral=True)
    
    @commands.hybrid_command(name='search', description='Advanced search with filters')
    async def search(self, ctx, *, query: str):
        """Advanced search with various filters."""
        async with ctx.typing():
            # Search multiple sources
            results = []
            
            # YouTube search
            yt_results = await SearchManager.search_youtube(query, max_results=3)
            for result in yt_results:
                result['platform'] = 'YouTube'
                results.append(result)
            
            # Spotify search (if credentials available)
            if os.getenv('SPOTIFY_CLIENT_ID') and os.getenv('SPOTIFY_CLIENT_SECRET'):
                sp_results = await SearchManager.search_spotify(query, max_results=3)
                for result in sp_results:
                    result['platform'] = 'Spotify'
                    results.append(result)
            
            if not results:
                await ctx.send(ERROR_MESSAGES['no_results'], ephemeral=True)
                return
            
            # Create embed with results
            embed = discord.Embed(
                title=f"🔍 Search Results for: {query}",
                color=EMBED_COLORS['info']
            )
            
            for i, result in enumerate(results[:5], 1):
                platform = result.get('platform', 'Unknown')
                title = result.get('title', 'Unknown')
                artist = result.get('artist', 'Unknown')
                duration = result.get('duration', 0)
                
                embed.add_field(
                    name=f"{i}. {platform}",
                    value=f"**{title}**\nby {artist}\nDuration: {self._format_duration(duration)}",
                    inline=False
                )
            
            # Add search tips
            embed.add_field(
                name="💡 Tips",
                value="• Click on a result number to play that song\n"
                      "• Use filters in future searches\n"
                      "• URLs are automatically detected",
                inline=False
            )
            
            await ctx.send(embed=embed, ephemeral=True)
            
            # Store results for quick access
            self.search_cache[f"results_{ctx.author.id}"] = results
    
    @commands.hybrid_command(name='trending', description='Show trending music')
    async def trending(self, ctx):
        """Show trending music."""
        trending_keywords = [
            "trending now",
            "viral hits",
            "new music",
            "hot right now",
            "chart toppers"
        ]
        
        embed = discord.Embed(
            title="🔥 Trending Music",
            description="What's hot right now",
            color=EMBED_COLORS['info']
        )
        
        trending_str = "\n".join(f"• {keyword}" for keyword in trending_keywords)
        embed.add_field(name="Search these trends:", value=trending_str, inline=False)
        
        view = discord.ui.View()
        
        class TrendingButton(discord.ui.Button):
            def __init__(self, label, query):
                super().__init__(style=discord.ButtonStyle.primary, label=label)
                self.query = query
            
            async def callback(self, interaction: discord.Interaction):
                await interaction.response.send_message(f"Searching trending: {self.query}", ephemeral=True)
        
        for keyword in trending_keywords[:3]:
            view.add_item(TrendingButton(keyword.title(), keyword))
        
        await ctx.send(embed=embed, view=view, ephemeral=True)
    
    # Utility Methods
    
    async def _play_next(self, ctx):
        """Play the next song in queue."""
        player = self.get_player(ctx.guild.id)
        
        # Connect to voice channel if not already connected
        if not ctx.guild.voice_client:
            if ctx.author.voice:
                try:
                    voice_client = await ctx.author.voice.channel.connect()
                    self.voice_clients[ctx.guild.id] = voice_client
                except Exception as e:
                    logger.error(f"Failed to connect to voice channel: {e}")
                    await ctx.send("❌ Failed to connect to voice channel!", ephemeral=True)
                    return
        
        song = player.get_next_song()
        if song:
            player.current_song = song
            player.is_playing = True
            player.is_paused = False
            player.current_position = 0
            player.start_time = datetime.now()
            
            # Record play for statistics
            player.record_play(song, ctx.author.id)
            
            # Reset voting
            player.voting_skip = {'yes': set(), 'no': set()}
            
            # Try to play the audio (simplified - would need actual audio processing)
            try:
                # This is where you would use FFmpeg or similar to play audio
                # For now, just show now playing embed
                embed = discord.Embed(
                    title="🎵 Now Playing",
                    description=f"**{song.get_display_name()}**",
                    color=EMBED_COLORS['now_playing']
                )
                embed.add_field(name="Duration", value=self._format_duration(song.duration), inline=True)
                embed.add_field(name="Source", value=song.source.capitalize(), inline=True)
                
                if song.thumbnail:
                    embed.set_thumbnail(url=song.thumbnail)
                
                await ctx.send(embed=embed)
                
            except Exception as e:
                logger.error(f"Failed to play audio: {e}")
                player.is_playing = False
                player.current_song = None
                await ctx.send("❌ Failed to play audio!", ephemeral=True)
        else:
            # No more songs
            player.is_playing = False
            player.current_song = None
            
            # Disconnect from voice channel after period of inactivity
            if ctx.guild.voice_client:
                await ctx.guild.voice_client.disconnect()
                del self.voice_clients[ctx.guild.id]
    
    def _format_duration(self, seconds: int) -> str:
        """Format duration in MM:SS or HH:MM:SS format."""
        if seconds < 0:
            seconds = 0
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes}:{seconds:02d}"
    
    def _create_progress_bar(self, current: int, total: int, length: int = 20) -> str:
        """Create a progress bar."""
        if total == 0:
            return "▬" * length
        
        filled = int(length * current / total)
        bar = "🔵" + "▬" * (filled - 1) + "🟡" + "▬" * (length - filled)
        return bar
    
    def _create_volume_bar(self, level: int) -> str:
        """Create a volume bar."""
        filled = int(10 * level / 200)
        return "🔊 " + "█" * filled + "░" * (10 - filled) + f" {level}%"
    
    # Error handling for music commands
    @play.error
    @pause.error
    @resume.error
    @skip.error
    @stop.error
    async def music_command_error(self, ctx, error):
        """Handle errors for music commands."""
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"Command on cooldown. Try again in {error.retry_after:.1f}s", ephemeral=True)
        elif isinstance(error, commands.CheckFailure):
            await ctx.send("You need to be in the same voice channel as the bot to use music commands!", ephemeral=True)
        else:
            logger.error(f"Music command error: {error}")
            await ctx.send("An error occurred while processing the music command.", ephemeral=True)


async def setup(bot):
    """Setup function for the cog."""
    await bot.add_cog(MusicCog(bot))