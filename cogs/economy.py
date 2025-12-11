"""
Economy System for Discord Bot
Provides points, levels, and economy commands.
"""

import json
import os
from datetime import datetime
from typing import Optional, Dict

import discord
from discord.ext import commands


class EconomyCog(commands.Cog):
    """Economy and leveling system."""
    
    def __init__(self, bot):
        self.bot = bot
        
        # Data storage
        self.user_data_file = "user_data.json"
        self.user_data = self.load_user_data()
        
        # Economy configuration
        self.daily_reward = 100
        self.weekly_reward = 500
        
    def load_user_data(self) -> Dict:
        """Load user data from file."""
        if os.path.exists(self.user_data_file):
            try:
                with open(self.user_data_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.bot.logger.error(f"Failed to load user data: {e}")
        
        return {}
    
    def save_user_data(self):
        """Save user data to file."""
        try:
            with open(self.user_data_file, 'w') as f:
                json.dump(self.user_data, f, indent=2)
        except Exception as e:
            self.bot.logger.error(f"Failed to save user data: {e}")
    
    def get_user_data(self, user_id: int) -> Dict:
        """Get or create user data."""
        if str(user_id) not in self.user_data:
            self.user_data[str(user_id)] = {
                "coins": 1000,  # Starting coins
                "xp": 0,
                "level": 1,
                "messages": 0,
                "last_daily": None,
                "last_weekly": None
            }
            self.save_user_data()
        
        return self.user_data[str(user_id)]
    
    def add_coins(self, user_id: int, amount: int):
        """Add coins to user."""
        user_data = self.get_user_data(user_id)
        user_data["coins"] += amount
        self.save_user_data()
    
    @commands.hybrid_command(name="profile", description="Check your profile and stats")
    async def profile(self, ctx, user: Optional[discord.User] = None):
        """Check user's profile and statistics."""
        target_user = user or ctx.author
        user_data = self.get_user_data(target_user.id)
        
        embed = discord.Embed(
            title=f"{target_user.display_name}'s Profile",
            color=0x7289da
        )
        
        # Basic stats
        embed.add_field(name="Coins", value=f"{user_data['coins']:,}", inline=True)
        embed.add_field(name="Level", value=str(user_data['level']), inline=True)
        embed.add_field(name="XP", value=str(user_data['xp']), inline=True)
        embed.add_field(name="Messages", value=str(user_data["messages"]), inline=True)
        
        # Set user avatar
        avatar_url = target_user.avatar.url if target_user.avatar else target_user.default_avatar.url
        embed.set_thumbnail(url=avatar_url)
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="daily", description="Claim your daily reward")
    @commands.cooldown(1, 86400, commands.BucketType.user)  # 24 hours
    async def daily(self, ctx):
        """Claim your daily reward."""
        user_id = ctx.author.id
        user_data = self.get_user_data(user_id)
        
        # Check if daily was already claimed
        last_daily = user_data.get("last_daily")
        if last_daily:
            last_daily_time = datetime.fromisoformat(last_daily)
            if (datetime.utcnow() - last_daily_time).total_seconds() < 86400:
                remaining = 86400 - (datetime.utcnow() - last_daily_time).total_seconds()
                hours = int(remaining // 3600)
                minutes = int((remaining % 3600) // 60)
                await ctx.send(f"You can claim your next daily in {hours}h {minutes}m!")
                return
        
        # Award daily reward
        self.add_coins(user_id, self.daily_reward)
        user_data["last_daily"] = datetime.utcnow().isoformat()
        self.save_user_data()
        
        embed = discord.Embed(
            title="Daily Reward Claimed!",
            description="Here's your daily reward:",
            color=0x00ff00
        )
        embed.add_field(name="Coins", value=f"+{self.daily_reward}", inline=True)
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="transfer", description="Transfer coins to another user")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def transfer(self, ctx, user: discord.User, amount: int):
        """Transfer coins to another user."""
        if amount <= 0:
            await ctx.send("Amount must be positive!")
            return
        
        sender_data = self.get_user_data(ctx.author.id)
        receiver_data = self.get_user_data(user.id)
        
        if sender_data["coins"] < amount:
            await ctx.send("You don't have enough coins!")
            return
        
        if user.id == ctx.author.id:
            await ctx.send("You can't transfer coins to yourself!")
            return
        
        # Perform transfer
        sender_data["coins"] -= amount
        receiver_data["coins"] += amount
        self.save_user_data()
        
        embed = discord.Embed(
            title="Transfer Complete",
            color=0x00ff00
        )
        embed.add_field(name="From", value=f"{ctx.author.display_name}", inline=True)
        embed.add_field(name="To", value=f"{user.display_name}", inline=True)
        embed.add_field(name="Amount", value=f"{amount:,} coins", inline=True)
        embed.add_field(name="Your New Balance", value=f"{sender_data['coins']:,} coins", inline=True)
        
        await ctx.send(embed=embed)


async def setup(bot):
    """Setup function for the cog."""
    await bot.add_cog(EconomyCog(bot))