# Advanced Music Cog - Testing Guide

## Unit Testing

### Test Song Class
```python
from cogs.music import Song
import discord

# Create test song
song = Song(
    title="Test Song",
    url="https://example.com/song.mp3",
    duration=180,
    requester=user_object,
    source="youtube",
    thumbnail="https://example.com/thumb.jpg",
    artist="Test Artist"
)

assert song.title == "Test Song"
assert song.duration == 180
assert song.source == "youtube"
```

### Test MusicPlayer Class
```python
from cogs.music import MusicPlayer, Song

player = MusicPlayer(guild_id=123456789)

# Test queue operations
song = Song("Test", "url", 180, requester, "youtube")
player.add_to_queue(song)
assert len(player.queue) == 1

# Test removing
removed = player.remove_from_queue(0)
assert len(player.queue) == 0
assert removed.title == "Test"

# Test shuffle
player.add_to_queue(song)
player.add_to_queue(song)
player.shuffle_queue()

# Test loop modes
player.loop_mode = "one"
assert player.loop_mode == "one"
```

## Integration Testing

### Test Music Commands

#### 1. Play Command
```
Setup:
1. Join voice channel
2. Run: !play "Never Gonna Give You Up"

Expected:
- Song added to queue
- Embed message shows song title
- Bot joins voice channel
- Song plays
```

#### 2. Queue Command
```
Setup:
1. Add 15 songs to queue
2. Run: !queue 1
3. Run: !queue 2

Expected:
- Page 1 shows songs 1-10
- Page 2 shows songs 11-15
- Queue stats show correct totals
```

#### 3. Now Playing
```
Setup:
1. Play a song
2. Run: !nowplaying

Expected:
- Shows current song title
- Shows duration and progress
- Shows requester
- Shows thumbnail image
```

#### 4. Volume Control
```
Setup:
Run: !volume 50
Run: !volume 150
Run: !volume 200

Expected:
- Volume updates successfully
- Volume bar displays correctly
- Values clamp to 0-200
```

#### 5. Loop Modes
```
Setup:
Run: !loop one
Run: !loop all
Run: !loop none

Expected:
- Loop mode changes
- Correct emoji shows
- Loop behavior works correctly
```

#### 6. Shuffle
```
Setup:
1. Add 10 songs in order
2. Run: !shuffle
3. Run: !queue

Expected:
- Queue order changes
- All songs remain in queue
- No songs duplicated
```

#### 7. Seek
```
Setup:
1. Play 3-minute song
2. Run: !seek 1 30

Expected:
- Seeks to 1:30 mark
- Progress updates
- Song continues from new position
```

#### 8. Skip
```
Setup:
1. Add multiple songs
2. Run: !skip

Expected:
- Current song stops
- Next song plays
- Skip message shows
```

#### 9. Favorite
```
Setup:
1. Play a song
2. Run: !favorite
3. Run: !favorite again

Expected:
- First: Song added to favorites
- Second: Error "already in favorites"
```

#### 10. History
```
Setup:
1. Play 5 songs
2. Run: !history

Expected:
- Shows recent songs
- Lists in reverse order
- Includes timestamps
```

#### 11. Playlist Operations
```
Create Playlist:
1. Add 5 songs to queue
2. Run: !playlist create "Test List"

Load Playlist:
1. Clear queue
2. Run: !playlist load "Test List"

Expected:
- Playlist created with correct songs
- Songs loaded back into queue
- List command shows the playlist
```

#### 12. Mood Playlists
```
Setup:
Run: !clearmood chill
Run: !clearmood energetic

Expected:
- Shows mood description
- Lists recommended keywords
- Provides search suggestions
```

#### 13. Decade Playlists
```
Setup:
Run: !decade 1980s
Run: !decade 2000s

Expected:
- Shows decade info
- Lists popular songs from era
- Provides search suggestions
```

#### 14. Equalizer
```
Setup:
Run: !equalizer bass_boost
Run: !equalizer pop
Run: !equalizer flat

Expected:
- EQ preset changes
- Description updates
- Audio characteristics change
```

#### 15. Speed Control
```
Setup:
Run: !speed 1.5
Run: !speed 0.8
Run: !speed 1.0

Expected:
- Speed multiplier updates
- Song plays at correct speed
- Speed bar shows percentage
```

#### 16. Special Effects
```
Nightcore:
Run: !nightcore
Expected: Speed increases to 1.25x

Slowed:
Run: !slowed
Expected: Speed decreases to 0.8x
```

## Performance Testing

### Queue Performance
```python
# Test with large queue
import time
from cogs.music import MusicPlayer

player = MusicPlayer(123456789)

start = time.time()
for i in range(500):
    song = Song(f"Song {i}", f"url_{i}", 180, requester, "youtube")
    player.add_to_queue(song)
elapsed = time.time() - start

print(f"Added 500 songs in {elapsed:.2f}s")  # Should be < 1 second
```

### Memory Usage
```python
import tracemalloc
from cogs.music import MusicPlayer

tracemalloc.start()

player = MusicPlayer(123456789)
for i in range(1000):
    song = Song(f"Song {i}", f"url_{i}", 180, requester, "youtube")
    player.add_to_queue(song)

current, peak = tracemalloc.get_traced_memory()
print(f"Current: {current / 1024 / 1024:.2f} MB")
print(f"Peak: {peak / 1024 / 1024:.2f} MB")

tracemalloc.stop()
```

## Stress Testing

### Multiple Guilds
```python
from cogs.music import MusicCog
import asyncio

cog = MusicCog(bot)

async def test_multiple_guilds():
    # Test with 100 guilds playing music
    for guild_id in range(1, 101):
        player = cog.get_player(guild_id)
        song = Song("Test", "url", 180, requester, "youtube")
        player.add_to_queue(song)
    
    print(f"Players created: {len(cog.players)}")

asyncio.run(test_multiple_guilds())
```

### Concurrent Operations
```python
import asyncio
from cogs.music import MusicCog

async def test_concurrent_plays():
    cog = MusicCog(bot)
    
    tasks = []
    for i in range(10):
        task = cog.play(ctx, query=f"song_{i}")
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    print(f"Concurrent plays completed: {len([r for r in results if r])}")

asyncio.run(test_concurrent_plays())
```

## User Acceptance Testing

### Beginner User Workflow
```
1. User joins voice channel
2. User types: !play "favorite song"
3. User checks: !nowplaying
4. User adjusts: !volume 80
5. User skips: !skip
6. User stops: !stop
```

### Advanced User Workflow
```
1. User creates playlist: !playlist create "Workout"
2. User adds multiple songs
3. User adjusts EQ: !equalizer pop
4. User sets speed: !speed 1.2
5. User enables effect: !nightcore
6. User checks stats: !stats
7. User saves playlist: !playlist save "Workout"
```

### Admin Workflow
```
1. Admin views server stats: !stats
2. Admin checks listening patterns
3. Admin manages permissions
4. Admin configures settings
5. Admin monitors usage
```

## Error Handling Tests

### Test Invalid Inputs
```
!volume 250        # Should fail (> 200)
!volume -10        # Should fail (< 0)
!seek 999 999      # Should fail (exceeds duration)
!remove 999        # Should fail (invalid position)
!move 1 999        # Should fail (invalid position)
```

### Test Missing State
```
!pause            # No song playing
!resume           # No paused song
!skip             # Empty queue
!nowplaying       # No current song
!favorite         # No current song
```

### Test Permission Issues
```
# Without connect permission
!play "song"      # Should fail to connect

# Without speak permission
!play "song"      # Should fail to play
```

## API Integration Tests

### YouTube Search
```python
async def test_youtube_search():
    from cogs.music import SearchManager
    
    manager = SearchManager()
    results = await manager.search_youtube("Never Gonna Give You Up", max_results=5)
    
    assert len(results) > 0
    assert 'title' in results[0]
    assert 'url' in results[0]
    assert 'youtube' in results[0]['url']
```

### Spotify Integration
```python
async def test_spotify_search():
    from cogs.music import SearchManager
    
    manager = SearchManager()
    results = await manager.search_spotify("Bohemian Rhapsody", max_results=5)
    
    assert len(results) > 0
    assert 'title' in results[0]
    assert 'spotify' in results[0]['source']
```

## Regression Testing

### After Updates
```
1. Test all core commands (!play, !pause, !skip, !stop)
2. Test queue operations (!queue, !remove, !move)
3. Test effects (!equalizer, !nightcore, !speed)
4. Test playlists (!playlist create, load, list)
5. Test statistics (!stats, !history)
6. Check no breaking changes
```

## Browser/UI Testing (Discord)

### Rich Embeds Display
- [ ] Now playing embed displays correctly
- [ ] Colors are consistent
- [ ] Thumbnails load properly
- [ ] Progress bar renders correctly
- [ ] All fields visible on mobile

### Command Response
- [ ] Success messages show properly
- [ ] Error messages are clear
- [ ] Pagination works
- [ ] Emojis display correctly

## Load Testing

### Simulated Users
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def simulate_user_session(user_id):
    """Simulate a user session"""
    # Play songs, check queue, adjust settings
    # Run for 5 minutes with 50 concurrent users
    
async def load_test():
    users = [simulate_user_session(i) for i in range(50)]
    await asyncio.gather(*users)

asyncio.run(load_test())
```

## Accessibility Testing

### Screen Reader Compatibility
- [ ] Command help is clear
- [ ] Embed messages have descriptions
- [ ] Error messages are descriptive

### Mobile Discord Client
- [ ] Commands work from mobile
- [ ] Embeds display correctly
- [ ] Buttons are clickable

## Documentation Testing

### Command Examples
```
Test each example in MUSIC_GUIDE.md to ensure they work
```

### Setup Instructions
```
Follow MUSIC_SETUP.md step-by-step on clean system
```

## Test Report Template

```markdown
## Test Report - [Date]

### Environment
- Bot Version: [x.x.x]
- Discord.py Version: [x.x.x]
- Python Version: [x.x.x]

### Tests Passed: ✓ X/Y

### Issues Found
1. [Issue Title]
   - Severity: [Low/Medium/High]
   - Steps: [Reproduction steps]
   - Expected: [Expected behavior]
   - Actual: [Actual behavior]

### Recommendations
- [Recommendation 1]
- [Recommendation 2]

### Sign-off
Tested by: [Name]
Date: [Date]
Status: [Pass/Fail/Conditional]
```

## Continuous Integration

### Automated Tests
```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_music.py

# Run with coverage
python -m pytest --cov=cogs.music
```

### Pre-commit Hooks
```bash
# Check syntax
python -m py_compile cogs/music.py

# Check imports
python -c "import cogs.music"

# Run linting
pylint cogs/music.py
```
