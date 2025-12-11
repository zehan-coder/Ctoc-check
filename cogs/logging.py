"""
Advanced Logging System Cog for Discord Bot
Enterprise-grade logging for messages, members, channels, and bot actions.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict
import io

import discord
from discord.ext import commands, tasks

logger = logging.getLogger(__name__)


class LoggingCog(commands.Cog):
    """Advanced logging system for comprehensive audit trails."""
    
    def __init__(self, bot):
        self.bot = bot
        from database_manager import AdvancedDatabase
        self.db = AdvancedDatabase()
        self.guild_configs = {}
        self.suspicious_activity = {}
        self.load_configs.start()
    
    async def cog_unload(self):
        """Cleanup when cog is unloaded."""
        self.load_configs.cancel()
    
    def get_log_channel(self, guild_id: int) -> Optional[int]:
        """Get logging channel for a guild."""
        return self.guild_configs.get(guild_id, {}).get('log_channel')
    
    async def log_event(
        self,
        guild_id: int,
        log_type: str,
        action: str,
        user_id: int = None,
        target_id: int = None,
        moderator_id: int = None,
        channel_id: int = None,
        message_id: int = None,
        before_state: Dict = None,
        after_state: Dict = None,
        details: str = None,
        retention_days: int = 30
    ):
        """Log an event to database and send to log channel."""
        try:
            # Calculate expiration
            expires_at = datetime.utcnow() + timedelta(days=retention_days) if retention_days else None
            
            # Add to database
            self.db.add_log(
                guild_id=guild_id,
                log_type=log_type,
                action=action,
                user_id=user_id,
                target_id=target_id,
                moderator_id=moderator_id,
                channel_id=channel_id,
                message_id=message_id,
                before_state=json.dumps(before_state) if before_state else None,
                after_state=json.dumps(after_state) if after_state else None,
                details=details,
                expires_at=expires_at
            )
            
            # Send to log channel
            guild = self.bot.get_guild(guild_id)
            if guild:
                log_channel_id = self.get_log_channel(guild_id)
                if log_channel_id:
                    log_channel = guild.get_channel(log_channel_id)
                    if log_channel:
                        embed = await self._create_log_embed(
                            log_type, action, user_id, target_id, moderator_id,
                            before_state, after_state, details, guild
                        )
                        try:
                            await log_channel.send(embed=embed)
                        except Exception as e:
                            logger.error(f"Failed to send log to channel: {e}")
        
        except Exception as e:
            logger.error(f"Failed to log event: {e}")
    
    async def _create_log_embed(
        self,
        log_type: str,
        action: str,
        user_id: int,
        target_id: int,
        moderator_id: int,
        before_state: Dict,
        after_state: Dict,
        details: str,
        guild: discord.Guild
    ) -> discord.Embed:
        """Create an embed for logging."""
        
        # Color based on log type
        color_map = {
            'message': 0x3498db,
            'member': 0x9b59b6,
            'channel': 0xe74c3c,
            'server': 0xf39c12,
            'command': 0x2ecc71,
            'mod': 0xc0392b
        }
        color = color_map.get(log_type, 0x95a5a6)
        
        embed = discord.Embed(
            title=f"{log_type.upper()} - {action}",
            color=color,
            timestamp=datetime.utcnow()
        )
        
        # Add user info
        if user_id:
            user = await self.bot.fetch_user(user_id) if user_id else None
            if user:
                embed.add_field(name="👤 User", value=f"{user.mention} ({user_id})", inline=False)
            else:
                embed.add_field(name="👤 User", value=f"ID: {user_id}", inline=False)
        
        # Add target info
        if target_id:
            try:
                target = await self.bot.fetch_user(target_id) if log_type == 'message' else guild.get_member(target_id)
                if target:
                    embed.add_field(name="🎯 Target", value=f"{target.mention} ({target_id})", inline=False)
                else:
                    embed.add_field(name="🎯 Target", value=f"ID: {target_id}", inline=False)
            except:
                embed.add_field(name="🎯 Target", value=f"ID: {target_id}", inline=False)
        
        # Add moderator info
        if moderator_id:
            try:
                mod = await self.bot.fetch_user(moderator_id)
                if mod:
                    embed.add_field(name="👮 Moderator", value=f"{mod.mention} ({moderator_id})", inline=False)
            except:
                pass
        
        # Add changes if applicable
        if before_state and after_state:
            changes = []
            for key in after_state:
                if before_state.get(key) != after_state.get(key):
                    changes.append(f"**{key}**: {before_state.get(key)} → {after_state.get(key)}")
            
            if changes:
                embed.add_field(
                    name="📝 Changes",
                    value="\n".join(changes[:5]),
                    inline=False
                )
        
        # Add details
        if details:
            embed.add_field(name="📋 Details", value=details[:1024], inline=False)
        
        return embed
    
    @tasks.loop(hours=1)
    async def load_configs(self):
        """Load guild configurations."""
        try:
            for guild in self.bot.guilds:
                # Initialize if not exists
                if guild.id not in self.guild_configs:
                    self.guild_configs[guild.id] = {
                        'log_channel': None,
                        'retention_days': 30,
                        'log_types': ['message', 'member', 'channel', 'command']
                    }
        except Exception as e:
            logger.error(f"Error in load_configs: {e}")
    
    @load_configs.before_loop
    async def before_load_configs(self):
        """Wait for bot to be ready."""
        await self.bot.wait_until_ready()
    
    # ========== MESSAGE EVENTS ==========
    
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        """Log deleted messages."""
        if message.author.bot or not message.guild:
            return
        
        await self.log_event(
            guild_id=message.guild.id,
            log_type='message',
            action='deleted',
            user_id=message.author.id,
            channel_id=message.channel.id,
            message_id=message.id,
            details=f"**Content:** {message.content[:500]}" if message.content else "No text content"
        )
    
    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        """Log edited messages."""
        if before.author.bot or not before.guild:
            return
        
        if before.content == after.content:
            return
        
        await self.log_event(
            guild_id=before.guild.id,
            log_type='message',
            action='edited',
            user_id=before.author.id,
            channel_id=before.channel.id,
            message_id=before.id,
            before_state={'content': before.content[:500]},
            after_state={'content': after.content[:500]}
        )
    
    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages: list):
        """Log bulk message deletions."""
        if not messages or not messages[0].guild:
            return
        
        guild = messages[0].guild
        channel = messages[0].channel
        
        details = f"Deleted {len(messages)} messages from {channel.mention}"
        
        await self.log_event(
            guild_id=guild.id,
            log_type='message',
            action='bulk_deleted',
            channel_id=channel.id,
            details=details
        )
        
        # Detect spam/raid pattern
        if len(messages) > 10:
            if guild.id not in self.suspicious_activity:
                self.suspicious_activity[guild.id] = []
            
            self.suspicious_activity[guild.id].append({
                'type': 'bulk_delete',
                'count': len(messages),
                'time': datetime.utcnow()
            })
    
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        """Log reaction additions (for important messages)."""
        if user.bot or not reaction.message.guild:
            return
    
    # ========== MEMBER EVENTS ==========
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Log member joins."""
        account_age = (datetime.utcnow() - member.created_at).days
        
        details = f"Account age: {account_age} days"
        
        # Detect suspicious new accounts
        if account_age < 3:
            await self.log_event(
                guild_id=member.guild.id,
                log_type='member',
                action='joined_suspicious',
                user_id=member.id,
                details=f"⚠️ NEW ACCOUNT (Age: {account_age} days) - {details}"
            )
        else:
            await self.log_event(
                guild_id=member.guild.id,
                log_type='member',
                action='joined',
                user_id=member.id,
                details=details
            )
    
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        """Log member leaves."""
        guild = member.guild
        
        # Try to determine if kicked/banned
        try:
            async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.kick):
                if entry.target == member:
                    await self.log_event(
                        guild_id=guild.id,
                        log_type='member',
                        action='kicked',
                        user_id=member.id,
                        moderator_id=entry.user.id if entry.user else None,
                        details=f"Reason: {entry.reason}" if entry.reason else "No reason provided"
                    )
                    return
        except:
            pass
        
        await self.log_event(
            guild_id=guild.id,
            log_type='member',
            action='left',
            user_id=member.id
        )
    
    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User):
        """Log member bans."""
        try:
            async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
                if entry.target == user:
                    await self.log_event(
                        guild_id=guild.id,
                        log_type='member',
                        action='banned',
                        user_id=user.id,
                        moderator_id=entry.user.id if entry.user else None,
                        details=f"Reason: {entry.reason}" if entry.reason else "No reason provided"
                    )
                    return
        except:
            pass
        
        await self.log_event(
            guild_id=guild.id,
            log_type='member',
            action='banned',
            user_id=user.id
        )
    
    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        """Log member updates (roles, nickname, etc)."""
        if before.roles != after.roles:
            # Role changes
            removed_roles = set(before.roles) - set(after.roles)
            added_roles = set(after.roles) - set(before.roles)
            
            changes = []
            if removed_roles:
                changes.append(f"Removed: {', '.join(r.mention for r in removed_roles)}")
            if added_roles:
                changes.append(f"Added: {', '.join(r.mention for r in added_roles)}")
            
            await self.log_event(
                guild_id=before.guild.id,
                log_type='member',
                action='roles_updated',
                user_id=before.id,
                details="\n".join(changes)
            )
        
        if before.nick != after.nick:
            await self.log_event(
                guild_id=before.guild.id,
                log_type='member',
                action='nickname_changed',
                user_id=before.id,
                before_state={'nickname': before.nick},
                after_state={'nickname': after.nick}
            )
    
    # ========== CHANNEL EVENTS ==========
    
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel):
        """Log channel creation."""
        await self.log_event(
            guild_id=channel.guild.id,
            log_type='channel',
            action='created',
            channel_id=channel.id,
            details=f"Channel type: {channel.type}"
        )
    
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        """Log channel deletion."""
        await self.log_event(
            guild_id=channel.guild.id,
            log_type='channel',
            action='deleted',
            channel_id=channel.id,
            details=f"Channel: {channel.name} (Type: {channel.type})"
        )
    
    @commands.Cog.listener()
    async def on_guild_channel_update(self, before: discord.abc.GuildChannel, after: discord.abc.GuildChannel):
        """Log channel updates."""
        changes = {}
        
        if before.name != after.name:
            changes['name'] = (before.name, after.name)
        
        if hasattr(before, 'topic') and hasattr(after, 'topic'):
            if before.topic != after.topic:
                changes['topic'] = (before.topic, after.topic)
        
        if hasattr(before, 'nsfw') and hasattr(after, 'nsfw'):
            if before.nsfw != after.nsfw:
                changes['nsfw'] = (before.nsfw, after.nsfw)
        
        if changes:
            before_state = {k: v[0] for k, v in changes.items()}
            after_state = {k: v[1] for k, v in changes.items()}
            
            await self.log_event(
                guild_id=before.guild.id,
                log_type='channel',
                action='updated',
                channel_id=before.id,
                before_state=before_state,
                after_state=after_state
            )
    
    # ========== ROLE EVENTS ==========
    
    @commands.Cog.listener()
    async def on_guild_role_create(self, role: discord.Role):
        """Log role creation."""
        await self.log_event(
            guild_id=role.guild.id,
            log_type='server',
            action='role_created',
            details=f"Role: {role.mention}"
        )
    
    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role):
        """Log role deletion."""
        await self.log_event(
            guild_id=role.guild.id,
            log_type='server',
            action='role_deleted',
            details=f"Role: {role.name}"
        )
    
    @commands.Cog.listener()
    async def on_guild_role_update(self, before: discord.Role, after: discord.Role):
        """Log role updates."""
        changes = {}
        
        if before.name != after.name:
            changes['name'] = (before.name, after.name)
        if before.color != after.color:
            changes['color'] = (str(before.color), str(after.color))
        if before.permissions != after.permissions:
            changes['permissions'] = ('Updated', 'Check audit logs for details')
        
        if changes:
            before_state = {k: v[0] for k, v in changes.items()}
            after_state = {k: v[1] for k, v in changes.items()}
            
            await self.log_event(
                guild_id=before.guild.id,
                log_type='server',
                action='role_updated',
                before_state=before_state,
                after_state=after_state
            )
    
    # ========== COMMAND LOGGING ==========
    
    @commands.Cog.listener()
    async def on_command(self, ctx):
        """Log command executions."""
        if ctx.author.bot:
            return
        
        # Log command
        await self.log_event(
            guild_id=ctx.guild.id if ctx.guild else 0,
            log_type='command',
            action='executed',
            user_id=ctx.author.id,
            channel_id=ctx.channel.id if ctx.guild else 0,
            details=f"**Command:** {ctx.message.content}"
        )
    
    # ========== LOGGING COMMANDS ==========
    
    @commands.group(name="logs", description="Logging commands")
    @commands.has_permissions(administrator=True)
    async def logs_group(self, ctx):
        """Logging command group."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use `!logs config`, `!logs search`, `!logs stats`, etc.")
    
    @logs_group.command(name="config", description="Configure logging")
    @commands.has_permissions(administrator=True)
    async def logs_config(self, ctx, log_channel: Optional[discord.TextChannel] = None):
        """Configure the logging channel."""
        if log_channel is None:
            current = self.get_log_channel(ctx.guild.id)
            if current:
                channel = ctx.guild.get_channel(current)
                await ctx.send(f"Current logging channel: {channel.mention if channel else 'Unknown'}")
            else:
                await ctx.send("No logging channel configured.")
            return
        
        # Set logging channel
        self.guild_configs[ctx.guild.id] = {
            'log_channel': log_channel.id,
            'retention_days': 30,
            'log_types': ['message', 'member', 'channel', 'command']
        }
        
        await ctx.send(f"✅ Logging channel set to {log_channel.mention}")
    
    @logs_group.command(name="search", description="Search logs")
    @commands.has_permissions(administrator=True)
    async def logs_search(self, ctx, search_type: str = "all", limit: int = 10):
        """Search logs. Types: all, message, member, channel, command, server"""
        if search_type not in ["all", "message", "member", "channel", "command", "server"]:
            await ctx.send("Invalid search type. Use: all, message, member, channel, command, server")
            return
        
        log_type = None if search_type == "all" else search_type
        logs = self.db.search_logs(ctx.guild.id, log_type=log_type, limit=min(limit, 50))
        
        if not logs:
            await ctx.send("No logs found.")
            return
        
        embed = discord.Embed(
            title=f"📋 Log Search Results ({len(logs)})",
            color=0x3498db
        )
        
        for log in logs[:10]:
            timestamp = log['created_at']
            log_text = f"**{log['action']}**\n"
            
            if log['user_id']:
                log_text += f"User: <@{log['user_id']}>\n"
            
            if log['details']:
                details = log['details'][:100]
                log_text += f"Details: {details}"
            
            embed.add_field(
                name=f"{log['log_type']} - {timestamp}",
                value=log_text,
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @logs_group.command(name="user", description="View user activity")
    @commands.has_permissions(administrator=True)
    async def logs_user(self, ctx, user: discord.User, limit: int = 20):
        """View activity log for a specific user."""
        logs = self.db.get_user_activity(ctx.guild.id, user.id, limit=limit)
        
        if not logs:
            await ctx.send(f"No activity logs found for {user.mention}")
            return
        
        embed = discord.Embed(
            title=f"👤 Activity Log for {user}",
            description=f"Showing {len(logs)} entries",
            color=0x9b59b6
        )
        
        for log in logs[:15]:
            timestamp = log['created_at']
            log_text = f"**{log['log_type']}** - {log['action']}\n"
            
            if log['details']:
                log_text += log['details'][:100]
            
            embed.add_field(name=timestamp, value=log_text, inline=False)
        
        await ctx.send(embed=embed)
    
    @logs_group.command(name="stats", description="View logging statistics")
    async def logs_stats(self, ctx):
        """View logging statistics for the server."""
        stats = self.db.get_log_stats(ctx.guild.id)
        
        if not stats:
            await ctx.send("No log statistics available.")
            return
        
        embed = discord.Embed(
            title="📊 Logging Statistics",
            color=0x2ecc71
        )
        
        embed.add_field(
            name="Total Logs",
            value=str(stats.get('total_logs', 0)),
            inline=True
        )
        
        embed.add_field(
            name="Last 24 Hours",
            value=str(stats.get('logs_24h', 0)),
            inline=True
        )
        
        # Logs by type
        logs_by_type = stats.get('logs_by_type', {})
        if logs_by_type:
            type_str = "\n".join([f"**{k}**: {v}" for k, v in logs_by_type.items()])
            embed.add_field(name="Logs by Type", value=type_str, inline=False)
        
        # Top actions
        top_actions = stats.get('top_actions', {})
        if top_actions:
            action_str = "\n".join([f"**{k}**: {v}" for k, v in top_actions.items()])
            embed.add_field(name="Top Actions", value=action_str, inline=False)
        
        await ctx.send(embed=embed)
    
    @logs_group.command(name="export", description="Export logs to file")
    @commands.has_permissions(administrator=True)
    async def logs_export(self, ctx, format: str = "json"):
        """Export logs to JSON or CSV format."""
        if format not in ["json", "csv"]:
            await ctx.send("Format must be 'json' or 'csv'")
            return
        
        async with ctx.typing():
            data = self.db.export_logs(ctx.guild.id, format=format)
            
            if not data:
                await ctx.send("No logs to export.")
                return
            
            # Create file
            filename = f"logs_{ctx.guild.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.{format}"
            file = discord.File(io.BytesIO(data.encode()), filename=filename)
            
            await ctx.send(f"📤 Exported {len(data)} bytes of logs", file=file)
    
    @logs_group.command(name="dashboard", description="View recent activity dashboard")
    async def logs_dashboard(self, ctx):
        """View a dashboard of recent activity."""
        logs = self.db.search_logs(ctx.guild.id, limit=30)
        
        if not logs:
            await ctx.send("No activity to display.")
            return
        
        embed = discord.Embed(
            title="📊 Activity Dashboard",
            description="Recent server activity",
            color=0xf39c12
        )
        
        # Count by type
        type_counts = {}
        for log in logs:
            log_type = log['log_type']
            type_counts[log_type] = type_counts.get(log_type, 0) + 1
        
        type_str = "\n".join([f"• **{k}**: {v}" for k, v in type_counts.items()])
        embed.add_field(name="Activity Breakdown", value=type_str, inline=False)
        
        # Recent events
        recent = logs[:5]
        recent_str = ""
        for log in recent:
            recent_str += f"• **{log['log_type']}** - {log['action']}\n"
        
        embed.add_field(name="Recent Events", value=recent_str, inline=False)
        
        embed.timestamp = datetime.utcnow()
        await ctx.send(embed=embed)


async def setup(bot):
    """Setup function for the cog."""
    await bot.add_cog(LoggingCog(bot))
