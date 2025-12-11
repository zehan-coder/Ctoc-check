"""
Music Utilities Module
Provides helper functions for music operations including lyrics fetching, 
metadata retrieval, and search functionality.
"""

import asyncio
import json
import logging
import os
from typing import Optional, Dict, List, Tuple
from datetime import datetime

import aiohttp
import requests

logger = logging.getLogger(__name__)


class LyricsManager:
    """Manage lyrics fetching from multiple sources."""
    
    GENIUS_TOKEN = os.getenv('GENIUS_TOKEN', '')
    LYRICS_OVH_API = "https://api.lyrics.ovh/v1"
    GENIUS_API = "https://api.genius.com"
    
    @classmethod
    async def get_lyrics_ovh(cls, artist: str, song: str) -> Optional[str]:
        """Get lyrics from Lyrics.ovh API."""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{cls.LYRICS_OVH_API}/{artist}/{song}"
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get('lyrics')
        except Exception as e:
            logger.error(f"Error fetching lyrics from Lyrics.ovh: {e}")
        return None
    
    @classmethod
    async def get_lyrics_genius(cls, song_title: str, artist: str) -> Optional[str]:
        """Get lyrics from Genius API."""
        if not cls.GENIUS_TOKEN:
            return None
        
        try:
            headers = {"Authorization": f"Bearer {cls.GENIUS_TOKEN}"}
            search_url = f"{cls.GENIUS_API}/search"
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
    def format_search_query(query: str, filters: Dict = None) -> str:
        """Format search query with optional filters."""
        if filters:
            if filters.get('year'):
                query += f" {filters['year']}"
            if filters.get('genre'):
                query += f" {filters['genre']}"
            if filters.get('duration'):
                query += f" duration:{filters['duration']}"
        
        return query
    
    @staticmethod
    async def search_youtube(query: str, max_results: int = 5) -> List[Dict]:
        """Search YouTube for music."""
        try:
            from youtube_search import YoutubeSearch
            
            results = YoutubeSearch(query, max_results=max_results).to_dict()
            formatted_results = []
            
            for result in results:
                formatted_results.append({
                    'title': result.get('title'),
                    'url': f"https://www.youtube.com/watch?v={result.get('id')}",
                    'thumbnail': result.get('thumbnails', [None])[0],
                    'channel': result.get('channel'),
                    'source': 'youtube'
                })
            
            return formatted_results
        except Exception as e:
            logger.error(f"Error searching YouTube: {e}")
            return []
    
    @staticmethod
    async def search_spotify(query: str, search_type: str = 'track', max_results: int = 5) -> List[Dict]:
        """Search Spotify for music."""
        try:
            import spotipy
            from spotipy.oauth2 import SpotifyClientCredentials
            
            client_id = os.getenv('SPOTIFY_CLIENT_ID')
            client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
            
            if not client_id or not client_secret:
                logger.warning("Spotify credentials not configured")
                return []
            
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


class MetadataManager:
    """Manage metadata retrieval for songs."""
    
    APPLE_MUSIC_API = "https://api.music.apple.com/v1"
    DEEZER_API = "https://api.deezer.com"
    
    @staticmethod
    async def get_apple_music_metadata(song_title: str, artist: str = None) -> Optional[Dict]:
        """Get metadata from Apple Music."""
        try:
            search_query = f"{song_title}"
            if artist:
                search_query += f" {artist}"
            
            async with aiohttp.ClientSession() as session:
                url = "https://itunes.apple.com/search"
                params = {
                    'term': search_query,
                    'media': 'music',
                    'entity': 'song',
                    'limit': 1
                }
                async with session.get(url, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data['results']:
                            result = data['results'][0]
                            return {
                                'title': result.get('trackName'),
                                'artist': result.get('artistName'),
                                'album': result.get('collectionName'),
                                'artwork_url': result.get('artworkUrl100'),
                                'preview_url': result.get('previewUrl'),
                                'explicit': result.get('trackExplicitness') == 'explicit',
                                'source': 'apple_music'
                            }
        except Exception as e:
            logger.error(f"Error fetching Apple Music metadata: {e}")
        
        return None
    
    @staticmethod
    async def get_deezer_metadata(song_title: str, artist: str = None) -> Optional[Dict]:
        """Get metadata from Deezer."""
        try:
            search_query = f"{song_title}"
            if artist:
                search_query += f" artist:{artist}"
            
            async with aiohttp.ClientSession() as session:
                url = "https://api.deezer.com/search"
                params = {'q': search_query, 'limit': 1}
                async with session.get(url, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data['data']:
                            track = data['data'][0]
                            return {
                                'title': track.get('title'),
                                'artist': track['artist']['name'] if track.get('artist') else 'Unknown',
                                'album': track.get('album', {}).get('title'),
                                'artwork_url': track.get('album', {}).get('cover_medium'),
                                'preview_url': track.get('preview'),
                                'duration': track.get('duration'),
                                'explicit': track.get('explicit_lyrics', False),
                                'source': 'deezer'
                            }
        except Exception as e:
            logger.error(f"Error fetching Deezer metadata: {e}")
        
        return None


class QueueStatistics:
    """Manage queue and listening statistics."""
    
    def __init__(self):
        self.user_stats: Dict[int, Dict] = {}
        self.server_stats: Dict[int, Dict] = {}
    
    def record_play(self, user_id: int, guild_id: int, song_title: str, 
                   artist: str, duration: int, genre: str = None):
        """Record a song play."""
        if user_id not in self.user_stats:
            self.user_stats[user_id] = {
                'total_plays': 0,
                'total_listening_time': 0,
                'top_artists': {},
                'top_genres': {},
                'listening_history': [],
                'favorite_genres': {}
            }
        
        stats = self.user_stats[user_id]
        stats['total_plays'] += 1
        stats['total_listening_time'] += duration
        
        if artist:
            stats['top_artists'][artist] = stats['top_artists'].get(artist, 0) + 1
        
        if genre:
            stats['top_genres'][genre] = stats['top_genres'].get(genre, 0) + 1
        
        stats['listening_history'].append({
            'title': song_title,
            'artist': artist,
            'timestamp': datetime.now().isoformat(),
            'duration': duration
        })
        
        # Keep only last 500 entries
        if len(stats['listening_history']) > 500:
            stats['listening_history'] = stats['listening_history'][-500:]
    
    def get_user_top_artists(self, user_id: int, limit: int = 10) -> List[Tuple[str, int]]:
        """Get user's top artists."""
        if user_id not in self.user_stats:
            return []
        
        artists = self.user_stats[user_id]['top_artists']
        return sorted(artists.items(), key=lambda x: x[1], reverse=True)[:limit]
    
    def get_user_top_genres(self, user_id: int, limit: int = 10) -> List[Tuple[str, int]]:
        """Get user's top genres."""
        if user_id not in self.user_stats:
            return []
        
        genres = self.user_stats[user_id]['top_genres']
        return sorted(genres.items(), key=lambda x: x[1], reverse=True)[:limit]
    
    def get_user_stats_summary(self, user_id: int) -> Dict:
        """Get user statistics summary."""
        if user_id not in self.user_stats:
            return {}
        
        stats = self.user_stats[user_id]
        return {
            'total_plays': stats['total_plays'],
            'total_listening_time': stats['total_listening_time'],
            'average_song_duration': stats['total_listening_time'] / max(stats['total_plays'], 1),
            'top_artist': max(stats['top_artists'].items(), key=lambda x: x[1])[0] if stats['top_artists'] else None,
            'top_genre': max(stats['top_genres'].items(), key=lambda x: x[1])[0] if stats['top_genres'] else None,
        }
    
    def get_listening_streak(self, user_id: int) -> int:
        """Get user's listening streak in days."""
        if user_id not in self.user_stats:
            return 0
        
        history = self.user_stats[user_id]['listening_history']
        if not history:
            return 0
        
        streak = 1
        last_date = datetime.fromisoformat(history[-1]['timestamp']).date()
        
        for i in range(len(history) - 2, -1, -1):
            current_date = datetime.fromisoformat(history[i]['timestamp']).date()
            if (last_date - current_date).days == 1:
                streak += 1
                last_date = current_date
            else:
                break
        
        return streak


class AudioQualityManager:
    """Manage audio quality and streaming settings."""
    
    QUALITY_SETTINGS = {
        '96': {'bitrate': 96, 'label': '96 kbps (Low)', 'format': 'mp3'},
        '128': {'bitrate': 128, 'label': '128 kbps (Standard)', 'format': 'mp3'},
        '192': {'bitrate': 192, 'label': '192 kbps (High)', 'format': 'mp3'},
        '256': {'bitrate': 256, 'label': '256 kbps (Very High)', 'format': 'aac'},
        '320': {'bitrate': 320, 'label': '320 kbps (Lossless)', 'format': 'mp3'},
        'flac': {'bitrate': None, 'label': 'FLAC (Lossless)', 'format': 'flac'},
        'opus': {'bitrate': 128, 'label': 'Opus (Efficient)', 'format': 'opus'},
    }
    
    @staticmethod
    def get_quality_preset(preset: str) -> Optional[Dict]:
        """Get quality preset settings."""
        return AudioQualityManager.QUALITY_SETTINGS.get(preset)
    
    @staticmethod
    def get_recommended_quality(bandwidth_mbps: float) -> str:
        """Get recommended quality based on bandwidth."""
        if bandwidth_mbps < 1:
            return '96'
        elif bandwidth_mbps < 2:
            return '128'
        elif bandwidth_mbps < 5:
            return '192'
        elif bandwidth_mbps < 10:
            return '320'
        else:
            return 'flac'
    
    @staticmethod
    def adapt_quality(current_quality: str, buffer_health: float) -> str:
        """Adapt quality based on buffer health (0-1)."""
        if buffer_health < 0.2:
            return '96'
        elif buffer_health < 0.4:
            return '128'
        elif buffer_health < 0.6:
            return '192'
        elif buffer_health < 0.8:
            return '256'
        else:
            return '320'


class PlaylistManager:
    """Manage user playlists."""
    
    def __init__(self):
        self.playlists: Dict[int, Dict[str, List]] = {}
    
    def create_playlist(self, user_id: int, playlist_name: str, description: str = None) -> bool:
        """Create a new playlist."""
        if user_id not in self.playlists:
            self.playlists[user_id] = {}
        
        if playlist_name not in self.playlists[user_id]:
            self.playlists[user_id][playlist_name] = {
                'songs': [],
                'created_at': datetime.now().isoformat(),
                'description': description or '',
                'is_collaborative': False,
                'collaborators': [user_id]
            }
            return True
        
        return False
    
    def add_song_to_playlist(self, user_id: int, playlist_name: str, song_data: Dict) -> bool:
        """Add song to playlist."""
        if user_id in self.playlists and playlist_name in self.playlists[user_id]:
            self.playlists[user_id][playlist_name]['songs'].append({
                **song_data,
                'added_at': datetime.now().isoformat()
            })
            return True
        
        return False
    
    def remove_song_from_playlist(self, user_id: int, playlist_name: str, song_index: int) -> bool:
        """Remove song from playlist."""
        if user_id in self.playlists and playlist_name in self.playlists[user_id]:
            songs = self.playlists[user_id][playlist_name]['songs']
            if 0 <= song_index < len(songs):
                songs.pop(song_index)
                return True
        
        return False
    
    def get_user_playlists(self, user_id: int) -> Dict[str, List]:
        """Get all playlists for a user."""
        return self.playlists.get(user_id, {})
    
    def delete_playlist(self, user_id: int, playlist_name: str) -> bool:
        """Delete a playlist."""
        if user_id in self.playlists and playlist_name in self.playlists[user_id]:
            del self.playlists[user_id][playlist_name]
            return True
        
        return False
