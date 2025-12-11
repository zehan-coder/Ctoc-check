# Multipurpose Discord Bot

A feature-rich Discord bot built with Discord.py, featuring utility, fun, moderation, information, and economy commands.

## Features

### 🛠️ Utility Commands
- `!ping` - Check bot latency
- `!help` - Show command help
- `!info` - Bot information
- `!avatar` - Get user's avatar

### 🎮 Fun Commands
- `!joke` - Random jokes
- `!8ball` - Magic 8ball responses
- `!coinflip` - Flip a coin

### 🛡️ Moderation Commands
- `!kick` - Kick users
- `!ban` - Ban users
- `!warn` - Warning system
- `!clear` - Clear messages

### 📊 Information Commands
- `!serverinfo` - Detailed server information
- `!userinfo` - User profile information

### 💰 Economy & Leveling
- `!profile` - View profile and stats
- `!daily` - Daily coin reward
- `!transfer` - Send coins to users

## Installation

### Prerequisites
- Python 3.8 or higher
- Discord account and bot token

### Setup Steps

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create a Discord Bot**
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Create a new application
   - Go to the "Bot" section
   - Click "Add Bot"
   - Copy the bot token

3. **Configure Environment**
   - Copy `.env.example` to `.env`
   - Edit `.env` and add your bot token:
     ```
     DISCORD_TOKEN=your_bot_token_here
     BOT_PREFIX=!
     ```

4. **Run the Bot**
   ```bash
   python bot.py
   ```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DISCORD_TOKEN` | Your Discord bot token | Required |
| `BOT_PREFIX` | Command prefix for text commands | `!` |
| `DATABASE_URL` | Database connection string | `sqlite:///bot.db` |
| `ADMIN_USER_IDS` | Comma-separated admin user IDs | Optional |
| `ERROR_LOG_CHANNEL_ID` | Channel ID for error logging | Optional |

## File Structure

```
discord-bot-multipurpose/
├── bot.py                  # Main bot file
├── cogs/                   # Command categories
│   ├── utility.py         # Utility commands
│   ├── fun.py             # Fun commands
│   ├── moderation.py      # Moderation commands
│   ├── information.py     # Information commands
│   └── economy.py         # Economy & leveling
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## Basic Commands

### Get Started
```
!help          # Show all commands
!ping          # Check bot latency
!info          # Bot information
```

### Fun Commands
```
!joke          # Tell a random joke
!8ball Will I have a good day?  # Ask the magic 8ball
!coinflip      # Flip a coin
```

### Server Information
```
!serverinfo    # Server details
!userinfo      # Your profile info
!avatar        # Get someone's avatar
```

### Moderation
```
!kick @user    # Kick a user (requires permissions)
!ban @user     # Ban a user (requires permissions)
!warn @user    # Warn a user (requires permissions)
!clear 10      # Clear 10 messages (requires permissions)
```

### Economy System
```
!profile       # Check your stats
!daily         # Claim daily coins
!transfer @user 100  # Send 100 coins
```

## Permissions

### Bot Permissions Required
- Send Messages
- Read Message History
- Embed Links
- Kick Members (for kick command)
- Ban Members (for ban command)
- Manage Messages (for clear command)

### User Permissions
- `!kick`, `!ban`, `!warn`: Requires Kick Members permission
- `!clear`: Requires Manage Messages permission
- All other commands are available to all users

## Economy System

### Earning Coins
- **Daily Reward**: 100 coins every 24 hours
- **Transfers**: Receive coins from other users
- **Starting Balance**: 1,000 coins

### Commands
- `!profile` - View your balance, level, and stats
- `!daily` - Claim daily reward (24h cooldown)
- `!transfer @user amount` - Send coins to other users

## Logging

The bot logs various events:
- Bot startup and connection status
- Command usage and errors
- Guild joins and leaves
- Moderation actions

Logs are saved to `bot.log` and displayed in console.

## Troubleshooting

### Common Issues

1. **Bot won't connect**
   - Check if bot token is correct in `.env`
   - Ensure bot has proper permissions in Discord server

2. **Commands not working**
   - Verify bot has necessary permissions
   - Check if command prefix is correct (default: `!`)

3. **Permission errors**
   - Bot needs proper permissions in server settings
   - Users need appropriate roles for certain commands

## Development

### Adding New Commands

1. Create a new cog file in `cogs/`
2. Define commands using `@commands.hybrid_command()`
3. Add the cog to the load list in `bot.py`
4. Follow existing code patterns and conventions

### Code Style
- Use type hints where appropriate
- Follow PEP 8 guidelines
- Add error handling for all commands
- Use async/await properly
- Include docstrings for functions and classes