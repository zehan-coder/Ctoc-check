# Advanced Music Cog - Complete Guide

## Overview

The Advanced Music Cog provides professional-grade music playback, streaming, and management capabilities for Discord servers. It supports multiple audio sources, advanced playback controls, user preferences, and comprehensive statistics.

## Features

### Core Playback Features
- **Play/Pause/Resume/Stop** - Full playback control
- **Skip/Previous** - Navigate through songs
- **Volume Control** - 0-200% with smooth transitions
- **Seek/Jump** - Jump to specific song positions with progress display
- **Loop Modes** - None, Current Song, or All Queue
- **Shuffle** - Randomize queue order
- **Speed Control** - 0.5x to 2x playback speed
- **Equalizer** - Multiple audio presets (flat, bass boost, pop, metal, jazz, classical, hip-hop, rock, electronic)
- **Special Effects** - Nightcore, Slowed, Reverb
- **Time Display** - Current/total with progress bar

### Queue Management
- **Dynamic Queue Display** - Paginated queue viewing
- **Add/Remove Songs** - Add single songs or remove by position
- **Move Songs** - Reorder songs in the queue
- **Shuffle Queue** - Randomize queue order
- **Clear Queue** - Reset entire queue
- **Queue History** - View previously played songs
- **Save as Playlist** - Save current queue as a playlist
- **Load Playlists** - Load saved playlists into queue

### Search & Source Integration
- **YouTube Search** - Find and play from YouTube
- **Spotify Integration** - Search and play Spotify tracks
- **Direct URL Support** - YouTube, Spotify, SoundCloud, direct MP3/WAV
- **Local File Support** - Upload and play audio files
- **Auto-detect Source** - Automatically identify source type
- **Search Filtering** - Filter by explicit content, duration, quality

### Now Playing Display
- **Rich Embeds** - Professional now playing cards
- **Album Art** - Thumbnail/cover images
- **Song Info** - Title, artist, album information
- **Progress Bar** - Visual progress indicator
- **Requester Info** - Who requested the song
- **Queue Position** - Current position in queue
- **Real-time Updates** - Dynamic progress updates

### User Library & Favorites
- **Favorite Songs** - Save unlimited favorite songs
- **Personal Playlists** - Create and manage playlists
- **Playlist Operations** - Create, edit, delete, rename
- **Collaborative Playlists** - Multiple users edit together
- **Music Taste Profile** - Top artists, genres, decades

### Recommendations & Discovery
- **Similar Songs** - Find songs similar to current track
- **Genre Playlists** - Genre-based recommendations
- **Mood-based Playlists** - Chill, Energetic, Sad, Happy, Focus, Party, Romantic, Workout
- **Decade Playlists** - 1980s, 1990s, 2000s, 2010s, 2020s
- **Weekly Recommendations** - Personalized suggestions
- **Radio Mode** - Auto-play similar songs

### Statistics & Analytics
- **Listening History** - Track with timestamps
- **Top Played Songs** - Per user rankings
- **Top Artists** - Artist play counts
- **Server Statistics** - Most streamed songs and artists
- **Listening Time** - Hours per month tracking
- **Genre Preferences** - Breakdown by genre
- **Listening Streaks** - Consecutive days tracking
- **Leaderboards** - Most active music listeners

### Advanced Controls
- **Channel-specific Permissions** - Control per channel
- **DJ Role Requirements** - Restrict commands by role
- **Voting System** - Democratic skip voting
- **User Bans** - Ban users from music commands
- **Whitelist/Blacklist** - Control songs and artists
- **Content Filtering** - Filter explicit content
- **Autoplay** - Auto-fill queue when running low
- **Gapless Playback** - Seamless song transitions

### Performance & Quality
- **High-quality Streaming** - Up to 320kbps
- **Adaptive Bitrate** - Auto-adjust to connection
- **Low Latency Playback** - Minimal delay
- **Memory Efficient** - Optimized caching
- **Connection Pooling** - Reliable connections
- **Automatic Reconnection** - Handle disconnections gracefully
- **Quality Auto-selection** - Adjust based on bandwidth
- **Buffer Management** - Intelligent buffering

### Audio Processing
- **Equalizer Presets** - Metal, Pop, Jazz, Classical, etc.
- **Custom Settings** - Per-user customization
- **Nightcore Effect** - Speed + Pitch up
- **Slowed Effect** - Speed + Pitch down
- **Reverb Effect** - Echo and space effects
- **Voice Effects** - Echo, pitch shift options
- **Audio Normalization** - Volume leveling
- **Stereo/Mono Conversion** - Format options

### DJ/Admin Controls
- **Force Skip** - Bypass voting system
- **Force Pause/Resume** - Override user control
- **Kick from Voice** - Remove from voice channel
- **Session Management** - Control music sessions
- **Session History** - Track who played what
- **User Restrictions** - Prevent specific users
- **Rate Limiting** - Per-user command limits
- **Maintenance Mode** - Pause entire system

## Command Reference

### Basic Playback Commands

#### `!play <song name or URL>`
Plays a song from YouTube or other supported sources.
```
!play Never Gonna Give You Up
!play https://www.youtube.com/watch?v=dQw4w9WgXcQ
!play spotify:track:...
```

#### `!pause`
Pauses the currently playing song.

#### `!resume`
Resumes a paused song.

#### `!skip`
Skips to the next song in the queue.

#### `!stop`
Stops playback and clears the queue.

### Queue Management Commands

#### `!queue [page]`
Displays the current queue with pagination (10 songs per page).
```
!queue
!queue 2
```

#### `!nowplaying` or `!np`
Shows detailed information about the currently playing song.

#### `!remove <position>`
Removes a song at the specified position from the queue.
```
!remove 3
```

#### `!move <from> <to>`
Moves a song from one position to another.
```
!move 2 5
```

#### `!shuffle`
Randomizes the order of songs in the queue.

#### `!clear`
Clears the entire queue.

### Playback Control Commands

#### `!volume <0-200>`
Sets the volume level.
```
!volume 75
!volume 150
```

#### `!loop [none|one|all]`
Sets the loop mode:
- `none` - No looping
- `one` - Loop current song
- `all` - Loop entire queue
```
!loop all
```

#### `!seek <minutes> [seconds]`
Jumps to a specific position in the song.
```
!seek 2 30
!seek 1
```

#### `!speed <0.5-2.0>`
Sets the playback speed.
```
!speed 1.25  # 25% faster
!speed 0.8   # 20% slower
```

### Audio Effects Commands

#### `!equalizer <preset>`
Sets the equalizer to a preset:
- `flat` - No modifications
- `bass_boost` - Enhanced bass
- `pop` - Optimized for pop
- `metal` - Optimized for metal
- `jazz` - Optimized for jazz
- `classical` - Optimized for classical
- `hip_hop` - Optimized for hip-hop
- `rock` - Optimized for rock
- `electronic` - Optimized for electronic

```
!equalizer bass_boost
!equalizer pop
```

#### `!nightcore`
Toggles the nightcore effect (sped up, pitched up).

#### `!slowed`
Toggles the slowed effect (slowed down, pitched down).

### User Library Commands

#### `!favorite`
Adds the currently playing song to your favorites.

#### `!history [page]`
Shows your listening history with pagination.
```
!history
!history 2
```

#### `!stats`
Shows server music statistics including top songs and artists.

### Playlist Commands

#### `!playlist create <name>`
Creates a new playlist from the current queue.
```
!playlist create My Workout Mix
```

#### `!playlist load <name>`
Loads a saved playlist into the queue.
```
!playlist load My Workout Mix
```

#### `!playlist list`
Lists all your saved playlists.

#### `!playlist delete <name>`
Deletes a playlist.
```
!playlist delete My Workout Mix
```

### Discovery Commands

#### `!clearmood <mood>`
Gets music recommendations based on mood:
- `chill` - Relaxing music
- `energetic` - High energy music
- `sad` - Emotional music
- `happy` - Happy music
- `focus` - Study/focus music
- `party` - Party music
- `romantic` - Romantic music
- `workout` - Workout music

```
!clearmood chill
!clearmood energetic
```

#### `!decade <decade>`
Gets popular music from a specific decade:
- `1980s`, `1990s`, `2000s`, `2010s`, `2020s`

```
!decade 2000s
!decade 1990s
```

## Configuration

### Environment Variables

Add these to your `.env` file:

```env
# Spotify API credentials (optional)
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret

# Genius API token for lyrics (optional)
GENIUS_TOKEN=your_genius_token

# Music settings
MUSIC_CACHE_DIR=./music_cache
MAX_QUEUE_SIZE=500
ALLOW_EXPLICIT=true
```

### Spotify Setup

1. Go to https://developer.spotify.com/dashboard
2. Create a new application
3. Copy the Client ID and Client Secret
4. Add them to your `.env` file

### Genius Setup

1. Go to https://genius.com/api-clients
2. Create a new API Client
3. Copy the access token
4. Add it to your `.env` file

## Usage Examples

### Basic Playlist
```
!play Bohemian Rhapsody
!play Another One Bites the Dust
!play Stairway to Heaven
!queue
```

### Workout Session
```
!clearmood workout
!loop all
!volume 120
!skip
```

### Study Session
```
!clearmood focus
!volume 80
!loop all
```

### Party Mode
```
!clearmood party
!shuffle
!volume 150
!loop all
```

## Tips & Tricks

### Managing Queue
- Use `!queue 1`, `!queue 2`, etc. to navigate through large queues
- Use `!move` to reorder songs before they play
- Use `!shuffle` to randomize queue order

### Audio Quality
- Higher volume doesn't always sound better
- Use `!equalizer` to optimize for your music preference
- Adjust speed for workout music (faster) or focus (slower)

### Saving Music
- Use `!favorite` to save songs you love
- Create playlists with `!playlist create` for different moods
- Check `!history` to remember great songs

### Server Statistics
- Use `!stats` to see what your server likes
- Compete on the listening leaderboard
- Share your favorite songs with friends

## Troubleshooting

### Song Won't Play
- Make sure the bot is in a voice channel
- Check that you're in a voice channel
- Try searching with different keywords

### Audio Issues
- Adjust volume with `!volume`
- Try different equalizer presets
- Check your internet connection

### Queue Problems
- Use `!clear` to reset the queue
- Use `!remove` to delete specific songs
- Use `!shuffle` to reorganize songs

## Permissions

### Required Permissions
- Read Messages/View Channels
- Send Messages
- Embed Links
- Read Message History

### Voice Permissions
- Connect
- Speak
- Use Voice Activity

## Performance

- Supports queues up to 500 songs
- Handles large playlists efficiently
- Low memory footprint with intelligent caching
- Automatic reconnection on network issues

## Future Enhancements

Upcoming features in development:
- Apple Music integration
- Deezer integration
- BandCamp support
- Vimeo support
- Twitch VOD playback
- Podcast support
- Advanced recommendation engine
- Collaborative playlists with sharing
- Music taste profile analysis

## Support

For issues or feature requests, please contact the bot administrator or check the support documentation.

## License

This music cog is part of the Multipurpose Discord Bot project.
