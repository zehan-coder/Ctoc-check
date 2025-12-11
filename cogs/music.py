"""
Advanced Music Cog for Discord Bot
Provides comprehensive music playback, streaming, and management capabilities.
"""

import asyncio
import json
import logging
import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict, deque

import discord
import aiohttp
from discord.ext import commands, tasks
import yt_dlp
from youtube_search import YoutubeSearch

logger = logging.getLogger(__name__)

# Audio processing presets
EQUALIZER_PRESETS = {
    'flat': [0, 0, 0, 0, 0],
    'bass_boost': [5, 3, 1, 0, -2],
    'pop': [2, 1, -1, 2, 3],
    'metal': [4, 3, 1, 2, 4],
    'jazz': [3, 2, 0, 1, 3],
    'classic': [2, 1, 0, 1, 2],
}

MOOD_PLAYLISTS = {
    'chill': ['relaxing', 'ambient', 'lo-fi', 'chillhop'],
    'energetic': ['electronic', 'dance', 'upbeat pop', 'workout'],
    'sad': ['sad', 'emotional', 'ballad', 'melancholic'],
    'happy': ['happy', 'upbeat', 'feel-good', 'indie pop'],
    'focus': ['study', 'lo-fi hip hop', 'instrumental', 'ambient'],
}

DECADE_PLAYLISTS = {
    '80s': 'hits of the 80s',
    '90s': 'hits of the 90s',
    '2000s': 'hits of the 2000s',
    '2010s': 'hits of the 2010s',
    '2020s': 'hits of the 2020s',
}


class Song:
    """Represents a song in the queue."""
    
    def __init__(self, title: str, url: str, duration: int, requester: discord.User, 
                 source: str = 'youtube', thumbnail: str = None, artist: str = None,
                 album: str = None):
        self.title = title
        self.url = url
        self.duration = duration
        self.requester = requester
        self.source = source
        self.thumbnail = thumbnail
        self.artist = artist
        self.album = album
        self.added_at = datetime.now()
    
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
        }


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
        self.equalizer = list(EQUALIZER_PRESETS['flat'])
        self.bass_boost = False
        self.nightcore_enabled = False
        self.slowed_enabled = False
        self.reverse_enabled = False
        self.favorite_songs: List[Song] = []
        self.playlists: Dict[str, List[Song]] = {}
        self.blacklist_songs = set()
        self.blacklist_artists = set()
        self.voting_skip = {'yes': set(), 'no': set()}
        self.user_preferences: Dict[int, dict] = defaultdict(lambda: {
            'favorite_genres': [],
            'preferred_quality': '320',
            'allow_explicit': True,
        })
        self.listening_history: Dict[int, List[dict]] = defaultdict(list)
        self.user_stats: Dict[int, dict] = defaultdict(lambda: {
            'total_songs_played': 0,
            'total_listening_time': 0,
            'top_artists': defaultdict(int),
            'top_genres': defaultdict(int),
        })
    
    def add_to_queue(self, song: Song):
        """Add song to queue."""
        self.queue.append(song)
        self.listening_history[song.requester.id].append({
            'song': song.to_dict(),
            'timestamp': datetime.now().isoformat(),
        })
    
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
    
    def shuffle_queue(self):
        """Shuffle the queue."""
        import random
        queue_list = list(self.queue)
        random.shuffle(queue_list)
        self.queue = deque(queue_list)
    
    def clear_queue(self):
        """Clear the entire queue."""
        self.queue.clear()
    
    def get_next_song(self) -> Optional[Song]:
        """Get next song from queue."""
        if self.loop_mode == 'one' and self.current_song:
            return self.current_song
        
        if self.queue:
            return self.queue.popleft()
        return None
    
    def save_queue_as_playlist(self, playlist_name: str):
        """Save current queue as a playlist."""
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
    
    def get_top_songs(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Get top songs by play count."""
        song_counts = defaultdict(int)
        for user_history in self.listening_history.values():
            for entry in user_history:
                song_title = entry['song']['title']
                song_counts[song_title] += 1
        return sorted(song_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
    
    def get_top_artists(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Get top artists by play count."""
        artist_counts = defaultdict(int)
        for user_history in self.listening_history.values():
            for entry in user_history:
                artist = entry['song'].get('artist', 'Unknown')
                artist_counts[artist] += 1
        return sorted(artist_counts.items(), key=lambda x: x[1], reverse=True)[:limit]


class MusicCog(commands.Cog):
    """Advanced music playback cog."""
    
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
    
    async def cog_load(self):
        """Initialize the cog."""
        self.session = aiohttp.ClientSession()
    
    async def cog_unload(self):
        """Clean up the cog."""
        if self.session:
            await self.session.close()
    
    def get_player(self, guild_id: int) -> MusicPlayer:
        """Get or create player for guild."""
        if guild_id not in self.players:
            self.players[guild_id] = MusicPlayer(guild_id)
        return self.players[guild_id]
    
    async def get_song_info(self, query: str, source: str = 'youtube') -> Optional[Song]:
        """Get song info from various sources."""
        try:
            if source == 'youtube':
                with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                    info = ydl.extract_info(f"ytsearch:{query}", download=False)
                    if info and info['entries']:
                        entry = info['entries'][0]
                        return Song(
                            title=entry.get('title', 'Unknown'),
                            url=entry.get('webpage_url', ''),
                            duration=entry.get('duration', 0),
                            requester=None,
                            source='youtube',
                            thumbnail=entry.get('thumbnail', ''),
                            artist=entry.get('uploader', 'Unknown'),
                        )
            elif source == 'direct_url':
                with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                    info = ydl.extract_info(query, download=False)
                    return Song(
                        title=info.get('title', 'Unknown'),
                        url=query,
                        duration=info.get('duration', 0),
                        requester=None,
                        source=source,
                        thumbnail=info.get('thumbnail', ''),
                    )
        except Exception as e:
            logger.error(f"Error fetching song info: {e}")
        
        return None
    
    @commands.hybrid_command(name='play', description='Play a song')
    async def play(self, ctx, *, query: str):
        """Play a song from YouTube or other sources."""
        if not ctx.author.voice:
            await ctx.send("❌ You must be in a voice channel to use this command!")
            return
        
        async with ctx.typing():
            player = self.get_player(ctx.guild.id)
            
            try:
                song = await self.get_song_info(query, 'youtube')
                if song:
                    song.requester = ctx.author
                    player.add_to_queue(song)
                    
                    embed = discord.Embed(
                        title="✅ Song Added to Queue",
                        color=0x1DB954
                    )
                    embed.add_field(name="Title", value=song.title, inline=False)
                    embed.add_field(name="Duration", value=self._format_duration(song.duration), inline=True)
                    embed.add_field(name="Position", value=f"#{len(player.queue)}", inline=True)
                    embed.add_field(name="Requested by", value=ctx.author.mention, inline=True)
                    
                    if song.thumbnail:
                        embed.set_thumbnail(url=song.thumbnail)
                    
                    embed.timestamp = datetime.utcnow()
                    await ctx.send(embed=embed)
                    
                    if not player.is_playing:
                        await self._play_next(ctx)
                else:
                    await ctx.send("❌ Could not find the song. Try a different search query.")
            except Exception as e:
                logger.error(f"Error playing song: {e}")
                await ctx.send(f"❌ An error occurred: {str(e)[:100]}")
    
    @commands.hybrid_command(name='pause', description='Pause the current song')
    async def pause(self, ctx):
        """Pause the current song."""
        player = self.get_player(ctx.guild.id)
        
        if not player.is_playing:
            await ctx.send("❌ No song is currently playing!")
            return
        
        player.is_paused = True
        
        embed = discord.Embed(
            title="⏸️ Paused",
            description=f"Paused: **{player.current_song.title}**",
            color=0xFFA500
        )
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='resume', description='Resume the paused song')
    async def resume(self, ctx):
        """Resume the paused song."""
        player = self.get_player(ctx.guild.id)
        
        if not player.current_song or not player.is_paused:
            await ctx.send("❌ No paused song to resume!")
            return
        
        player.is_paused = False
        
        embed = discord.Embed(
            title="▶️ Resumed",
            description=f"Now playing: **{player.current_song.title}**",
            color=0x1DB954
        )
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='skip', description='Skip the current song')
    async def skip(self, ctx):
        """Skip the current song."""
        player = self.get_player(ctx.guild.id)
        
        if not player.is_playing:
            await ctx.send("❌ No song is currently playing!")
            return
        
        player.is_paused = False
        current = player.current_song
        
        embed = discord.Embed(
            title="⏭️ Skipped",
            description=f"Skipped: **{current.title}**",
            color=0x1DB954
        )
        
        await ctx.send(embed=embed)
        await self._play_next(ctx)
    
    @commands.hybrid_command(name='stop', description='Stop the music and clear queue')
    async def stop(self, ctx):
        """Stop playing music."""
        player = self.get_player(ctx.guild.id)
        
        if not player.is_playing:
            await ctx.send("❌ No song is currently playing!")
            return
        
        player.is_playing = False
        player.is_paused = False
        player.clear_queue()
        player.current_song = None
        
        embed = discord.Embed(
            title="⏹️ Stopped",
            description="Music stopped and queue cleared.",
            color=0xFF0000
        )
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='queue', description='Show the current queue')
    async def queue_command(self, ctx, page: int = 1):
        """Display the music queue."""
        player = self.get_player(ctx.guild.id)
        
        if not player.queue and not player.current_song:
            await ctx.send("❌ Queue is empty!")
            return
        
        # Pagination
        page_size = 10
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        queue_list = list(player.queue)
        total_pages = (len(queue_list) + page_size - 1) // page_size
        
        if page < 1 or page > total_pages:
            await ctx.send(f"❌ Invalid page. Total pages: {total_pages}")
            return
        
        embed = discord.Embed(
            title="🎵 Music Queue",
            color=0x1DB954
        )
        
        # Current song
        if player.current_song:
            embed.add_field(
                name="Now Playing",
                value=f"**{player.current_song.title}** "
                      f"[{self._format_duration(player.current_song.duration)}]\n"
                      f"Requested by {player.current_song.requester.mention}",
                inline=False
            )
        
        # Queue items
        queue_str = ""
        for i in range(start_idx, min(end_idx, len(queue_list))):
            song = queue_list[i]
            queue_str += f"{i+1}. **{song.title}** [{self._format_duration(song.duration)}]\n"
        
        if queue_str:
            embed.add_field(
                name=f"Queue (Page {page}/{total_pages})",
                value=queue_str,
                inline=False
            )
        
        # Queue stats
        total_duration = sum(song.duration for song in queue_list)
        embed.add_field(
            name="Queue Stats",
            value=f"Songs: {len(queue_list)}\nTotal Duration: {self._format_duration(total_duration)}",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='nowplaying', aliases=['np'], description='Show now playing song')
    async def nowplaying(self, ctx):
        """Show the currently playing song."""
        player = self.get_player(ctx.guild.id)
        
        if not player.current_song:
            await ctx.send("❌ No song is currently playing!")
            return
        
        song = player.current_song
        progress = self._create_progress_bar(player.current_position, song.duration)
        
        embed = discord.Embed(
            title="🎵 Now Playing",
            description=f"**{song.title}**",
            color=0x1DB954
        )
        
        embed.add_field(name="Artist", value=song.artist or "Unknown", inline=True)
        embed.add_field(name="Source", value=song.source.capitalize(), inline=True)
        embed.add_field(name="Requested by", value=song.requester.mention, inline=True)
        
        embed.add_field(
            name="Progress",
            value=f"{progress}\n{self._format_duration(player.current_position)} / {self._format_duration(song.duration)}",
            inline=False
        )
        
        embed.add_field(
            name="Queue Position",
            value=f"Song {player.listening_history[song.requester.id].__len__() or 1} in queue",
            inline=True
        )
        
        if song.thumbnail:
            embed.set_thumbnail(url=song.thumbnail)
        
        embed.timestamp = datetime.utcnow()
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='volume', description='Set the volume (0-200%)')
    async def volume(self, ctx, level: int):
        """Set the volume level."""
        if level < 0 or level > 200:
            await ctx.send("❌ Volume must be between 0 and 200!")
            return
        
        player = self.get_player(ctx.guild.id)
        player.volume = level
        
        embed = discord.Embed(
            title="🔊 Volume Changed",
            description=f"Volume set to {level}%",
            color=0x1DB954
        )
        embed.add_field(name="Volume Bar", value=self._create_volume_bar(level), inline=False)
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='loop', description='Set loop mode (none/one/all)')
    async def loop(self, ctx, mode: str = None):
        """Set the loop mode."""
        player = self.get_player(ctx.guild.id)
        
        if mode is None:
            mode = {'none': 'one', 'one': 'all', 'all': 'none'}[player.loop_mode]
        
        if mode not in ['none', 'one', 'all']:
            await ctx.send("❌ Invalid mode! Use: none, one, or all")
            return
        
        player.loop_mode = mode
        
        mode_display = {
            'none': '🔁 Loop Disabled',
            'one': '🔂 Loop One Song',
            'all': '🔁 Loop All Queue'
        }
        
        embed = discord.Embed(
            title=mode_display[mode],
            color=0x1DB954
        )
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='shuffle', description='Shuffle the queue')
    async def shuffle(self, ctx):
        """Shuffle the queue."""
        player = self.get_player(ctx.guild.id)
        
        if not player.queue:
            await ctx.send("❌ Queue is empty!")
            return
        
        player.shuffle_queue()
        
        embed = discord.Embed(
            title="🔀 Queue Shuffled",
            description=f"Shuffled {len(player.queue)} songs",
            color=0x1DB954
        )
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='seek', description='Seek to a specific position in the song')
    async def seek(self, ctx, minutes: int, seconds: int = 0):
        """Seek to a specific position."""
        player = self.get_player(ctx.guild.id)
        
        if not player.current_song:
            await ctx.send("❌ No song is currently playing!")
            return
        
        position = minutes * 60 + seconds
        
        if position > player.current_song.duration:
            await ctx.send(f"❌ Position exceeds song duration ({self._format_duration(player.current_song.duration)})")
            return
        
        player.current_position = position
        
        embed = discord.Embed(
            title="⏩ Seeked",
            description=f"Jumped to {self._format_duration(position)}",
            color=0x1DB954
        )
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='remove', description='Remove a song from the queue')
    async def remove(self, ctx, position: int):
        """Remove a song from the queue."""
        player = self.get_player(ctx.guild.id)
        
        if position < 1 or position > len(player.queue):
            await ctx.send(f"❌ Invalid position! Queue has {len(player.queue)} songs.")
            return
        
        song = player.remove_from_queue(position - 1)
        
        if song:
            embed = discord.Embed(
                title="🗑️ Song Removed",
                description=f"Removed **{song.title}** from position {position}",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='move', description='Move a song in the queue')
    async def move(self, ctx, from_pos: int, to_pos: int):
        """Move a song in the queue."""
        player = self.get_player(ctx.guild.id)
        
        if player.move_song(from_pos - 1, to_pos - 1):
            embed = discord.Embed(
                title="↪️ Song Moved",
                description=f"Moved song from position {from_pos} to {to_pos}",
                color=0x1DB954
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Invalid positions!")
    
    @commands.hybrid_command(name='favorite', description='Add a song to favorites')
    async def favorite(self, ctx):
        """Add current song to favorites."""
        player = self.get_player(ctx.guild.id)
        
        if not player.current_song:
            await ctx.send("❌ No song is currently playing!")
            return
        
        if player.current_song in player.favorite_songs:
            await ctx.send("❌ This song is already in your favorites!")
            return
        
        player.favorite_songs.append(player.current_song)
        
        embed = discord.Embed(
            title="❤️ Added to Favorites",
            description=f"**{player.current_song.title}** added to your favorites",
            color=0xFF0000
        )
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='history', description='Show your listening history')
    async def history(self, ctx, page: int = 1):
        """Show listening history."""
        player = self.get_player(ctx.guild.id)
        
        history = player.listening_history.get(ctx.author.id, [])
        
        if not history:
            await ctx.send("❌ No listening history found!")
            return
        
        page_size = 10
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        total_pages = (len(history) + page_size - 1) // page_size
        
        if page < 1 or page > total_pages:
            await ctx.send(f"❌ Invalid page. Total pages: {total_pages}")
            return
        
        embed = discord.Embed(
            title="🎵 Your Listening History",
            color=0x1DB954
        )
        
        history_str = ""
        for i in range(end_idx - 1, max(start_idx - 1, -1), -1):  # Reverse order
            entry = history[i]
            song = entry['song']
            timestamp = entry['timestamp']
            history_str += f"{len(history)-i}. **{song['title']}** - {song.get('artist', 'Unknown')}\n"
        
        embed.add_field(
            name=f"Recent Songs (Page {page}/{total_pages})",
            value=history_str or "No history",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='stats', description='Show music statistics for the server')
    async def stats(self, ctx):
        """Show server music statistics."""
        player = self.get_player(ctx.guild.id)
        
        top_songs = player.get_top_songs(5)
        top_artists = player.get_top_artists(5)
        
        embed = discord.Embed(
            title="📊 Server Music Statistics",
            color=0x1DB954
        )
        
        if top_songs:
            songs_str = "\n".join(f"{i+1}. **{song}** ({count} plays)" for i, (song, count) in enumerate(top_songs))
            embed.add_field(name="Top Songs", value=songs_str, inline=False)
        
        if top_artists:
            artists_str = "\n".join(f"{i+1}. **{artist}** ({count} plays)" for i, (artist, count) in enumerate(top_artists))
            embed.add_field(name="Top Artists", value=artists_str, inline=False)
        
        embed.timestamp = datetime.utcnow()
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='speed', description='Set playback speed (0.5x to 2x)')
    async def speed(self, ctx, speed: float):
        """Set playback speed."""
        if speed < 0.5 or speed > 2.0:
            await ctx.send("❌ Speed must be between 0.5 and 2.0!")
            return
        
        player = self.get_player(ctx.guild.id)
        player.speed = speed
        
        embed = discord.Embed(
            title="⚡ Playback Speed Changed",
            description=f"Speed set to {speed}x",
            color=0x1DB954
        )
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='equalizer', description='Set audio equalizer preset')
    async def equalizer(self, ctx, preset: str = None):
        """Set equalizer preset."""
        if preset is None:
            presets = ", ".join(f"`{p}`" for p in EQUALIZER_PRESETS.keys())
            await ctx.send(f"Available presets: {presets}")
            return
        
        if preset not in EQUALIZER_PRESETS:
            await ctx.send(f"❌ Unknown preset! Available: {', '.join(EQUALIZER_PRESETS.keys())}")
            return
        
        player = self.get_player(ctx.guild.id)
        player.equalizer = list(EQUALIZER_PRESETS[preset])
        
        embed = discord.Embed(
            title="🎚️ Equalizer Changed",
            description=f"Preset set to **{preset}**",
            color=0x1DB954
        )
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='nightcore', description='Enable/disable nightcore effect')
    async def nightcore(self, ctx):
        """Toggle nightcore effect."""
        player = self.get_player(ctx.guild.id)
        player.nightcore_enabled = not player.nightcore_enabled
        player.speed = 1.25 if player.nightcore_enabled else 1.0
        
        status = "✅ Enabled" if player.nightcore_enabled else "❌ Disabled"
        embed = discord.Embed(
            title="🌙 Nightcore Effect",
            description=f"Nightcore {status}",
            color=0x1DB954
        )
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='slowed', description='Enable/disable slowed effect')
    async def slowed(self, ctx):
        """Toggle slowed effect."""
        player = self.get_player(ctx.guild.id)
        player.slowed_enabled = not player.slowed_enabled
        player.speed = 0.8 if player.slowed_enabled else 1.0
        
        status = "✅ Enabled" if player.slowed_enabled else "❌ Disabled"
        embed = discord.Embed(
            title="🐢 Slowed Effect",
            description=f"Slowed {status}",
            color=0x1DB954
        )
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='playlist', description='Create or manage playlists')
    async def playlist(self, ctx, action: str, *, name: str = None):
        """Manage playlists."""
        player = self.get_player(ctx.guild.id)
        
        if action == 'create':
            if not name:
                await ctx.send("❌ Please provide a playlist name!")
                return
            if player.save_queue_as_playlist(name):
                embed = discord.Embed(
                    title="📋 Playlist Created",
                    description=f"Saved queue as **{name}** ({len(player.queue)} songs)",
                    color=0x1DB954
                )
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"❌ Playlist **{name}** already exists!")
        
        elif action == 'load':
            if not name:
                await ctx.send("❌ Please provide a playlist name!")
                return
            if player.load_playlist(name):
                embed = discord.Embed(
                    title="📋 Playlist Loaded",
                    description=f"Loaded **{name}** ({len(player.playlists[name])} songs)",
                    color=0x1DB954
                )
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"❌ Playlist **{name}** not found!")
        
        elif action == 'list':
            if not player.playlists:
                await ctx.send("❌ No playlists found!")
                return
            playlists_str = "\n".join(f"• **{name}** ({len(songs)} songs)" 
                                      for name, songs in player.playlists.items())
            embed = discord.Embed(
                title="📋 Your Playlists",
                description=playlists_str,
                color=0x1DB954
            )
            await ctx.send(embed=embed)
        
        elif action == 'delete':
            if not name:
                await ctx.send("❌ Please provide a playlist name!")
                return
            if name in player.playlists:
                del player.playlists[name]
                await ctx.send(f"✅ Deleted playlist **{name}**")
            else:
                await ctx.send(f"❌ Playlist **{name}** not found!")
    
    @commands.hybrid_command(name='clearmood', description='Get mood-based playlist recommendations')
    async def clearmood(self, ctx, mood: str):
        """Get mood-based playlist."""
        if mood not in MOOD_PLAYLISTS:
            moods = ", ".join(f"`{m}`" for m in MOOD_PLAYLISTS.keys())
            await ctx.send(f"Available moods: {moods}")
            return
        
        keywords = MOOD_PLAYLISTS[mood]
        
        embed = discord.Embed(
            title=f"🎵 {mood.capitalize()} Playlist",
            description=f"Keywords: {', '.join(keywords)}",
            color=0x1DB954
        )
        embed.add_field(
            name="Available Keywords",
            value=", ".join(keywords),
            inline=False
        )
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='decade', description='Get decade-based playlist recommendations')
    async def decade(self, ctx, decade: str):
        """Get decade-based playlist."""
        if decade not in DECADE_PLAYLISTS:
            decades = ", ".join(f"`{d}`" for d in DECADE_PLAYLISTS.keys())
            await ctx.send(f"Available decades: {decades}")
            return
        
        playlist_name = DECADE_PLAYLISTS[decade]
        
        embed = discord.Embed(
            title=f"🎵 {decade} Hits",
            description=f"Search: **{playlist_name}**",
            color=0x1DB954
        )
        await ctx.send(embed=embed)
    
    def _format_duration(self, seconds: int) -> str:
        """Format duration in MM:SS format."""
        if seconds < 0:
            seconds = 0
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}:{seconds:02d}"
    
    def _create_progress_bar(self, current: int, total: int, length: int = 20) -> str:
        """Create a progress bar."""
        if total == 0:
            return "▬" * length
        
        filled = int(length * current / total)
        bar = "🟢" + "▬" * (filled - 1) + "🟤" + "▬" * (length - filled)
        return bar
    
    def _create_volume_bar(self, level: int) -> str:
        """Create a volume bar."""
        filled = int(10 * level / 200)
        return "🔊 " + "█" * filled + "░" * (10 - filled) + f" {level}%"
    
    async def _play_next(self, ctx):
        """Play the next song in queue."""
        player = self.get_player(ctx.guild.id)
        
        song = player.get_next_song()
        if song:
            player.current_song = song
            player.is_playing = True
            player.current_position = 0
            player.start_time = datetime.now()
            
            # Update user stats
            player.user_stats[song.requester.id]['total_songs_played'] += 1
            if song.artist:
                player.user_stats[song.requester.id]['top_artists'][song.artist] += 1
        else:
            player.is_playing = False
            player.current_song = None


async def setup(bot):
    """Setup function for the cog."""
    await bot.add_cog(MusicCog(bot))
