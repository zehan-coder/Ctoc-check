"""
Advanced Giveaway System Cog for Discord Bot
Comprehensive giveaway management with multiple entry methods and advanced features.
"""

import asyncio
import random
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from uuid import uuid4

import discord
from discord.ext import commands, tasks

logger = logging.getLogger(__name__)


class GiveawayView(discord.ui.View):
    """Interactive view for giveaway entry."""
    
    def __init__(self, cog, giveaway_id: str, timeout=None):
        super().__init__(timeout=timeout)
        self.cog = cog
        self.giveaway_id = giveaway_id
    
    @discord.ui.button(label="Enter Giveaway", style=discord.ButtonStyle.green)
    async def enter_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Button to enter giveaway."""
        await interaction.response.defer(ephemeral=True)
        
        giveaway = self.cog.db.get_giveaway(self.giveaway_id)
        if not giveaway:
            await interaction.followup.send("Giveaway not found!", ephemeral=True)
            return
        
        if giveaway['status'] != 'active':
            await interaction.followup.send(f"This giveaway is {giveaway['status']}!", ephemeral=True)
            return
        
        # Check eligibility
        eligible, reason = await self.cog.check_eligibility(interaction.user, giveaway)
        if not eligible:
            await interaction.followup.send(f"You are not eligible: {reason}", ephemeral=True)
            return
        
        # Add entry
        success = self.cog.db.add_entry(self.giveaway_id, interaction.user.id)
        if success:
            await interaction.followup.send("✅ You have entered the giveaway!", ephemeral=True)
        else:
            await interaction.followup.send("❌ Failed to enter giveaway.", ephemeral=True)


class GiveawayCog(commands.Cog):
    """Advanced giveaway system for managing server giveaways."""
    
    def __init__(self, bot):
        self.bot = bot
        from database_manager import AdvancedDatabase
        self.db = AdvancedDatabase()
        self.reminder_tasks = {}
        self.check_giveaways.start()
        self.cleanup_giveaways.start()
    
    async def cog_unload(self):
        """Cleanup when cog is unloaded."""
        self.check_giveaways.cancel()
        self.cleanup_giveaways.cancel()
    
    @tasks.loop(minutes=1)
    async def check_giveaways(self):
        """Check and end expired giveaways."""
        try:
            for guild in self.bot.guilds:
                giveaways = self.db.get_active_giveaways(guild.id)
                for giveaway in giveaways:
                    if giveaway['status'] == 'active':
                        ends_at = datetime.fromisoformat(giveaway['ends_at'])
                        now = datetime.utcnow()
                        
                        # Check if giveaway should end
                        if now >= ends_at and not giveaway['paused_at']:
                            await self.end_giveaway(giveaway['giveaway_id'])
        except Exception as e:
            logger.error(f"Error in check_giveaways: {e}")
    
    @check_giveaways.before_loop
    async def before_check_giveaways(self):
        """Wait for bot to be ready."""
        await self.bot.wait_until_ready()
    
    @tasks.loop(hours=1)
    async def cleanup_giveaways(self):
        """Cleanup old giveaways and expired logs."""
        try:
            self.db.cleanup_expired_logs()
            logger.info("Cleanup task completed")
        except Exception as e:
            logger.error(f"Error in cleanup_giveaways: {e}")
    
    @cleanup_giveaways.before_loop
    async def before_cleanup(self):
        """Wait for bot to be ready."""
        await self.bot.wait_until_ready()
    
    async def check_eligibility(self, user: discord.Member, giveaway: Dict) -> tuple[bool, str]:
        """Check if user is eligible for giveaway."""
        # Check if user is in the server
        if isinstance(user, discord.User):
            try:
                guild = self.bot.get_guild(giveaway['guild_id'])
                user = guild.get_member(user.id)
                if not user:
                    return False, "You are not in this server."
            except:
                return False, "Could not verify server membership."
        
        # Check whitelist
        if giveaway['whitelist_users']:
            if user.id not in giveaway['whitelist_users']:
                return False, "You are not whitelisted for this giveaway."
        
        # Check blacklist
        if giveaway['blacklist_users']:
            if user.id in giveaway['blacklist_users']:
                return False, "You are blacklisted from this giveaway."
        
        # Check required roles
        if giveaway['requires_roles']:
            user_roles = [r.id for r in user.roles]
            has_required = any(role_id in user_roles for role_id in giveaway['requires_roles'])
            if not has_required:
                return False, "You do not have a required role."
        
        # Check excluded roles
        if giveaway['exclude_roles']:
            user_roles = [r.id for r in user.roles]
            has_excluded = any(role_id in user_roles for role_id in giveaway['exclude_roles'])
            if has_excluded:
                return False, "You have an excluded role."
        
        # Check account age
        if giveaway['min_account_age_days']:
            account_age = (datetime.utcnow() - user.created_at).days
            if account_age < giveaway['min_account_age_days']:
                return False, f"Your account is too new (requires {giveaway['min_account_age_days']} days)."
        
        # Check server membership duration
        if giveaway['min_server_join_days']:
            join_age = (datetime.utcnow() - user.joined_at).days
            if join_age < giveaway['min_server_join_days']:
                return False, f"You haven't been in this server long enough (requires {giveaway['min_server_join_days']} days)."
        
        return True, ""
    
    async def send_giveaway_embed(self, channel: discord.TextChannel, giveaway: Dict, remaining: str = None):
        """Send giveaway embed to channel."""
        try:
            prizes_str = "\n".join([f"• {prize}" for prize in giveaway['prizes']])
            
            embed = discord.Embed(
                title=f"🎁 {giveaway['title']}",
                description=giveaway['description'] or "Join this amazing giveaway!",
                color=0xFF6B9D
            )
            
            embed.add_field(
                name="🏆 Prizes",
                value=prizes_str if prizes_str else "Amazing prizes await!",
                inline=False
            )
            
            embed.add_field(
                name="🎯 Winners",
                value=f"{giveaway['winner_count']} winner(s)",
                inline=True
            )
            
            if remaining:
                embed.add_field(
                    name="⏱️ Time Remaining",
                    value=remaining,
                    inline=True
                )
            
            # Add eligibility info if any
            eligibility_parts = []
            if giveaway['requires_roles']:
                eligibility_parts.append(f"Requires specific roles")
            if giveaway['min_account_age_days']:
                eligibility_parts.append(f"Account age: {giveaway['min_account_age_days']}+ days")
            if giveaway['min_server_join_days']:
                eligibility_parts.append(f"Server membership: {giveaway['min_server_join_days']}+ days")
            
            if eligibility_parts:
                embed.add_field(
                    name="📋 Requirements",
                    value="\n".join(eligibility_parts),
                    inline=False
                )
            
            embed.set_footer(text=f"Giveaway ID: {giveaway['giveaway_id'][:8]}")
            embed.timestamp = datetime.utcnow()
            
            view = GiveawayView(self, giveaway['giveaway_id'], timeout=None)
            message = await channel.send(embed=embed, view=view)
            return message.id
        except Exception as e:
            logger.error(f"Failed to send giveaway embed: {e}")
            return None
    
    async def end_giveaway(self, giveaway_id: str):
        """End a giveaway and select winners."""
        try:
            giveaway = self.db.get_giveaway(giveaway_id)
            if not giveaway or giveaway['status'] == 'ended':
                return
            
            # Update status
            self.db.update_giveaway(giveaway_id, status='ended', ended_at=datetime.utcnow().isoformat())
            
            # Get entries
            entries = self.db.get_entries(giveaway_id)
            
            if not entries:
                # No winners
                guild = self.bot.get_guild(giveaway['guild_id'])
                channel = guild.get_channel(giveaway['channel_id'])
                
                if channel:
                    embed = discord.Embed(
                        title="🎁 Giveaway Ended",
                        description=f"No one entered {giveaway['title']}. Better luck next time!",
                        color=0xFF6B9D
                    )
                    await channel.send(embed=embed)
                return
            
            # Select winners with weighted random (more entries = higher chance)
            winners = []
            selected_users = set()
            
            for position in range(min(giveaway['winner_count'], len(set(e['user_id'] for e in entries)))):
                # Build weighted list
                eligible_entries = [e for e in entries if e['user_id'] not in selected_users]
                if not eligible_entries:
                    break
                
                # Weighted random selection
                weights = [e['entry_count'] for e in eligible_entries]
                winner_entry = random.choices(eligible_entries, weights=weights, k=1)[0]
                
                winner_id = winner_entry['user_id']
                prize = giveaway['prizes'][position] if position < len(giveaway['prizes']) else giveaway['prizes'][-1]
                
                # Check eligibility at end time
                guild = self.bot.get_guild(giveaway['guild_id'])
                user = guild.get_member(winner_id)
                
                if user:
                    eligible, _ = await self.check_eligibility(user, giveaway)
                    if eligible:
                        self.db.add_winner(giveaway_id, winner_id, prize, position + 1)
                        winners.append((user, prize))
                        selected_users.add(winner_id)
                        
                        # DM winner
                        try:
                            dm_embed = discord.Embed(
                                title="🎉 You won a giveaway!",
                                description=f"Congratulations! You won **{prize}** in **{giveaway['title']}**!",
                                color=0x00FF00
                            )
                            await user.send(embed=dm_embed)
                        except:
                            pass
            
            # Post results
            guild = self.bot.get_guild(giveaway['guild_id'])
            channel = guild.get_channel(giveaway['channel_id'])
            
            if channel:
                if winners:
                    winners_str = "\n".join([f"• {user.mention} - **{prize}**" for user, prize in winners])
                    embed = discord.Embed(
                        title="🎁 Giveaway Ended",
                        description=f"**{giveaway['title']}** has ended!",
                        color=0x00FF00
                    )
                    embed.add_field(name="🏆 Winners", value=winners_str, inline=False)
                    embed.timestamp = datetime.utcnow()
                    await channel.send(embed=embed)
                else:
                    embed = discord.Embed(
                        title="🎁 Giveaway Ended",
                        description=f"No eligible winners found for **{giveaway['title']}**.",
                        color=0xFF6B9D
                    )
                    await channel.send(embed=embed)
        
        except Exception as e:
            logger.error(f"Failed to end giveaway {giveaway_id}: {e}")
    
    @commands.group(name="giveaway", description="Giveaway commands")
    @commands.has_permissions(administrator=True)
    async def giveaway_group(self, ctx):
        """Giveaway command group."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use `!giveaway start`, `!giveaway list`, etc.")
    
    @giveaway_group.command(name="start", description="Start a new giveaway")
    @commands.has_permissions(administrator=True)
    async def start_giveaway(
        self,
        ctx,
        duration_minutes: int,
        winner_count: int = 1,
        *,
        title: str = None
    ):
        """Start a new giveaway. Usage: !giveaway start <minutes> [winners] <title>"""
        if not title:
            await ctx.send("❌ Please provide a title for the giveaway.")
            return
        
        if duration_minutes < 1 or duration_minutes > 10080:  # Max 1 week
            await ctx.send("❌ Duration must be between 1 and 10080 minutes.")
            return
        
        if winner_count < 1 or winner_count > 10:
            await ctx.send("❌ Winner count must be between 1 and 10.")
            return
        
        # Create giveaway
        giveaway_id = f"giveaway_{uuid4().hex[:12]}"
        duration_seconds = duration_minutes * 60
        
        self.db.create_giveaway(
            giveaway_id=giveaway_id,
            guild_id=ctx.guild.id,
            creator_id=ctx.author.id,
            channel_id=ctx.channel.id,
            title=title,
            prizes=[title] * winner_count,
            duration_seconds=duration_seconds,
            winner_count=winner_count
        )
        
        # Send giveaway message
        remaining = f"{duration_minutes} minute(s)"
        message_id = await self.send_giveaway_embed(ctx.channel, self.db.get_giveaway(giveaway_id), remaining)
        
        if message_id:
            self.db.update_giveaway(giveaway_id, message_id=message_id)
            await ctx.send(f"✅ Giveaway **{title}** started! React to enter.", delete_after=10)
        else:
            await ctx.send("❌ Failed to start giveaway.")
    
    @giveaway_group.command(name="list", description="List active giveaways")
    async def list_giveaways(self, ctx):
        """List all active giveaways."""
        giveaways = self.db.get_active_giveaways(ctx.guild.id)
        
        if not giveaways:
            await ctx.send("No active giveaways.")
            return
        
        embed = discord.Embed(
            title=f"🎁 Active Giveaways ({len(giveaways)})",
            color=0xFF6B9D
        )
        
        for giveaway in giveaways[:10]:
            ends_at = datetime.fromisoformat(giveaway['ends_at'])
            remaining = (ends_at - datetime.utcnow()).total_seconds()
            
            if remaining > 0:
                minutes = int(remaining // 60)
                hours = minutes // 60
                days = hours // 24
                
                if days > 0:
                    time_str = f"{days}d {hours % 24}h"
                elif hours > 0:
                    time_str = f"{hours}h {minutes % 60}m"
                else:
                    time_str = f"{minutes}m"
                
                entries = len(self.db.get_entries(giveaway['giveaway_id']))
                
                embed.add_field(
                    name=giveaway['title'],
                    value=f"Winners: {giveaway['winner_count']} | Entries: {entries} | Time: {time_str}",
                    inline=False
                )
        
        await ctx.send(embed=embed)
    
    @giveaway_group.command(name="end", description="End a giveaway early")
    @commands.has_permissions(administrator=True)
    async def end_giveaway_cmd(self, ctx, giveaway_id: str):
        """End a giveaway early."""
        giveaway = self.db.get_giveaway(giveaway_id)
        if not giveaway:
            await ctx.send("❌ Giveaway not found.")
            return
        
        if giveaway['guild_id'] != ctx.guild.id:
            await ctx.send("❌ This giveaway is not in this server.")
            return
        
        await self.end_giveaway(giveaway_id)
        await ctx.send(f"✅ Giveaway **{giveaway['title']}** ended!")
    
    @giveaway_group.command(name="reroll", description="Reroll a giveaway winner")
    @commands.has_permissions(administrator=True)
    async def reroll_giveaway(self, ctx, giveaway_id: str):
        """Reroll winner(s) for a finished giveaway."""
        giveaway = self.db.get_giveaway(giveaway_id)
        if not giveaway:
            await ctx.send("❌ Giveaway not found.")
            return
        
        if giveaway['guild_id'] != ctx.guild.id:
            await ctx.send("❌ This giveaway is not in this server.")
            return
        
        # Get entries
        entries = self.db.get_entries(giveaway_id)
        if not entries:
            await ctx.send("❌ No entries to reroll from.")
            return
        
        # Clear old winners
        old_winners = self.db.get_winners(giveaway_id)
        
        # Select new winner
        eligible_entries = [e for e in entries]
        weights = [e['entry_count'] for e in eligible_entries]
        winner_entry = random.choices(eligible_entries, weights=weights, k=1)[0]
        
        guild = self.bot.get_guild(giveaway['guild_id'])
        user = guild.get_member(winner_entry['user_id'])
        
        if user:
            try:
                dm_embed = discord.Embed(
                    title="🎉 Reroll Winner!",
                    description=f"You won a reroll in **{giveaway['title']}**!",
                    color=0x00FF00
                )
                await user.send(embed=dm_embed)
            except:
                pass
        
        embed = discord.Embed(
            title="🔄 Reroll Result",
            description=f"New winner for **{giveaway['title']}**: {user.mention if user else 'Unknown User'}",
            color=0xFF6B9D
        )
        await ctx.send(embed=embed)
    
    @giveaway_group.command(name="results", description="View giveaway results")
    async def giveaway_results(self, ctx, giveaway_id: str):
        """View results of a giveaway."""
        giveaway = self.db.get_giveaway(giveaway_id)
        if not giveaway:
            await ctx.send("❌ Giveaway not found.")
            return
        
        if giveaway['guild_id'] != ctx.guild.id:
            await ctx.send("❌ This giveaway is not in this server.")
            return
        
        winners = self.db.get_winners(giveaway_id)
        entries = self.db.get_entries(giveaway_id)
        
        embed = discord.Embed(
            title=f"🎁 {giveaway['title']} - Results",
            color=0xFF6B9D
        )
        
        embed.add_field(name="Status", value=giveaway['status'], inline=True)
        embed.add_field(name="Total Entries", value=str(len(entries)), inline=True)
        embed.add_field(name="Total Participants", value=str(len(set(e['user_id'] for e in entries))), inline=True)
        
        if winners:
            winners_str = ""
            guild = self.bot.get_guild(giveaway['guild_id'])
            for i, winner in enumerate(winners, 1):
                user = guild.get_member(winner['user_id'])
                username = user.mention if user else f"User {winner['user_id']}"
                winners_str += f"{i}. {username} - **{winner['prize']}**\n"
            
            embed.add_field(name="🏆 Winners", value=winners_str, inline=False)
        else:
            embed.add_field(name="🏆 Winners", value="No winners", inline=False)
        
        await ctx.send(embed=embed)


async def setup(bot):
    """Setup function for the cog."""
    await bot.add_cog(GiveawayCog(bot))
