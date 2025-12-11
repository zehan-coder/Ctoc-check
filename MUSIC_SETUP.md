# Advanced Music Cog - Setup and Configuration Guide

## Quick Start

### Prerequisites
- Python 3.8+
- Discord bot with voice permissions
- (Optional) Spotify API credentials
- (Optional) Genius API token

### Installation

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

This installs:
- `discord.py` - Discord bot framework
- `yt-dlp` - YouTube audio extraction
- `youtube-search-python` - YouTube search functionality
- `spotipy` - Spotify API integration
- `lyricsgenius` - Lyrics fetching
- `requests` - HTTP library
- `Pillow` - Image processing

2. **Configure environment variables**:

Create or update your `.env` file:

```env
# Basic Discord Configuration
DISCORD_TOKEN=your_bot_token_here
BOT_PREFIX=!

# Music Configuration (Optional)
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
GENIUS_TOKEN=your_genius_token

# Music Settings
MUSIC_CACHE_DIR=./music_cache
MAX_QUEUE_SIZE=500
ALLOW_EXPLICIT=true
```

## Detailed Setup Instructions

### Step 1: Create Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to "Bot" section and create a bot
4. Copy the token and add it to your `.env` file as `DISCORD_TOKEN`
5. Go to OAuth2 > URL Generator
6. Select scopes: `bot`
7. Select permissions:
   - Read Messages/View Channels
   - Send Messages
   - Embed Links
   - Read Message History
   - Connect (voice)
   - Speak (voice)
   - Use Voice Activity

### Step 2: Spotify Integration (Optional)

To enable Spotify search and metadata:

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Log in or create an account
3. Create a new application
4. Accept the terms and create the app
5. Copy your **Client ID** and **Client Secret**
6. Add to `.env`:
   ```env
   SPOTIFY_CLIENT_ID=your_client_id_here
   SPOTIFY_CLIENT_SECRET=your_client_secret_here
   ```

### Step 3: Genius Lyrics (Optional)

To enable lyrics searching:

1. Go to [Genius API Clients](https://genius.com/api-clients)
2. Create a new API client
3. Generate an access token
4. Add to `.env`:
   ```env
   GENIUS_TOKEN=your_token_here
   ```

### Step 4: Bot Permissions

Ensure your bot has these permissions in your Discord server:

**Text Channel Permissions:**
- Send Messages
- Embed Links
- Read Message History

**Voice Channel Permissions:**
- Connect
- Speak
- Use Voice Activity

## Configuration Options

### Music Settings

Edit `.env` to customize:

```env
# Queue size limit (default: 500)
MAX_QUEUE_SIZE=500

# Audio quality preference
# Options: 96, 128, 192, 256, 320, flac, opus
DEFAULT_QUALITY=320

# Allow/block explicit content
ALLOW_EXPLICIT=true

# Cache directory for audio files
MUSIC_CACHE_DIR=./music_cache
```

### Bot Settings

```env
# Command prefix (default: !)
BOT_PREFIX=!

# Admin user IDs (comma-separated)
ADMIN_USER_IDS=123456789,987654321

# Error logging channel
ERROR_LOG_CHANNEL_ID=123456789
```

## Database Setup

The music system stores:
- User favorites
- Playlists
- Listening history
- Statistics
- User preferences

This data persists locally and can be backed up.

## Verify Installation

Run this to test the bot:

```bash
python3 bot.py
```

You should see output like:
```
2024-01-01 12:00:00 - root - INFO - Setting up bot...
2024-01-01 12:00:01 - root - INFO - Loaded extension: cogs.music
2024-01-01 12:00:02 - root - INFO - Bot Token has connected to Discord!
```

## First Use

### 1. Join a Voice Channel
Connect to a voice channel in your Discord server.

### 2. Play Your First Song
```
!play Rick Roll Never Gonna Give You Up
```

### 3. Check the Queue
```
!queue
```

### 4. View Now Playing
```
!nowplaying
```

## Common Setup Issues

### Issue: "No module named 'discord'"
**Solution**: Install requirements
```bash
pip install -r requirements.txt
```

### Issue: "Bot can't connect to voice channel"
**Solution**: Check bot permissions
- Ensure bot has "Connect" and "Speak" permissions
- Check if the voice channel is full
- Verify bot isn't muted

### Issue: "Can't find song"
**Solution**: Try different search terms
- Be more specific with song/artist names
- Try just the artist name
- Check spelling

### Issue: Spotify search not working
**Solution**: Configure Spotify credentials
- Get Client ID and Secret from Spotify Developer
- Add to `.env` file
- Restart bot

### Issue: Lyrics not showing
**Solution**: Configure Genius token
- Create API client on Genius.com
- Get access token
- Add to `.env` file
- Restart bot

## Performance Tuning

### For Smaller Servers (< 1000 users)
```env
MAX_QUEUE_SIZE=500
DEFAULT_QUALITY=192
MUSIC_CACHE_DIR=./music_cache
```

### For Larger Servers (> 5000 users)
```env
MAX_QUEUE_SIZE=250
DEFAULT_QUALITY=128
MUSIC_CACHE_DIR=/var/cache/discord_music
```

### For Premium Networks
```env
MAX_QUEUE_SIZE=1000
DEFAULT_QUALITY=320
MUSIC_CACHE_DIR=/ssd/music_cache
```

## Security Best Practices

1. **Never commit `.env` file** - Add to `.gitignore`
2. **Use environment variables** - Don't hardcode credentials
3. **Limit admin IDs** - Only trusted users should have admin access
4. **Monitor bot activity** - Check logs regularly
5. **Disable explicit content** if needed:
   ```env
   ALLOW_EXPLICIT=false
   ```

## Backup and Restore

### Backup User Data
```bash
# Backup playlists and favorites
cp -r music_cache backup_$(date +%Y%m%d)
```

### Export Playlist
The bot automatically saves playlists that can be shared.

## Deployment

### Heroku Deployment
```bash
heroku create your-bot-name
heroku config:set DISCORD_TOKEN=your_token
git push heroku main
```

### Docker Deployment
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python3", "bot.py"]
```

### VPS Deployment
```bash
# Install Python
sudo apt-get install python3 python3-pip

# Install dependencies
pip3 install -r requirements.txt

# Run bot in background
nohup python3 bot.py > bot.log 2>&1 &
```

## Monitoring

### Check Bot Logs
```bash
tail -f bot.log
```

### Monitor Resource Usage
```bash
ps aux | grep bot.py
```

### Restart Bot
```bash
# Kill process
pkill -f bot.py

# Restart
python3 bot.py &
```

## Advanced Configuration

### Custom Aliases
Add custom command aliases in config file (future feature).

### Custom Equalizer Presets
Add your own EQ presets (future feature).

### Custom Playlist Templates
Create preset playlists for your server (future feature).

## Troubleshooting Commands

```bash
# Check Python version
python3 --version

# Verify modules installed
python3 -c "import discord; print(discord.__version__)"

# Test bot connection
python3 bot.py --test

# Check logs for errors
grep -i error bot.log
```

## Getting Help

1. **Check logs** - Look for error messages in bot.log
2. **Read documentation** - See MUSIC_GUIDE.md
3. **Discord Server** - Join support server for help
4. **GitHub Issues** - Report bugs on GitHub

## Next Steps

After setup:
1. Invite bot to your server
2. Configure permissions
3. Run first time setup
4. Start adding music features
5. Customize preferences
6. Share with your community

## Regular Maintenance

### Weekly
- Check bot is running
- Review logs for errors
- Monitor disk space

### Monthly
- Backup user data
- Update dependencies
- Review statistics

### Quarterly
- Update Python
- Security audit
- Performance review

## Updates

Check for updates:
```bash
git pull origin main
pip install -r requirements.txt
```

Restart bot after updates:
```bash
pkill -f bot.py
python3 bot.py &
```

## Support Resources

- [Discord.py Documentation](https://discordpy.readthedocs.io/)
- [Spotify API Documentation](https://developer.spotify.com/documentation/)
- [yt-dlp Documentation](https://github.com/yt-dlp/yt-dlp)
- [Genius API Documentation](https://docs.genius.com/)
