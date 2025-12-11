"""
Utility Commands for Discord Bot
Provides basic utility functions like ping, help, info, etc.
"""

import os
import platform
import time
from datetime import datetime
from typing import Optional

import discord
from discord.ext import commands


class UtilityCog(commands.Cog):
    """Utility commands for basic bot functionality."""
    
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()
    
    @commands.hybrid_command(name="ping", description="Check bot latency")
    async def ping(self, ctx):
        """Check the bot's latency."""
        latency = round(self.bot.latency * 1000)
        
        embed = discord.Embed(
            title="Pong!",
            color=0x00ff00
        )
        embed.add_field(name="Latency", value=f"{latency}ms", inline=True)
        embed.add_field(name="API Latency", value=f"{latency}ms", inline=True)
        embed.timestamp = datetime.utcnow()
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="help", description="Show help information")
    async def help_command(self, ctx, *, command: Optional[str] = None):
        """Show help information about commands."""
        if command:
            # Show help for specific command
            cmd = self.bot.get_command(command)
            if not cmd:
                await ctx.send(f"Command '{command}' not found.")
                return
            
            embed = discord.Embed(
                title=f"Command: {cmd.name}",
                description=cmd.description or "No description available.",
                color=0x7289da
            )
            
            # Add usage
            if cmd.usage:
                embed.add_field(name="Usage", value=f"`{ctx.prefix}{cmd.usage}`", inline=False)
            else:
                embed.add_field(name="Usage", value=f"`{ctx.prefix}{cmd.name}`", inline=False)
            
            # Add aliases
            if cmd.aliases:
                embed.add_field(name="Aliases", value=", ".join(f"`{alias}`" for alias in cmd.aliases), inline=False)
            
            await ctx.send(embed=embed)
        else:
            # Show general help
            embed = discord.Embed(
                title="Multipurpose Bot Help",
                description=f"Welcome to {ctx.guild.name}! Use the prefix `{ctx.prefix}` for commands.",
                color=0x7289da
            )
            
            # Add bot info
            uptime = datetime.utcnow() - datetime.fromtimestamp(self.start_time)
            uptime_str = str(uptime).split('.')[0]  # Remove microseconds
            
            embed.add_field(
                name="Bot Info",
                value=f"Uptime: {uptime_str}\n"
                      f"Servers: {len(self.bot.guilds)}\n"
                      f"Users: {len(self.bot.users)}",
                inline=True
            )
            
            # Add command categories
            categories = {}
            for cmd in self.bot.commands:
                if cmd.cog and not cmd.hidden:
                    category = cmd.cog.qualified_name
                    if category not in categories:
                        categories[category] = []
                    categories[category].append(cmd.name)
            
            for category, commands_list in categories.items():
                commands_str = ", ".join(f"`{cmd}`" for cmd in commands_list)
                embed.add_field(name=category, value=commands_str, inline=False)
            
            embed.set_footer(text="Use !help <command> for more info on a specific command.")
            await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="info", description="Show bot information")
    async def info_command(self, ctx):
        """Show detailed bot information."""
        uptime = datetime.utcnow() - datetime.fromtimestamp(self.start_time)
        uptime_str = str(uptime).split('.')[0]
        
        # Get system info
        python_version = platform.python_version()
        discord_py_version = discord.__version__
        
        embed = discord.Embed(
            title="Bot Information",
            color=0x7289da
        )
        
        embed.add_field(name="Bot Name", value=self.bot.user.name, inline=True)
        embed.add_field(name="Bot ID", value=self.bot.user.id, inline=True)
        embed.add_field(name="Prefix", value=f"`{ctx.prefix}`", inline=True)
        
        embed.add_field(name="Servers", value=str(len(self.bot.guilds)), inline=True)
        embed.add_field(name="Users", value=str(len(self.bot.users)), inline=True)
        embed.add_field(name="Channels", value=str(len(list(self.bot.get_all_channels()))), inline=True)
        
        embed.add_field(name="Uptime", value=uptime_str, inline=True)
        embed.add_field(name="Python Version", value=python_version, inline=True)
        embed.add_field(name="Discord.py Version", value=discord_py_version, inline=True)
        
        embed.timestamp = datetime.utcnow()
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="avatar", description="Get user's avatar")
    async def avatar(self, ctx, user: Optional[discord.User] = None):
        """Get a user's avatar."""
        user = user or ctx.author
        
        embed = discord.Embed(
            title=f"{user.name}'s Avatar",
            color=0x7289da
        )
        
        avatar_url = user.avatar.url if user.avatar else user.default_avatar.url
        embed.set_image(url=avatar_url)
        embed.add_field(name="Direct Link", value=f"[Click here]({avatar_url})", inline=False)
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="userinfo", description="Get detailed user information")
    async def userinfo(self, ctx, user: Optional[discord.User] = None):
        """Get detailed information about a user."""
        user = user or ctx.author
        
        member = None
        if ctx.guild:
            member = ctx.guild.get_member(user.id)
        
        embed = discord.Embed(
            title=f"{user.name}",
            color=0x7289da
        )
        
        avatar_url = user.avatar.url if user.avatar else user.default_avatar.url
        embed.set_thumbnail(url=avatar_url)
        
        embed.add_field(name="User ID", value=str(user.id), inline=True)
        embed.add_field(name="Bot", value="Yes" if user.bot else "No", inline=True)
        
        created_at = user.created_at
        account_age = datetime.utcnow() - created_at
        embed.add_field(name="Account Created", value=f"{created_at.strftime('%B %d, %Y')}\n({account_age.days} days ago)", inline=False)
        
        if member:
            joined_at = member.joined_at
            member_age = datetime.utcnow() - joined_at if joined_at else None
            
            embed.add_field(name="Nickname", value=member.display_name, inline=True)
            embed.add_field(name="Joined Server", value=f"{joined_at.strftime('%B %d, %Y')}\n({member_age.days} days ago)" if joined_at else "Unknown", inline=True)
            
            roles = [role for role in member.roles if role != ctx.guild.default_role]
            if roles:
                role_mention = " ".join(role.mention for role in roles[:5])
                if len(roles) > 5:
                    role_mention += f" and {len(roles) - 5} more..."
                embed.add_field(name=f"Roles ({len(roles)})", value=role_mention, inline=False)
        
        embed.timestamp = datetime.utcnow()
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="serverinfo", description="Get detailed server information")
    async def serverinfo(self, ctx):
        """Get detailed information about the current server."""
        if not ctx.guild:
            await ctx.send("This command can only be used in a server!")
            return
        
        guild = ctx.guild
        
        created_at = guild.created_at
        server_age = datetime.utcnow() - created_at
        
        total_members = guild.member_count
        humans = sum(1 for member in guild.members if not member.bot)
        bots = total_members - humans
        
        embed = discord.Embed(
            title=f"{guild.name}",
            description=guild.description or "No description",
            color=0x7289da
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        embed.add_field(name="Server ID", value=str(guild.id), inline=True)
        embed.add_field(name="Owner", value=str(guild.owner), inline=True)
        embed.add_field(name="Created", value=f"{created_at.strftime('%B %d, %Y')}\n({server_age.days} days ago)", inline=False)
        
        embed.add_field(name="Members", value=f"Total: {total_members}\nHumans: {humans}\nBots: {bots}", inline=True)
        
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)
        embed.add_field(name="Channels", value=f"Text: {text_channels}\nVoice: {voice_channels}\nCategories: {categories}", inline=True)
        
        embed.add_field(name="Roles", value=str(len(guild.roles)), inline=True)
        
        embed.timestamp = datetime.utcnow()
        await ctx.send(embed=embed)


async def setup(bot):
    """Setup function for the cog."""
    await bot.add_cog(UtilityCog(bot))