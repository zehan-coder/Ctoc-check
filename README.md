# Multipurpose Discord Bot with Advanced Features

A feature-rich Discord bot built with Discord.py, featuring utility, fun, moderation, information, economy commands, plus **advanced ticketing system**, **comprehensive giveaway system**, and **enterprise-grade logging**.

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

### 🎁 Advanced Giveaway System
- **Customizable Giveaways**: Duration, prizes, winner count
- **Multiple Entry Methods**: Reactions, buttons, command-based
- **Role-Based Eligibility**: Require or exclude specific roles
- **Account Age Requirements**: Minimum account creation time
- **Server Membership Filters**: Minimum time in server
- **Whitelist/Blacklist**: Control who can win
- **Multi-Prize Giveaways**: Different prizes for each winner
- **Fair Winner Selection**: Weighted random selection with entry count
- **Winner Notifications**: Automatic DMs to winners
- **Giveaway Reminders**: Notifications at 1 hour and 10 minutes before end
- **Pause/Resume**: Temporarily pause active giveaways
- **Reroll Functionality**: Select new winners
- **Giveaway History**: Track past giveaways and results
- **Templates**: Save and reuse giveaway configurations

### 📊 Enterprise-Grade Logging System
- **Message Logging**: Deleted, edited, bulk deleted messages
- **Member Logging**: Joins, leaves, bans, kicks, role changes
- **Channel Logging**: Creation, deletion, updates
- **Role Logging**: Creation, deletion, permission changes
- **Server Logging**: Settings changes, webhooks, integrations
- **Command Logging**: All command executions with arguments
- **User Activity Timeline**: Complete activity history per user
- **Searchable Logs**: Filter by type, user, action, date range
- **Export Functionality**: Export logs to JSON/CSV formats
- **Log Retention**: Automatic cleanup of old logs
- **Statistics Dashboard**: Log statistics and trends
- **Suspicious Activity Detection**: Pattern detection for spam/raids
- **Audit Trail**: Full accountability with moderator tracking

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
├── database_manager.py         # Giveaway & logging database
├── cogs/                       # Command categories
│   ├── utility.py             # Utility commands
│   ├── fun.py                 # Fun commands
│   ├── moderation.py          # Moderation commands
│   ├── information.py         # Information commands
│   ├── economy.py             # Economy & leveling
│   ├── ticketing.py           # Advanced ticketing system
│   ├── giveaway.py            # Advanced giveaway system
│   └── logging.py             # Enterprise logging system
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
├── .gitignore                # Git ignore rules
├── tickets.db                # Ticketing database (auto-created)
├── advanced.db               # Giveaway & logging database (auto-created)
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

### Giveaway Commands (Admin Only)
```
!giveaway start <minutes> [winners] <title>  # Start a new giveaway
!giveaway list                               # List active giveaways
!giveaway end <giveaway_id>                 # End giveaway early
!giveaway reroll <giveaway_id>              # Reroll winner(s)
!giveaway results <giveaway_id>             # View giveaway results
```

### Logging Commands (Admin Only)
```
!logs config [channel]      # Configure logging channel
!logs search [type] [limit] # Search logs (types: all, message, member, channel, command, server)
!logs user @user [limit]    # View user activity
!logs stats                 # View logging statistics
!logs export [format]       # Export logs (json or csv)
!logs dashboard             # View activity dashboard
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

## Giveaway System Guide

### Quick Start
1. **Start Giveaway**: `!giveaway start 30 1 Amazing Prize` (30 minutes, 1 winner)
2. **Users Enter**: Click the "Enter Giveaway" button
3. **Giveaway Ends**: Automatically after duration expires
4. **Winners Announced**: Posted in channel and DM'd

### Advanced Features
- **Role Requirements**: Require specific roles to participate
- **Account Age**: Users must have account older than X days
- **Server Membership**: Users must be in server for X days
- **Blacklist/Whitelist**: Control who can win
- **Multiple Winners**: Each winner gets their own prize
- **Reroll**: Select different winners from existing entries

### Giveaway Management
- Active giveaways are automatically tracked
- Winners are selected fairly with weighted random (more entries = higher chance)
- Past giveaway results are stored indefinitely
- Giveaways can be ended early if needed

## Logging System Guide

### Log Types
- **message** - Message deletions, edits, bulk deletions
- **member** - Member joins, leaves, bans, kicks
- **channel** - Channel creation, deletion, updates
- **server** - Role changes, server settings
- **command** - Command executions
- **mod** - Moderation actions

### Setup Logging
1. **Configure Log Channel**: `!logs config #logging`
2. **System Starts Recording**: All events logged automatically
3. **View Logs**: Use search and filter commands
4. **Export Data**: Export for external analysis

### Log Features
- **User Activity**: See all actions by a specific user
- **Search & Filter**: Find specific events
- **Statistics**: Get insights into server activity
- **Export**: Download logs as JSON or CSV
- **Auto-Cleanup**: Old logs automatically deleted based on retention

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
- View Audit Log (for logging moderation actions)

### User Permissions
- `!kick`, `!ban`, `!warn`: Requires Kick Members permission
- `!clear`: Requires Manage Messages permission
- `!ticket-claim`, `!ticket-assign`, `!ticket-close`: Requires Manage Messages permission
- `!ticket-create`, `!ticket-note`: Available to all users
- `!giveaway *`: Requires Administrator permission
- `!logs *`: Requires Administrator permission
- All other commands are available to all users

## Database

### Ticket Database (tickets.db)
- **tickets** - Main ticket information
- **ticket_notes** - Comments and notes on tickets
- **ticket_claims** - Staff claims on tickets
- **ticket_transcripts** - Saved conversation history
- **ticket_ratings** - User satisfaction ratings
- **user_profiles** - User statistics

### Advanced Database (advanced.db)
- **giveaways** - Active and completed giveaways
- **giveaway_entries** - User entries in giveaways
- **giveaway_winners** - Giveaway winners and results
- **giveaway_templates** - Saved giveaway templates
- **logs** - Complete server event logs
  - Indexed for fast searching
  - Includes automatic expiration for old logs

Both databases are automatically created on first run and persist across bot restarts.

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
