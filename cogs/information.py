"""
Information Commands for Discord Bot
Provides detailed information commands for roles, channels, emojis, etc.
"""

import asyncio
from datetime import datetime
from typing import Optional

import discord
from discord.ext import commands


class InformationCog(commands.Cog):
    """Information and lookup commands."""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="serverinfo", description="Show server information")
    async def server_info(self, ctx):
        """Show detailed server information."""
        if not ctx.guild:
            await ctx.send("This command can only be used in a server!")
            return
        
        guild = ctx.guild
        
        # Calculate server age
        created_at = guild.created_at
        server_age = datetime.utcnow() - created_at
        
        # Get member counts
        total_members = guild.member_count
        humans = sum(1 for member in guild.members if not member.bot)
        bots = total_members - humans
        
        embed = discord.Embed(
            title=f"{guild.name}",
            description=guild.description or "No description",
            color=0x7289da
        )
        
        # Server icon
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        # Basic info
        embed.add_field(name="Server ID", value=str(guild.id), inline=True)
        embed.add_field(name="Owner", value=str(guild.owner), inline=True)
        embed.add_field(name="Created", value=f"{created_at.strftime('%B %d, %Y')}\\n({server_age.days} days ago)", inline=False)
        
        # Member info
        embed.add_field(name="Members", value=f"Total: {total_members}\\nHumans: {humans}\\nBots: {bots}", inline=True)
        
        # Channel info
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)
        embed.add_field(name="Channels", value=f"Text: {text_channels}\\nVoice: {voice_channels}\\nCategories: {categories}", inline=True)
        
        # Role info
        embed.add_field(name="Roles", value=str(len(guild.roles)), inline=True)
        
        embed.timestamp = datetime.utcnow()
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="userinfo", description="Show user information")
    async def user_info(self, ctx, user: Optional[discord.User] = None):
        """Show detailed user information."""
        user = user or ctx.author
        
        # Check if user is in the current guild
        member = None
        if ctx.guild:
            member = ctx.guild.get_member(user.id)
        
        embed = discord.Embed(
            title=f"{user.name}",
            color=0x7289da
        )
        
        # User avatar
        avatar_url = user.avatar.url if user.avatar else user.default_avatar.url
        embed.set_thumbnail(url=avatar_url)
        
        # Basic info
        embed.add_field(name="User ID", value=str(user.id), inline=True)
        embed.add_field(name="Bot", value="Yes" if user.bot else "No", inline=True)
        
        # Account creation
        created_at = user.created_at
        account_age = datetime.utcnow() - created_at
        embed.add_field(name="Account Created", value=f"{created_at.strftime('%B %d, %Y')}\\n({account_age.days} days ago)", inline=False)
        
        # Guild member info (if applicable)
        if member:
            joined_at = member.joined_at
            member_age = datetime.utcnow() - joined_at if joined_at else None
            
            embed.add_field(name="Nickname", value=member.display_name, inline=True)
            embed.add_field(name="Joined Server", value=f"{joined_at.strftime('%B %d, %Y')}\\n({member_age.days} days ago)" if joined_at else "Unknown", inline=True)
            
            # Roles
            roles = [role for role in member.roles if role != ctx.guild.default_role]
            if roles:
                role_mention = " ".join(role.mention for role in roles[:5])
                if len(roles) > 5:
                    role_mention += f" and {len(roles) - 5} more..."
                embed.add_field(name=f"Roles ({len(roles)})", value=role_mention, inline=False)
        
        embed.timestamp = datetime.utcnow()
        await ctx.send(embed=embed)


async def setup(bot):
    """Setup function for the cog."""
    await bot.add_cog(InformationCog(bot))