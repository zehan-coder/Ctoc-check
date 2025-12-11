"""
Music Configuration and Constants
Provides configuration, presets, and constants for the advanced music system.
"""

from enum import Enum
from typing import Dict, List

# Audio quality presets
AUDIO_QUALITY = {
    'low': {'bitrate': 96, 'description': 'Low quality - faster streaming'},
    'standard': {'bitrate': 128, 'description': 'Standard quality'},
    'high': {'bitrate': 192, 'description': 'High quality'},
    'very_high': {'bitrate': 256, 'description': 'Very high quality'},
    'lossless': {'bitrate': 320, 'description': 'Lossless quality - best sound'},
}

# Equalizer presets
EQUALIZER_PRESETS = {
    'flat': {
        'name': 'Flat',
        'values': [0, 0, 0, 0, 0],
        'description': 'No audio modification'
    },
    'bass_boost': {
        'name': 'Bass Boost',
        'values': [5, 3, 1, 0, -2],
        'description': 'Enhanced bass frequencies'
    },
    'pop': {
        'name': 'Pop',
        'values': [2, 1, -1, 2, 3],
        'description': 'Optimized for pop music'
    },
    'metal': {
        'name': 'Metal',
        'values': [4, 3, 1, 2, 4],
        'description': 'Enhanced for metal music'
    },
    'jazz': {
        'name': 'Jazz',
        'values': [3, 2, 0, 1, 3],
        'description': 'Optimized for jazz'
    },
    'classical': {
        'name': 'Classical',
        'values': [2, 1, 0, 1, 2],
        'description': 'Optimized for classical music'
    },
    'hip_hop': {
        'name': 'Hip-Hop',
        'values': [3, 2, -1, 1, 2],
        'description': 'Enhanced for hip-hop and rap'
    },
    'rock': {
        'name': 'Rock',
        'values': [3, 2, 1, 2, 3],
        'description': 'Optimized for rock music'
    },
    'electronic': {
        'name': 'Electronic',
        'values': [2, 1, 2, 1, 1],
        'description': 'Enhanced for electronic music'
    },
}

# Mood-based playlists
MOOD_PLAYLISTS = {
    'chill': {
        'keywords': ['relaxing', 'ambient', 'lo-fi', 'chillhop', 'chill'],
        'emoji': '😌',
        'description': 'Relaxing and calming music'
    },
    'energetic': {
        'keywords': ['electronic', 'dance', 'upbeat pop', 'workout', 'energetic'],
        'emoji': '⚡',
        'description': 'High energy and upbeat music'
    },
    'sad': {
        'keywords': ['sad', 'emotional', 'ballad', 'melancholic', 'introspective'],
        'emoji': '😢',
        'description': 'Emotional and melancholic music'
    },
    'happy': {
        'keywords': ['happy', 'upbeat', 'feel-good', 'indie pop', 'cheerful'],
        'emoji': '😊',
        'description': 'Happy and feel-good music'
    },
    'focus': {
        'keywords': ['study', 'lo-fi hip hop', 'instrumental', 'ambient', 'focus'],
        'emoji': '🎯',
        'description': 'Music for focus and concentration'
    },
    'party': {
        'keywords': ['party', 'club', 'dance', 'electronic', 'hype'],
        'emoji': '🎉',
        'description': 'Party and club music'
    },
    'romantic': {
        'keywords': ['romantic', 'love', 'slow', 'ballad', 'soft'],
        'emoji': '💕',
        'description': 'Romantic and love songs'
    },
    'workout': {
        'keywords': ['workout', 'gym', 'intense', 'high energy', 'motivation'],
        'emoji': '💪',
        'description': 'High energy workout music'
    },
}

# Decade-based playlists
DECADE_PLAYLISTS = {
    '1980s': {
        'search_query': 'hits of the 1980s',
        'emoji': '📻',
        'description': 'Popular hits from the 1980s'
    },
    '1990s': {
        'search_query': 'hits of the 1990s',
        'emoji': '🎬',
        'description': 'Popular hits from the 1990s'
    },
    '2000s': {
        'search_query': 'hits of the 2000s',
        'emoji': '💿',
        'description': 'Popular hits from the 2000s'
    },
    '2010s': {
        'search_query': 'hits of the 2010s',
        'emoji': '📱',
        'description': 'Popular hits from the 2010s'
    },
    '2020s': {
        'search_query': 'hits of the 2020s',
        'emoji': '🎵',
        'description': 'Popular hits from the 2020s'
    },
}

# Genre definitions
GENRES = {
    'pop': '🎤',
    'rock': '🎸',
    'hip_hop': '🎤',
    'r_and_b': '🎹',
    'electronic': '🎛️',
    'country': '🤠',
    'jazz': '🎷',
    'classical': '🎻',
    'metal': '🤘',
    'indie': '🎸',
    'folk': '🎸',
    'soul': '🎤',
    'funk': '🎷',
    'reggae': '🌴',
    'latin': '🎺',
    'k_pop': '🇰🇷',
    'anime': '🎌',
    'game_music': '🎮',
}

# Loop modes
LOOP_MODES = {
    'none': {'emoji': '➡️', 'description': 'No looping'},
    'one': {'emoji': '🔂', 'description': 'Loop current song'},
    'all': {'emoji': '🔁', 'description': 'Loop entire queue'},
}

# Play status
PLAY_STATUS = {
    'playing': '▶️',
    'paused': '⏸️',
    'stopped': '⏹️',
    'loading': '⏳',
    'error': '❌',
}

# Special effects
SPECIAL_EFFECTS = {
    'nightcore': {
        'name': 'Nightcore',
        'emoji': '🌙',
        'speed_multiplier': 1.25,
        'pitch_shift': 1.2,
        'description': 'Sped up and pitched up effect'
    },
    'slowed': {
        'name': 'Slowed',
        'emoji': '🐢',
        'speed_multiplier': 0.8,
        'pitch_shift': 0.8,
        'description': 'Slowed down and pitched down effect'
    },
    'bass_boost': {
        'name': 'Bass Boost',
        'emoji': '🔊',
        'equalizer_preset': 'bass_boost',
        'description': 'Enhanced bass frequencies'
    },
    'reverb': {
        'name': 'Reverb',
        'emoji': '🎵',
        'description': 'Added reverb/echo effect'
    },
}

# Command help messages
COMMAND_HELP = {
    'play': 'Play a song: `!play <song name or URL>`',
    'pause': 'Pause the current song: `!pause`',
    'resume': 'Resume paused music: `!resume`',
    'skip': 'Skip to next song: `!skip`',
    'stop': 'Stop music and clear queue: `!stop`',
    'queue': 'View the music queue: `!queue [page]`',
    'nowplaying': 'Show current song: `!nowplaying`',
    'volume': 'Set volume (0-200%): `!volume <level>`',
    'loop': 'Set loop mode: `!loop [none|one|all]`',
    'shuffle': 'Shuffle the queue: `!shuffle`',
    'seek': 'Seek to position: `!seek <minutes> [seconds]`',
    'remove': 'Remove song from queue: `!remove <position>`',
    'move': 'Move song in queue: `!move <from> <to>`',
    'favorite': 'Add song to favorites: `!favorite`',
    'history': 'View listening history: `!history [page]`',
    'stats': 'View music statistics: `!stats`',
    'speed': 'Set playback speed: `!speed <0.5-2.0>`',
    'equalizer': 'Set equalizer: `!equalizer <preset>`',
    'nightcore': 'Toggle nightcore effect: `!nightcore`',
    'slowed': 'Toggle slowed effect: `!slowed`',
    'playlist': 'Manage playlists: `!playlist <create|load|list|delete> [name]`',
    'mood': 'Get mood-based playlist: `!clearmood <mood>`',
    'decade': 'Get decade playlist: `!decade <decade>`',
    'lyrics': 'Show lyrics for current song: `!lyrics`',
    'search': 'Advanced search with filters: `!search <query>`',
    'recommendations': 'Get music recommendations: `!recommendations`',
    'radio': 'Enable/disable radio mode: `!radio`',
    'vote': 'Vote to skip song: `!vote`',
}

# Error messages
ERROR_MESSAGES = {
    'not_in_voice': '❌ You must be in a voice channel to use this command!',
    'no_song_playing': '❌ No song is currently playing!',
    'empty_queue': '❌ Queue is empty!',
    'invalid_position': '❌ Invalid position!',
    'search_failed': '❌ Could not find the song. Try a different search query.',
    'api_error': '❌ An API error occurred. Please try again later.',
    'connection_failed': '❌ Failed to connect to voice channel!',
    'no_permission': '❌ You do not have permission to use this command!',
    'no_results': '❌ No results found for your search.',
    'not_in_guild': '❌ This command can only be used in a server!',
    'bot_not_in_voice': '❌ Bot is not connected to a voice channel!',
    'user_not_in_bot_channel': '❌ You must be in the same voice channel as the bot!',
}

# Success messages
SUCCESS_MESSAGES = {
    'song_added': '✅ Song added to queue!',
    'paused': '⏸️ Music paused',
    'resumed': '▶️ Music resumed',
    'skipped': '⏭️ Song skipped',
    'stopped': '⏹️ Music stopped',
    'queue_cleared': '✅ Queue cleared!',
    'shuffled': '🔀 Queue shuffled!',
    'voted': '✅ Vote recorded!',
    'playlist_created': '✅ Playlist created!',
    'playlist_loaded': '✅ Playlist loaded!',
    'removed_from_favorites': '❤️ Removed from favorites',
    'added_to_favorites': '❤️ Added to favorites',
}

# Info colors (Discord embed colors)
EMBED_COLORS = {
    'success': 0x1DB954,    # Spotify Green
    'error': 0xFF0000,      # Red
    'info': 0x7289DA,       # Discord Blue
    'warning': 0xFFA500,    # Orange
    'now_playing': 0x1DB954,
    'queue': 0x7289DA,
    'stats': 0x9C27B0,      # Purple
    'lyrics': 0x9C27B0,
    'recommendations': 0xFF6B6B,
    'playlist': 0x4ECDC4,
}

# Maximum values
MAX_QUEUE_SIZE = 500
MAX_FAVORITES = 1000
MAX_PLAYLISTS = 50
MAX_PLAYLIST_SIZE = 500
MAX_HISTORY_ENTRIES = 500

# Default settings
DEFAULT_SETTINGS = {
    'volume': 100,
    'quality': 'high',
    'loop_mode': 'none',
    'allow_explicit': True,
    'auto_play': True,
    'shuffle': False,
    'skip_votes': 3,
    'announce_songs': True,
    'crossfade': False,
}

# API endpoints
API_ENDPOINTS = {
    'lyrics_ovh': 'https://api.lyrics.ovh/v1',
    'genius': 'https://api.genius.com',
    'apple_music': 'https://api.music.apple.com/v1',
    'deezer': 'https://api.deezer.com',
    'spotify_search': 'https://api.spotify.com/v1/search',
}

# Music source patterns
SOURCE_PATTERNS = {
    'youtube': [
        r'youtube\.com/watch\?v=',
        r'youtu\.be/',
        r'youtube\.com/playlist\?list=',
        r'youtube\.com/shorts/',
    ],
    'spotify': [
        r'spotify\.com/track/',
        r'spotify\.com/playlist/',
        r'spotify\.com/album/',
        r'spotify\.com/artist/',
    ],
    'soundcloud': [
        r'soundcloud\.com/',
        r'snd\.sc/',
    ],
    'direct_audio': [
        r'\.mp3$',
        r'\.wav$',
        r'\.flac$',
        r'\.ogg$',
        r'\.m4a$',
    ]
}