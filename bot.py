"""
Multipurpose Discord Bot - Main Application
A comprehensive Discord bot with utility, fun, moderation, and information commands.
"""

import asyncio
import logging
import os
from datetime import datetime
from typing import Optional

import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class MultipurposeBot(commands.Bot):
    """Main bot class with custom functionality."""
    
    def __init__(self):
        # Define intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(
            command_prefix=self.get_prefix,
            intents=intents,
            case_insensitive=True,
            help_command=None
        )
        
        # Configuration
        self.token = os.getenv('DISCORD_TOKEN')
        self.prefix = os.getenv('BOT_PREFIX', '!')
        self.admin_ids = [int(id_str) for id_str in os.getenv('ADMIN_USER_IDS', '').split(',') if id_str.strip()]
        self.error_log_channel = os.getenv('ERROR_LOG_CHANNEL_ID')
        
        # Error handling
        self.logger = logger
        
    async def get_prefix(self, message):
        """Get the bot prefix."""
        if not self.is_ready():
            return self.prefix
        return commands.when_mentioned_or(self.prefix)(message)
    
    async def setup_hook(self):
        """Setup hook called when bot is starting."""
        self.logger.info("Setting up bot...")
        
        # Load extensions (cogs)
        await self.load_extensions()
        
        # Sync slash commands
        try:
            synced = await self.tree.sync()
            self.logger.info(f"Synced {len(synced)} slash command(s)")
        except Exception as e:
            self.logger.error(f"Failed to sync slash commands: {e}")
    
    async def load_extensions(self):
        """Load all bot extensions."""
        extensions = [
            'cogs.utility',
            'cogs.fun',
            'cogs.moderation',
            'cogs.information',
            'cogs.economy',
            'cogs.ticketing',
            'cogs.giveaway',
            'cogs.logging',
            'cogs.music'
        ]
        
        for extension in extensions:
            try:
                await self.load_extension(extension)
                self.logger.info(f"Loaded extension: {extension}")
            except Exception as e:
                self.logger.error(f"Failed to load extension {extension}: {e}")
    
    async def on_ready(self):
        """Called when bot is ready."""
        self.logger.info(f'{self.user} has connected to Discord!')
        
        # Set bot status
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{self.prefix}help | {len(self.guilds)} servers"
        )
        await self.change_presence(activity=activity)
        
        # Log guild information
        for guild in self.guilds:
            self.logger.info(f'Connected to guild: {guild.name} (ID: {guild.id})')
    
    async def on_guild_join(self, guild):
        """Called when bot joins a new guild."""
        self.logger.info(f"Joined new guild: {guild.name} (ID: {guild.id})")
        
        # Send welcome message if possible
        try:
            channel = guild.system_channel
            if channel and channel.permissions_for(guild.me).send_messages:
                embed = discord.Embed(
                    title="Hello! I'm your new multipurpose bot!",
                    description=f"Thanks for adding me to {guild.name}!",
                    color=0x00ff00
                )
                embed.add_field(
                    name="Quick Start",
                    value=f"Use {self.prefix}help to see all available commands!",
                    inline=False
                )
                await channel.send(embed=embed)
        except Exception as e:
            self.logger.error(f"Failed to send welcome message to {guild.name}: {e}")
    
    async def on_message(self, message):
        """Handle incoming messages."""
        # Don't process messages from bots
        if message.author.bot:
            return
        
        # Process commands
        await self.process_commands(message)
    
    async def on_command_error(self, ctx, error):
        """Handle command errors."""
        # Get original error
        error = getattr(error, 'original', error)
        
        # Log error
        self.logger.error(f"Command error in {ctx.command}: {error}")
        
        # Send error message to user
        if isinstance(error, commands.CommandNotFound):
            return  # Don't respond to unknown commands
        
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to use this command!")
        
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("I don't have permission to perform this action!")
        
        elif isinstance(error, commands.BadArgument):
            await ctx.send("Invalid arguments provided. Check the command help!")
        
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"Command on cooldown. Try again in {error.retry_after:.1f}s")
        
        else:
            await ctx.send("An unexpected error occurred. Please try again later.")
            
            # Log to error channel if configured
            if self.error_log_channel:
                try:
                    channel = self.get_channel(int(self.error_log_channel))
                    if channel:
                        embed = discord.Embed(
                            title="Bot Error",
                            color=0xff0000
                        )
                        embed.add_field(name="Command", value=ctx.command, inline=True)
                        embed.add_field(name="User", value=f"{ctx.author} ({ctx.author.id})", inline=True)
                        embed.add_field(name="Guild", value=f"{ctx.guild} ({ctx.guild.id})", inline=True)
                        embed.add_field(name="Error", value=str(error), inline=False)
                        embed.timestamp = datetime.utcnow()
                        await channel.send(embed=embed)
                except Exception as e:
                    self.logger.error(f"Failed to log error to channel: {e}")
    
    def is_admin(self, user: discord.User) -> bool:
        """Check if user is a bot admin."""
        return user.id in self.admin_ids
    
    async def close(self):
        """Close the bot connection."""
        self.logger.info("Shutting down bot...")
        await super().close()


async def main():
    """Main function to run the bot."""
    bot = MultipurposeBot()
    
    if not bot.token:
        logger.error("No Discord token found in environment variables!")
        return
    
    try:
        await bot.start(bot.token)
    except discord.LoginFailure:
        logger.error("Invalid Discord token provided!")
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
    finally:
        await bot.close()


if __name__ == '__main__':
    asyncio.run(main())