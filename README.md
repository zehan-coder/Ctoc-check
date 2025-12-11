# Multipurpose Discord Bot with Advanced Ticketing System

A feature-rich Discord bot built with Discord.py, featuring utility, fun, moderation, information, economy commands, and an **advanced integrated ticketing system**.

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

### 🎫 Advanced Ticketing System
- **Ticket Creation**: Users can create tickets via commands or interactive panels
- **Ticket Management**: Create, assign, claim, and close tickets
- **Status Tracking**: Open, In-Progress, Closed, Resolved, Awaiting Response
- **Priority Levels**: Low, Medium, High, Urgent
- **Private Channels**: Automatic private ticket channels with role-based access
- **Notes/Comments**: Add timestamped notes and comments to tickets
- **Satisfaction Ratings**: Users can rate tickets after resolution (1-5 stars)
- **Transcripts**: Automatic transcript saving when tickets are closed
- **Statistics**: Dashboard showing ticket stats and metrics
- **Auto-closing**: Automatic closure of inactive tickets (configurable)
- **Ticket Panels**: Interactive embed-based panels for ticket creation
- **Ticket Search**: View your ticket history and status

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
   - Enable these Intents:
     - Message Content Intent
     - Members Intent

3. **Configure Environment**
   - Copy `.env.example` to `.env`
   - Edit `.env` and add your bot token:
     ```
     DISCORD_TOKEN=your_bot_token_here
     BOT_PREFIX=!
     SUPPORT_ROLE_ID=your_support_role_id_here  # Optional
     TICKET_CATEGORY_ID=your_ticket_category_id  # Optional
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
| `DATABASE_URL` | Database connection string | `sqlite:///tickets.db` |
| `ADMIN_USER_IDS` | Comma-separated admin user IDs | Optional |
| `ERROR_LOG_CHANNEL_ID` | Channel ID for error logging | Optional |
| `SUPPORT_ROLE_ID` | Support staff role for ticket permissions | Optional |
| `TICKET_CATEGORY_ID` | Category ID where ticket channels are created | Optional |
| `TICKET_AUTO_CLOSE_DAYS` | Days before auto-closing inactive tickets | `7` |
| `TICKET_ALERT_CHANNEL_ID` | Channel for admin ticket alerts | Optional |

## File Structure

```
discord-bot-multipurpose/
├── bot.py                      # Main bot file
├── ticket_database.py          # Ticket database management
├── cogs/                       # Command categories
│   ├── utility.py             # Utility commands
│   ├── fun.py                 # Fun commands
│   ├── moderation.py          # Moderation commands
│   ├── information.py         # Information commands
│   ├── economy.py             # Economy & leveling
│   └── ticketing.py           # Advanced ticketing system
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
├── .gitignore                # Git ignore rules
├── tickets.db                # SQLite database (auto-created)
├── bot.log                   # Bot logs (auto-created)
└── README.md                 # This file
```

## Basic Commands

### Get Started
```
!help          # Show all commands
!ping          # Check bot latency
!info          # Bot information
```

### Ticketing System

#### User Commands
```
!ticket [category] <title>     # Create a new ticket
!tickets                       # View your tickets
!ticket-info <ticket_number>   # Get ticket details
!ticket-note <ticket_number> <note>  # Add a note to ticket
!panel-create                  # Create ticket creation panel (staff only)
```

#### Staff Commands
```
!ticket-claim <ticket_number>  # Claim a ticket
!ticket-assign <ticket_number> <@member>  # Assign ticket to staff
!ticket-close <ticket_number> [reason]  # Close a ticket
!ticket-reopen <ticket_number> [reason]  # Reopen a closed ticket
!ticket-status <ticket_number> <status>  # Change ticket status
!ticket-stats                  # View ticket statistics
```

#### Ticket Categories
- `support` - Support requests (🆘)
- `bug` - Bug reports (🐛)
- `feature` - Feature requests (⭐)
- `general` - General inquiries (💬)
- `billing` - Billing questions (💳)

#### Ticket Statuses
- `open` - Newly created, awaiting staff
- `in-progress` - Being worked on
- `awaiting-response` - Waiting for user feedback
- `resolved` - Issue resolved
- `closed` - Ticket closed

#### Ticket Priority
- `low` - Non-urgent
- `medium` - Standard priority
- `high` - Urgent
- `urgent` - Critical

### Fun Commands
```
!joke          # Tell a random joke
!8ball <question>  # Ask the magic 8ball
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

## Ticketing System Guide

### For Users

1. **Create a Ticket**
   - Option A: Use command: `!ticket support My issue title`
   - Option B: Click a category button on a ticket panel

2. **Track Your Ticket**
   - Use `!tickets` to see all your tickets
   - Use `!ticket-info TK-123456-0001` to see detailed info

3. **Add Notes**
   - Use `!ticket-note TK-123456-0001 My question here`
   - Or click "Add Note" button in ticket channel

4. **Rate the Service**
   - After ticket is closed, rate your satisfaction (1-5 stars)

### For Staff/Admins

1. **Manage Tickets**
   - Claim tickets: `!ticket-claim TK-123456-0001`
   - Assign tickets: `!ticket-assign TK-123456-0001 @staff_member`
   - Change status: `!ticket-status TK-123456-0001 in-progress`

2. **Close Tickets**
   - `!ticket-close TK-123456-0001 Issue resolved`
   - Automatic transcript is saved

3. **Reopen if Needed**
   - `!ticket-reopen TK-123456-0001 Additional info needed`

4. **View Statistics**
   - `!ticket-stats` to see overall statistics
   - Includes open tickets, average resolution time, satisfaction ratings

### Ticket Lifecycle

1. **Creation** → User creates ticket with category, title, and description
2. **Assignment** → Staff claims or is assigned to the ticket
3. **Work** → Notes and comments are added as work progresses
4. **Resolution** → Status changes to "Resolved" or ticket is closed
5. **Feedback** → User rates satisfaction (1-5 stars)
6. **Archive** → Transcript is saved, channel can be archived

## Permissions

### Bot Permissions Required
- Send Messages
- Read Message History
- Embed Links
- Manage Channels (for creating ticket channels)
- Manage Roles (for setting channel permissions)
- Kick Members (for kick command)
- Ban Members (for ban command)
- Manage Messages (for clear command)

### User Permissions
- `!kick`, `!ban`, `!warn`: Requires Kick Members permission
- `!clear`: Requires Manage Messages permission
- `!ticket-claim`, `!ticket-assign`, `!ticket-close`: Requires Manage Messages permission
- `!ticket-create`, `!ticket-note`: Available to all users
- All other commands are available to all users

## Database

### SQLite Tables
- **tickets** - Main ticket information
- **ticket_notes** - Comments and notes on tickets
- **ticket_claims** - Staff claims on tickets
- **ticket_transcripts** - Saved conversation history
- **ticket_ratings** - User satisfaction ratings
- **user_profiles** - User statistics

The database is automatically created on first run and persists across bot restarts.

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
- All ticket operations with timestamps
- Database operations

Logs are saved to `bot.log` and displayed in console with timestamps and severity levels.

## Troubleshooting

### Common Issues

1. **Bot won't connect**
   - Check if bot token is correct in `.env`
   - Ensure bot has proper permissions in Discord server
   - Verify bot has Message Content Intent enabled

2. **Commands not working**
   - Verify bot has necessary permissions
   - Check if command prefix is correct (default: `!`)
   - Ensure bot has Read Message History permission

3. **Ticket channels not created**
   - Bot needs "Manage Channels" permission
   - Bot needs "Manage Roles" permission
   - Verify the ticket category ID is correct (if using custom category)

4. **Permission errors**
   - Bot needs proper permissions in server settings
   - Staff needs "Manage Messages" permission for ticket commands
   - Users need appropriate roles for certain commands

5. **Database errors**
   - Ensure `tickets.db` file is writable
   - Check that SQLite is properly installed
   - Verify file permissions in bot directory

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

### Extending the Ticketing System

The ticketing system can be extended by:
1. Adding new ticket categories in `TicketingCog.CATEGORIES`
2. Adding new statuses in `TicketingCog.STATUSES`
3. Modifying the database schema in `ticket_database.py`
4. Adding new views/modals for UI enhancements

## Support

For issues, suggestions, or contributions, please refer to the project's GitHub repository.

## License

This project is provided as-is for educational and personal use.
