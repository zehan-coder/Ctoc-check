"""
Moderation Commands for Discord Bot
Provides moderation tools like kick, ban, warn, mute, etc.
"""

import asyncio
from datetime import datetime
from typing import Optional

import discord
from discord.ext import commands


class ModerationCog(commands.Cog):
    """Moderation and administrative commands."""
    
    def __init__(self, bot):
        self.bot = bot
        
        # Warning system
        self.warnings = {}  # guild_id: {user_id: [warnings]}
    
    @commands.hybrid_command(name="kick", description="Kick a user from the server")
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, user: discord.Member, *, reason: str = "No reason provided"):
        """Kick a user from the server."""
        if user.id == ctx.author.id:
            await ctx.send("You can't kick yourself!")
            return
        
        if user.id == self.bot.user.id:
            await ctx.send("You can't kick me!")
            return
        
        # Check if user can be kicked (higher role check)
        if user.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
            await ctx.send("You can't kick someone with a higher or equal role!")
            return
        
        try:
            # Create embed for logging
            embed = discord.Embed(
                title="User Kicked",
                color=0xffa500
            )
            embed.add_field(name="User", value=f"{user} ({user.id})", inline=True)
            embed.add_field(name="Moderator", value=f"{ctx.author} ({ctx.author.id})", inline=True)
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.timestamp = datetime.utcnow()
            
            # Send DM to user
            try:
                await user.send(f"You have been kicked from {ctx.guild.name}. Reason: {reason}")
            except:
                pass  # User might have DMs disabled
            
            await ctx.guild.kick(user, reason=reason)
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            await ctx.send("I don't have permission to kick this user!")
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")
    
    @commands.hybrid_command(name="ban", description="Ban a user from the server")
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.Member, days: int = 1, *, reason: str = "No reason provided"):
        """Ban a user from the server."""
        if days < 0 or days > 7:
            await ctx.send("Days must be between 0 and 7!")
            return
        
        if user.id == ctx.author.id:
            await ctx.send("You can't ban yourself!")
            return
        
        if user.id == self.bot.user.id:
            await ctx.send("You can't ban me!")
            return
        
        # Check if user can be banned (higher role check)
        if user.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
            await ctx.send("You can't ban someone with a higher or equal role!")
            return
        
        try:
            # Create embed for logging
            embed = discord.Embed(
                title="User Banned",
                color=0xff0000
            )
            embed.add_field(name="User", value=f"{user} ({user.id})", inline=True)
            embed.add_field(name="Moderator", value=f"{ctx.author} ({ctx.author.id})", inline=True)
            embed.add_field(name="Reason", value=reason, inline=False)
            if days > 0:
                embed.add_field(name="Messages Deleted", value=f"Last {days} days", inline=True)
            embed.timestamp = datetime.utcnow()
            
            # Send DM to user
            try:
                await user.send(f"You have been banned from {ctx.guild.name}. Reason: {reason}")
            except:
                pass  # User might have DMs disabled
            
            await ctx.guild.ban(user, reason=reason, delete_message_days=days)
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            await ctx.send("I don't have permission to ban this user!")
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")
    
    @commands.hybrid_command(name="warn", description="Warn a user")
    @commands.has_permissions(kick_members=True)
    async def warn(self, ctx, user: discord.Member, *, reason: str = "No reason provided"):
        """Warn a user."""
        if user.id == ctx.author.id:
            await ctx.send("You can't warn yourself!")
            return
        
        # Get or create guild warnings
        if ctx.guild.id not in self.warnings:
            self.warnings[ctx.guild.id] = {}
        
        if user.id not in self.warnings[ctx.guild.id]:
            self.warnings[ctx.guild.id][user.id] = []
        
        # Add warning
        warning = {
            "reason": reason,
            "moderator": ctx.author.id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.warnings[ctx.guild.id][user.id].append(warning)
        warning_count = len(self.warnings[ctx.guild.id][user.id])
        
        # Send DM to user
        try:
            await user.send(f"You have been warned in {ctx.guild.name}. Reason: {reason}\\nTotal warnings: {warning_count}")
        except:
            pass  # User might have DMs disabled
        
        embed = discord.Embed(
            title="User Warned",
            color=0xffff00
        )
        embed.add_field(name="User", value=f"{user} ({user.id})", inline=True)
        embed.add_field(name="Moderator", value=f"{ctx.author} ({ctx.author.id})", inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Total Warnings", value=str(warning_count), inline=True)
        embed.timestamp = datetime.utcnow()
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="clear", description="Clear messages")
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int = 10):
        """Clear messages."""
        if amount < 1 or amount > 100:
            await ctx.send("Amount must be between 1 and 100!")
            return
        
        try:
            # Calculate messages to delete (including the command message)
            deleted = await ctx.channel.purge(limit=amount + 1)
            
            embed = discord.Embed(
                title="Messages Cleared",
                color=0x00ff00
            )
            embed.add_field(name="Amount", value=str(len(deleted) - 1), inline=True)
            embed.add_field(name="Moderator", value=f"{ctx.author} ({ctx.author.id})", inline=True)
            embed.timestamp = datetime.utcnow()
            
            # Send confirmation message and auto-delete it
            confirmation = await ctx.send(embed=embed)
            await asyncio.sleep(3)
            await confirmation.delete()
            
        except discord.Forbidden:
            await ctx.send("I don't have permission to delete messages!")
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")


async def setup(bot):
    """Setup function for the cog."""
    await bot.add_cog(ModerationCog(bot))