"""
Advanced Music Features Module
Provides recommendations, discovery, advanced search, and analytics.
"""

import asyncio
import json
import logging
from collections import defaultdict, Counter
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """Generates music recommendations based on user behavior."""
    
    def __init__(self):
        self.user_listening_history: Dict[int, List[dict]] = defaultdict(list)
        self.genre_weights: Dict[int, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        self.artist_weights: Dict[int, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
    
    def record_listen(self, user_id: int, song_data: dict, genre: str = None):
        """Record a song listen for recommendations."""
        self.user_listening_history[user_id].append({
            'song': song_data,
            'timestamp': datetime.now().isoformat(),
            'genre': genre
        })
        
        # Update weights
        if genre:
            self.genre_weights[user_id][genre] += 1.0
        
        if song_data.get('artist'):
            self.artist_weights[user_id][song_data['artist']] += 1.0
    
    def get_recommendations(self, user_id: int, limit: int = 10) -> List[dict]:
        """Get personalized recommendations for a user."""
        if user_id not in self.user_listening_history:
            return []
        
        # Get user's top genres
        top_genres = sorted(
            self.genre_weights[user_id].items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        # Get user's top artists
        top_artists = sorted(
            self.artist_weights[user_id].items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        recommendations = []
        
        # This would normally query a music API for similar songs
        # For now, return metadata that can be used for searching
        for genre, weight in top_genres:
            recommendations.append({
                'type': 'genre',
                'value': genre,
                'weight': weight,
                'search_query': f"similar to {genre}"
            })
        
        for artist, weight in top_artists:
            recommendations.append({
                'type': 'artist',
                'value': artist,
                'weight': weight,
                'search_query': f"songs like {artist}"
            })
        
        return sorted(recommendations, key=lambda x: x['weight'], reverse=True)[:limit]
    
    def get_similar_songs(self, song_data: dict, limit: int = 10) -> List[dict]:
        """Get songs similar to the current song."""
        recommendations = []
        
        # Based on artist
        if song_data.get('artist'):
            recommendations.append({
                'type': 'artist',
                'query': f"{song_data['artist']} similar",
                'reason': f'Songs by {song_data["artist"]}'
            })
        
        # Based on genre/mood (if available)
        if song_data.get('genre'):
            recommendations.append({
                'type': 'genre',
                'query': song_data['genre'],
                'reason': f'{song_data["genre"]} music'
            })
        
        # Based on era
        if song_data.get('year'):
            decade = (song_data['year'] // 10) * 10
            recommendations.append({
                'type': 'decade',
                'query': f'hits of the {decade}s',
                'reason': f'Music from {decade}s'
            })
        
        return recommendations[:limit]
    
    def get_user_taste_profile(self, user_id: int) -> dict:
        """Get a user's music taste profile."""
        if user_id not in self.user_listening_history:
            return {}
        
        history = self.user_listening_history[user_id]
        if not history:
            return {}
        
        # Genre distribution
        genres = defaultdict(int)
        artists = defaultdict(int)
        total_listen_time = 0
        
        for entry in history:
            if entry.get('genre'):
                genres[entry['genre']] += 1
            if entry['song'].get('artist'):
                artists[entry['song']['artist']] += 1
            total_listen_time += entry['song'].get('duration', 0)
        
        # Calculate percentages
        total_plays = len(history)
        genre_pct = {g: round((count / total_plays * 100), 2) 
                    for g, count in genres.items()}
        artist_pct = {a: round((count / total_plays * 100), 2) 
                     for a, count in artists.items()}
        
        return {
            'total_songs_played': total_plays,
            'total_listening_time': total_listen_time,
            'favorite_genre': max(genres.items(), key=lambda x: x[1])[0] if genres else None,
            'favorite_artist': max(artists.items(), key=lambda x: x[1])[0] if artists else None,
            'genre_distribution': genre_pct,
            'artist_distribution': artist_pct,
            'listening_hours_per_month': round(total_listen_time / 3600 / (len(history) / 30), 2) if history else 0,
        }


class MusicDiscovery:
    """Music discovery and search functionality."""
    
    TRENDING_KEYWORDS = {
        'current': ['trending now', 'viral', 'hot right now', 'new releases'],
        'classic': ['classic hits', 'timeless', 'best of all time', 'greatest hits'],
        'experimental': ['underground', 'indie', 'alternative', 'experimental'],
    }
    
    @staticmethod
    async def get_trending_songs(limit: int = 10) -> List[dict]:
        """Get trending songs."""
        # This would normally query Spotify/Apple Music/YouTube charts
        return [
            {
                'search_query': keyword,
                'type': 'trending'
            }
            for keyword in MusicDiscovery.TRENDING_KEYWORDS['current']
        ][:limit]
    
    @staticmethod
    async def get_genre_recommendations(genre: str, limit: int = 10) -> List[dict]:
        """Get songs by genre."""
        subgenres = {
            'pop': ['pop', 'dance pop', 'synth-pop', 'teen pop'],
            'rock': ['rock', 'alternative rock', 'indie rock', 'hard rock'],
            'hip_hop': ['hip hop', 'rap', 'trap', 'mumble rap'],
            'electronic': ['electronic', 'house', 'techno', 'dubstep'],
            'country': ['country', 'folk', 'country rock', 'bluegrass'],
            'r_and_b': ['R&B', 'soul', 'funk', 'disco'],
            'jazz': ['jazz', 'fusion', 'smooth jazz', 'bebop'],
            'classical': ['classical', 'orchestral', 'chamber', 'baroque'],
        }
        
        keywords = subgenres.get(genre, [genre])
        return [
            {
                'search_query': keyword,
                'type': 'genre',
                'genre': genre
            }
            for keyword in keywords
        ][:limit]
    
    @staticmethod
    def get_mood_search_queries(mood: str) -> List[str]:
        """Get search queries for a specific mood."""
        mood_queries = {
            'chill': [
                'chill lo-fi beats',
                'relaxing ambient music',
                'chillhop',
                'chill vibes',
                'peaceful piano'
            ],
            'energetic': [
                'high energy EDM',
                'workout music',
                'pump up songs',
                'dance music',
                'electronic energy'
            ],
            'sad': [
                'sad songs',
                'emotional ballads',
                'heartbreak songs',
                'melancholic music',
                'introspective'
            ],
            'happy': [
                'feel good songs',
                'happy music',
                'uplifting pop',
                'cheerful indie',
                'positive vibes'
            ],
            'focus': [
                'study music',
                'focus beats',
                'instrumental study',
                'background music',
                'concentration music'
            ],
            'party': [
                'party hits',
                'club bangers',
                'dance floor anthems',
                'party music',
                'club classics'
            ],
            'romantic': [
                'romantic songs',
                'love songs',
                'slow jams',
                'romantic ballads',
                'couples music'
            ],
            'workout': [
                'workout music',
                'gym motivation',
                'running music',
                'fitness beats',
                'high energy anthems'
            ],
        }
        
        return mood_queries.get(mood, [mood])


class AdvancedSearch:
    """Advanced search with filters and caching."""
    
    def __init__(self):
        self.search_history: Dict[int, List[dict]] = defaultdict(list)
        self.saved_searches: Dict[int, List[str]] = defaultdict(list)
        self.search_cache: Dict[str, List[dict]] = {}
        self.popular_searches: Counter = Counter()
    
    def record_search(self, user_id: int, query: str, results_count: int):
        """Record a search for analytics."""
        self.search_history[user_id].append({
            'query': query,
            'timestamp': datetime.now().isoformat(),
            'results_count': results_count
        })
        
        # Keep only last 100 searches per user
        if len(self.search_history[user_id]) > 100:
            self.search_history[user_id] = self.search_history[user_id][-100:]
        
        # Track popular searches
        self.popular_searches[query] += 1
    
    def save_search(self, user_id: int, query: str) -> bool:
        """Save a search for quick access."""
        if query not in self.saved_searches[user_id]:
            self.saved_searches[user_id].append(query)
            return True
        return False
    
    def remove_saved_search(self, user_id: int, query: str) -> bool:
        """Remove a saved search."""
        if query in self.saved_searches[user_id]:
            self.saved_searches[user_id].remove(query)
            return True
        return False
    
    def get_user_saved_searches(self, user_id: int) -> List[str]:
        """Get user's saved searches."""
        return self.saved_searches.get(user_id, [])
    
    def get_popular_searches(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Get the most popular searches across all users."""
        return self.popular_searches.most_common(limit)
    
    def cache_search_results(self, query: str, results: List[dict]):
        """Cache search results."""
        self.search_cache[query] = results
    
    def get_cached_results(self, query: str) -> Optional[List[dict]]:
        """Get cached search results."""
        return self.search_cache.get(query)
    
    def apply_filters(self, songs: List[dict], filters: Dict) -> List[dict]:
        """Apply filters to search results."""
        filtered = songs
        
        # Explicit content filter
        if not filters.get('allow_explicit', True):
            filtered = [s for s in filtered if not s.get('explicit', False)]
        
        # Duration filter
        if 'max_duration' in filters:
            max_duration = filters['max_duration'] * 60  # Convert to seconds
            filtered = [s for s in filtered if s.get('duration', 0) <= max_duration]
        
        if 'min_duration' in filters:
            min_duration = filters['min_duration'] * 60
            filtered = [s for s in filtered if s.get('duration', 0) >= min_duration]
        
        # Year filter
        if 'year' in filters:
            year = filters['year']
            filtered = [s for s in filtered if s.get('year') == year]
        
        # Year range filter
        if 'year_range' in filters:
            min_year, max_year = filters['year_range']
            filtered = [s for s in filtered if min_year <= s.get('year', min_year) <= max_year]
        
        # Genre filter
        if 'genre' in filters:
            genre = filters['genre'].lower()
            filtered = [s for s in filtered if genre in s.get('genre', '').lower()]
        
        # Artist filter
        if 'artist' in filters:
            artist = filters['artist'].lower()
            filtered = [s for s in filtered if artist in s.get('artist', '').lower()]
        
        return filtered


class ListeningAnalytics:
    """Advanced listening analytics and insights."""
    
    def __init__(self):
        self.server_stats: Dict[int, dict] = defaultdict(lambda: {
            'total_plays': 0,
            'unique_users': set(),
            'song_plays': defaultdict(int),
            'artist_plays': defaultdict(int),
            'hourly_plays': defaultdict(int),
            'daily_plays': defaultdict(int),
        })
    
    def record_server_play(self, guild_id: int, user_id: int, song: dict):
        """Record a song play for server statistics."""
        stats = self.server_stats[guild_id]
        stats['total_plays'] += 1
        stats['unique_users'].add(user_id)
        stats['song_plays'][song['title']] += 1
        stats['artist_plays'][song.get('artist', 'Unknown')] += 1
        
        # Hourly and daily tracking
        now = datetime.now()
        stats['hourly_plays'][now.hour] += 1
        stats['daily_plays'][now.strftime('%Y-%m-%d')] += 1
    
    def get_server_stats(self, guild_id: int) -> dict:
        """Get comprehensive server music statistics."""
        stats = self.server_stats[guild_id]
        
        return {
            'total_plays': stats['total_plays'],
            'unique_listeners': len(stats['unique_users']),
            'top_songs': sorted(stats['song_plays'].items(), key=lambda x: x[1], reverse=True)[:10],
            'top_artists': sorted(stats['artist_plays'].items(), key=lambda x: x[1], reverse=True)[:10],
            'peak_hour': max(stats['hourly_plays'].items(), key=lambda x: x[1])[0] if stats['hourly_plays'] else None,
            'total_listeners': len(stats['unique_users']),
        }
    
    def get_peak_listening_times(self, guild_id: int) -> Dict[int, int]:
        """Get peak listening times by hour."""
        return dict(self.server_stats[guild_id]['hourly_plays'])
    
    def get_listening_trends(self, guild_id: int, days: int = 7) -> List[Tuple[str, int]]:
        """Get listening trends over the last N days."""
        stats = self.server_stats[guild_id]
        trends = []
        
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            plays = stats['daily_plays'].get(date, 0)
            trends.append((date, plays))
        
        return sorted(trends, key=lambda x: x[0])
    
    def get_music_taste_summary(self, guild_id: int) -> dict:
        """Get a summary of the server's music taste."""
        stats = self.server_stats[guild_id]
        
        return {
            'most_popular_song': max(stats['song_plays'].items(), key=lambda x: x[1])[0] if stats['song_plays'] else None,
            'most_popular_artist': max(stats['artist_plays'].items(), key=lambda x: x[1])[0] if stats['artist_plays'] else None,
            'total_unique_songs': len(stats['song_plays']),
            'total_unique_artists': len(stats['artist_plays']),
            'average_plays_per_listener': stats['total_plays'] / len(stats['unique_users']) if stats['unique_users'] else 0,
        }


class RadioMode:
    """Auto-play similar songs functionality."""
    
    def __init__(self):
        self.active_radios: Dict[int, dict] = {}
    
    def enable_radio(self, guild_id: int, seed_song: dict, mode: str = 'artist'):
        """Enable radio mode based on a seed song."""
        self.active_radios[guild_id] = {
            'seed_song': seed_song,
            'mode': mode,  # artist, genre, decade
            'started_at': datetime.now().isoformat(),
            'played_count': 0,
        }
    
    def disable_radio(self, guild_id: int):
        """Disable radio mode."""
        if guild_id in self.active_radios:
            del self.active_radios[guild_id]
    
    def is_radio_enabled(self, guild_id: int) -> bool:
        """Check if radio mode is enabled."""
        return guild_id in self.active_radios
    
    def get_next_radio_song(self, guild_id: int) -> Optional[dict]:
        """Get next song for radio mode."""
        if guild_id not in self.active_radios:
            return None
        
        radio = self.active_radios[guild_id]
        mode = radio['mode']
        
        if mode == 'artist':
            return {
                'search_query': f"{radio['seed_song']['artist']} songs",
                'mode': 'artist'
            }
        elif mode == 'genre':
            return {
                'search_query': radio['seed_song'].get('genre', 'similar'),
                'mode': 'genre'
            }
        elif mode == 'decade':
            year = radio['seed_song'].get('year', 2020)
            decade = (year // 10) * 10
            return {
                'search_query': f"hits of the {decade}s",
                'mode': 'decade'
            }
        
        return None
