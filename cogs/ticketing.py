"""
Advanced Ticketing System Cog
Provides comprehensive ticket management with panels, claims, ratings, and more.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional

import discord
from discord.ext import commands, tasks

from ticket_database import TicketDatabase

logger = logging.getLogger(__name__)


class TicketingCog(commands.Cog):
    """Advanced ticket management system."""
    
    # Ticket categories
    CATEGORIES = {
        'support': '🆘',
        'bug': '🐛',
        'feature': '⭐',
        'general': '💬',
        'billing': '💳'
    }
    
    # Ticket statuses
    STATUSES = {
        'open': 0xff0000,
        'in-progress': 0xffaa00,
        'closed': 0x00ff00,
        'resolved': 0x00aa00,
        'awaiting-response': 0x0000ff
    }
    
    # Priority colors
    PRIORITY_COLORS = {
        'low': 0x00ff00,
        'medium': 0xffaa00,
        'high': 0xff6600,
        'urgent': 0xff0000
    }
    
    def __init__(self, bot):
        self.bot = bot
        self.db = TicketDatabase()
        self.ticket_counter = {}  # {guild_id: next_number}
        self.inactive_check.start()
    
    def cog_unload(self):
        """Clean up when cog is unloaded."""
        self.inactive_check.cancel()
    
    @tasks.loop(hours=1)
    async def inactive_check(self):
        """Check for inactive tickets and auto-close if configured."""
        try:
            for guild in self.bot.guilds:
                tickets = self.db.get_guild_tickets(guild.id, status='open')
                
                # Check for tickets inactive for 7 days (configurable)
                cutoff = datetime.utcnow() - timedelta(days=7)
                
                for ticket_data in tickets:
                    updated_at = datetime.fromisoformat(ticket_data['updated_at'])
                    if updated_at < cutoff:
                        # Close the ticket
                        self.db.update_ticket(ticket_data['id'], status='closed')
                        
                        # Try to notify in channel
                        if ticket_data['channel_id']:
                            try:
                                channel = self.bot.get_channel(ticket_data['channel_id'])
                                if channel:
                                    embed = discord.Embed(
                                        title="Ticket Auto-Closed",
                                        description="This ticket was closed due to inactivity.",
                                        color=0xff0000
                                    )
                                    await channel.send(embed=embed)
                            except:
                                pass
        except Exception as e:
            logger.error(f"Error in inactive check: {e}")
    
    @inactive_check.before_loop
    async def before_inactive_check(self):
        """Wait until bot is ready before starting the check."""
        await self.bot.wait_until_ready()
    
    def get_next_ticket_number(self, guild_id: int) -> str:
        """Get next ticket number for a guild."""
        if guild_id not in self.ticket_counter:
            self.ticket_counter[guild_id] = 1
        
        number = self.ticket_counter[guild_id]
        self.ticket_counter[guild_id] += 1
        return f"TK-{guild_id}-{number:04d}"
    
    @commands.command(name="ticket", description="Create a new support ticket")
    async def ticket_create(
        self,
        ctx,
        category: Optional[str] = None,
        *,
        title: Optional[str] = None
    ):
        """Create a new ticket with interactive prompts."""
        if not title:
            embed = discord.Embed(
                title="Ticket Creation",
                description="Please provide a title for your ticket.\nUsage: `!ticket [category] <title>`",
                color=0x7289da
            )
            embed.add_field(
                name="Available Categories",
                value="\n".join(f"• {cat}" for cat in self.CATEGORIES.keys()),
                inline=False
            )
            await ctx.send(embed=embed)
            return
        
        # Validate category
        if category and category.lower() not in self.CATEGORIES:
            await ctx.send(f"Invalid category. Available: {', '.join(self.CATEGORIES.keys())}")
            return
        
        category = category.lower() if category else 'general'
        
        # Get description
        embed = discord.Embed(
            title="Ticket Creation - Description",
            description="Please describe your issue in detail.",
            color=0x7289da
        )
        await ctx.send(embed=embed)
        
        try:
            msg = await self.bot.wait_for(
                'message',
                check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
                timeout=300.0
            )
            description = msg.content
        except asyncio.TimeoutError:
            await ctx.send("Ticket creation timed out.")
            return
        
        # Create ticket
        ticket_number = self.get_next_ticket_number(ctx.guild.id)
        ticket_id = self.db.create_ticket(
            ticket_number=ticket_number,
            guild_id=ctx.guild.id,
            creator_id=ctx.author.id,
            category=category,
            title=title,
            description=description,
            priority='medium'
        )
        
        if not ticket_id:
            await ctx.send("Failed to create ticket. Please try again.")
            return
        
        # Create private ticket channel
        try:
            # Get moderator role or use current guild roles
            support_role = discord.utils.find(
                lambda r: r.name.lower() in ['support', 'staff', 'moderator'],
                ctx.guild.roles
            ) or ctx.guild.default_role
            
            # Create channel
            overwrites = {
                ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                self.bot.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                support_role: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
            
            channel = await ctx.guild.create_text_channel(
                name=f"ticket-{ticket_number.lower()}",
                overwrites=overwrites,
                category=discord.utils.get(ctx.guild.categories, name='tickets') or None
            )
            
            # Update ticket with channel ID
            self.db.update_ticket(ticket_id, channel_id=channel.id)
            
            # Send initial message in ticket channel
            embed = discord.Embed(
                title=f"Ticket #{ticket_number}",
                description=title,
                color=self.STATUSES['open']
            )
            embed.add_field(name="Category", value=category.capitalize(), inline=True)
            embed.add_field(name="Status", value="Open", inline=True)
            embed.add_field(name="Priority", value="Medium", inline=True)
            embed.add_field(name="Creator", value=f"{ctx.author.mention}", inline=True)
            embed.add_field(name="Description", value=description, inline=False)
            embed.timestamp = datetime.utcnow()
            
            await channel.send(embed=embed)
            
            # Create action buttons
            view = TicketActionView(self, ticket_id)
            await channel.send(view=view)
            
            # Notify creator
            embed = discord.Embed(
                title="Ticket Created",
                description=f"Your ticket has been created successfully!",
                color=0x00ff00
            )
            embed.add_field(name="Ticket Number", value=f"`{ticket_number}`", inline=False)
            embed.add_field(name="Channel", value=channel.mention, inline=False)
            embed.add_field(name="Status", value="Open - Awaiting staff", inline=False)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Failed to create ticket channel: {e}")
            await ctx.send(f"Ticket created ({ticket_number}) but failed to create channel: {e}")
    
    @commands.command(name="tickets", description="View your tickets")
    async def tickets_list(self, ctx):
        """List user's tickets."""
        tickets = self.db.get_user_tickets(ctx.guild.id, ctx.author.id)
        
        if not tickets:
            await ctx.send("You don't have any tickets.")
            return
        
        embed = discord.Embed(
            title=f"Your Tickets",
            description=f"You have {len(tickets)} ticket(s)",
            color=0x7289da
        )
        
        for ticket in tickets:
            status_color = self.STATUSES.get(ticket['status'], 0x7289da)
            status_str = ticket['status'].replace('-', ' ').title()
            
            value = f"Status: **{status_str}**\n"
            value += f"Category: **{ticket['category'].capitalize()}**\n"
            value += f"Priority: **{ticket['priority'].capitalize()}**\n"
            
            if ticket['assignee_id']:
                value += f"Assigned to: <@{ticket['assignee_id']}>\n"
            
            embed.add_field(
                name=f"#{ticket['ticket_number']}",
                value=value,
                inline=False
            )
        
        embed.set_footer(text=f"Use !ticket-info <ticket_number> for details")
        await ctx.send(embed=embed)
    
    @commands.command(name="ticket-info", description="Get ticket information")
    async def ticket_info(self, ctx, ticket_number: str):
        """Get detailed ticket information."""
        ticket = self.db.get_ticket_by_number(ticket_number)
        
        if not ticket:
            await ctx.send(f"Ticket {ticket_number} not found.")
            return
        
        # Check permissions
        if (ticket['creator_id'] != ctx.author.id and
            ticket['assignee_id'] != ctx.author.id and
            not ctx.author.guild_permissions.manage_messages):
            await ctx.send("You don't have permission to view this ticket.")
            return
        
        status_color = self.STATUSES.get(ticket['status'], 0x7289da)
        priority_color = self.PRIORITY_COLORS.get(ticket['priority'], 0x7289da)
        
        embed = discord.Embed(
            title=f"Ticket #{ticket['ticket_number']}",
            description=ticket['title'],
            color=status_color
        )
        
        embed.add_field(name="Status", value=ticket['status'].replace('-', ' ').title(), inline=True)
        embed.add_field(name="Priority", value=ticket['priority'].capitalize(), inline=True)
        embed.add_field(name="Category", value=ticket['category'].capitalize(), inline=True)
        
        embed.add_field(name="Creator", value=f"<@{ticket['creator_id']}>", inline=True)
        
        if ticket['assignee_id']:
            embed.add_field(name="Assigned to", value=f"<@{ticket['assignee_id']}>", inline=True)
        
        embed.add_field(name="Description", value=ticket['description'] or "No description", inline=False)
        
        created_at = datetime.fromisoformat(ticket['created_at'])
        embed.add_field(name="Created", value=f"<t:{int(created_at.timestamp())}:R>", inline=True)
        
        if ticket['closed_at']:
            closed_at = datetime.fromisoformat(ticket['closed_at'])
            embed.add_field(name="Closed", value=f"<t:{int(closed_at.timestamp())}:R>", inline=True)
        
        # Get notes
        notes = self.db.get_notes(ticket['id'])
        if notes:
            notes_text = f"**{len(notes)} note(s)**"
            embed.add_field(name="Notes/Comments", value=notes_text, inline=False)
        
        # Get rating if exists
        rating = self.db.get_rating(ticket['id'])
        if rating and rating['rating']:
            embed.add_field(name="Satisfaction Rating", value=f"⭐ {rating['rating']}/5", inline=True)
        
        await ctx.send(embed=embed)
    
    @commands.command(name="ticket-note", description="Add note to ticket")
    async def ticket_note(self, ctx, ticket_number: str, *, content: str):
        """Add a note/comment to a ticket."""
        ticket = self.db.get_ticket_by_number(ticket_number)
        
        if not ticket:
            await ctx.send(f"Ticket {ticket_number} not found.")
            return
        
        # Check permissions
        if (ticket['creator_id'] != ctx.author.id and
            ticket['assignee_id'] != ctx.author.id and
            not ctx.author.guild_permissions.manage_messages):
            await ctx.send("You don't have permission to add notes to this ticket.")
            return
        
        # Add note
        note_id = self.db.add_note(ticket['id'], ctx.author.id, content)
        
        if note_id:
            embed = discord.Embed(
                title="Note Added",
                description=content,
                color=0x00ff00
            )
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
            embed.timestamp = datetime.utcnow()
            
            # Send in ticket channel if exists
            if ticket['channel_id']:
                try:
                    channel = self.bot.get_channel(ticket['channel_id'])
                    if channel:
                        await channel.send(embed=embed)
                except:
                    pass
            
            await ctx.send(embed=embed)
        else:
            await ctx.send("Failed to add note.")
    
    @commands.command(name="ticket-claim", description="Claim a ticket (staff only)")
    @commands.has_permissions(manage_messages=True)
    async def ticket_claim(self, ctx, ticket_number: str):
        """Claim a ticket as support staff."""
        ticket = self.db.get_ticket_by_number(ticket_number)
        
        if not ticket:
            await ctx.send(f"Ticket {ticket_number} not found.")
            return
        
        # Check if already claimed
        active_claim = self.db.get_active_claim(ticket['id'])
        if active_claim and active_claim['claimer_id'] != ctx.author.id:
            claimer = self.bot.get_user(active_claim['claimer_id'])
            await ctx.send(f"This ticket is already claimed by {claimer.mention}")
            return
        
        # Claim ticket
        if self.db.claim_ticket(ticket['id'], ctx.author.id):
            embed = discord.Embed(
                title="Ticket Claimed",
                description=f"Claimed by {ctx.author.mention}",
                color=0x00ff00
            )
            
            await ctx.send(embed=embed)
            
            # Notify in ticket channel
            if ticket['channel_id']:
                try:
                    channel = self.bot.get_channel(ticket['channel_id'])
                    if channel:
                        await channel.send(embed=embed)
                except:
                    pass
        else:
            await ctx.send("Failed to claim ticket.")
    
    @commands.command(name="ticket-assign", description="Assign ticket to staff member")
    @commands.has_permissions(manage_messages=True)
    async def ticket_assign(self, ctx, ticket_number: str, member: discord.Member):
        """Assign a ticket to a staff member."""
        ticket = self.db.get_ticket_by_number(ticket_number)
        
        if not ticket:
            await ctx.send(f"Ticket {ticket_number} not found.")
            return
        
        if self.db.update_ticket(ticket['id'], assignee_id=member.id):
            embed = discord.Embed(
                title="Ticket Assigned",
                description=f"Assigned to {member.mention}",
                color=0x00ff00
            )
            
            await ctx.send(embed=embed)
            
            # Notify in ticket channel
            if ticket['channel_id']:
                try:
                    channel = self.bot.get_channel(ticket['channel_id'])
                    if channel:
                        await channel.send(embed=embed)
                except:
                    pass
        else:
            await ctx.send("Failed to assign ticket.")
    
    @commands.command(name="ticket-close", description="Close a ticket")
    @commands.has_permissions(manage_messages=True)
    async def ticket_close(self, ctx, ticket_number: str, *, reason: str = "No reason provided"):
        """Close a ticket and optionally save transcript."""
        ticket = self.db.get_ticket_by_number(ticket_number)
        
        if not ticket:
            await ctx.send(f"Ticket {ticket_number} not found.")
            return
        
        if ticket['status'] == 'closed':
            await ctx.send("This ticket is already closed.")
            return
        
        # Update status
        self.db.update_ticket(
            ticket['id'],
            status='closed',
            closed_at=datetime.utcnow().isoformat()
        )
        
        # Get notes for transcript
        notes = self.db.get_notes(ticket['id'])
        transcript = f"Ticket: {ticket['ticket_number']}\n"
        transcript += f"Created: {ticket['created_at']}\n"
        transcript += f"Closed: {datetime.utcnow().isoformat()}\n"
        transcript += f"Creator: {ticket['creator_id']}\n"
        transcript += f"Title: {ticket['title']}\n\n"
        
        if notes:
            transcript += "=== CONVERSATION ===\n"
            for note in notes:
                timestamp = datetime.fromisoformat(note['created_at']).strftime("%Y-%m-%d %H:%M:%S")
                transcript += f"[{timestamp}] <@{note['author_id']}>: {note['content']}\n"
        
        # Save transcript
        self.db.save_transcript(ticket['id'], transcript)
        
        embed = discord.Embed(
            title="Ticket Closed",
            description=reason,
            color=0xff0000
        )
        embed.add_field(name="Ticket", value=f"`{ticket_number}`", inline=False)
        embed.add_field(name="Closed by", value=ctx.author.mention, inline=False)
        
        await ctx.send(embed=embed)
        
        # Notify in ticket channel
        if ticket['channel_id']:
            try:
                channel = self.bot.get_channel(ticket['channel_id'])
                if channel:
                    await channel.send(embed=embed)
                    
                    # Ask for rating
                    rating_view = TicketRatingView(self, ticket['id'])
                    await channel.send(
                        "Please rate your experience with this ticket (1-5 stars):",
                        view=rating_view
                    )
            except:
                pass
    
    @commands.command(name="ticket-reopen", description="Reopen a closed ticket")
    async def ticket_reopen(self, ctx, ticket_number: str, *, reason: str = "No reason provided"):
        """Reopen a closed ticket."""
        ticket = self.db.get_ticket_by_number(ticket_number)
        
        if not ticket:
            await ctx.send(f"Ticket {ticket_number} not found.")
            return
        
        # Check permissions
        if (ticket['creator_id'] != ctx.author.id and
            not ctx.author.guild_permissions.manage_messages):
            await ctx.send("You don't have permission to reopen this ticket.")
            return
        
        if ticket['status'] != 'closed':
            await ctx.send("Only closed tickets can be reopened.")
            return
        
        self.db.update_ticket(ticket['id'], status='open', closed_at=None)
        
        embed = discord.Embed(
            title="Ticket Reopened",
            description=reason,
            color=0xff0000
        )
        embed.add_field(name="Ticket", value=f"`{ticket_number}`", inline=False)
        embed.add_field(name="Reopened by", value=ctx.author.mention, inline=False)
        
        await ctx.send(embed=embed)
        
        if ticket['channel_id']:
            try:
                channel = self.bot.get_channel(ticket['channel_id'])
                if channel:
                    await channel.send(embed=embed)
            except:
                pass
    
    @commands.command(name="ticket-status", description="Change ticket status")
    @commands.has_permissions(manage_messages=True)
    async def ticket_status(self, ctx, ticket_number: str, status: str):
        """Change ticket status."""
        if status.lower() not in self.STATUSES:
            valid = ", ".join(self.STATUSES.keys())
            await ctx.send(f"Invalid status. Valid: {valid}")
            return
        
        ticket = self.db.get_ticket_by_number(ticket_number)
        
        if not ticket:
            await ctx.send(f"Ticket {ticket_number} not found.")
            return
        
        self.db.update_ticket(ticket['id'], status=status.lower())
        
        embed = discord.Embed(
            title="Status Updated",
            description=f"Status changed to **{status.capitalize()}**",
            color=self.STATUSES[status.lower()]
        )
        
        await ctx.send(embed=embed)
        
        if ticket['channel_id']:
            try:
                channel = self.bot.get_channel(ticket['channel_id'])
                if channel:
                    await channel.send(embed=embed)
            except:
                pass
    
    @commands.command(name="ticket-stats", description="View ticket statistics")
    async def ticket_stats(self, ctx):
        """Display ticket statistics."""
        stats = self.db.get_stats(ctx.guild.id)
        
        embed = discord.Embed(
            title="Ticket Statistics",
            color=0x7289da
        )
        
        embed.add_field(name="Total Tickets", value=str(stats.get('total', 0)), inline=True)
        embed.add_field(name="Open", value=str(stats.get('open', 0)), inline=True)
        embed.add_field(name="In Progress", value=str(stats.get('in_progress', 0)), inline=True)
        embed.add_field(name="Closed", value=str(stats.get('closed', 0)), inline=True)
        
        avg_rating = stats.get('avg_satisfaction_rating', 0)
        embed.add_field(name="Avg Satisfaction", value=f"⭐ {avg_rating}/5", inline=True)
        
        avg_hours = stats.get('avg_resolution_hours', 0)
        hours = int(avg_hours)
        minutes = int((avg_hours % 1) * 60)
        embed.add_field(
            name="Avg Resolution Time",
            value=f"{hours}h {minutes}m",
            inline=True
        )
        
        embed.timestamp = datetime.utcnow()
        await ctx.send(embed=embed)
    
    @commands.command(name="panel-create", description="Create a ticket creation panel")
    @commands.has_permissions(manage_messages=True)
    async def panel_create(self, ctx):
        """Create an interactive ticket creation panel."""
        embed = discord.Embed(
            title="Support Ticket Panel",
            description="Click a button below to create a ticket.",
            color=0x7289da
        )
        
        embed.add_field(
            name="Choose a Category",
            value="\n".join(f"{emoji} {name.capitalize()}" for name, emoji in self.CATEGORIES.items()),
            inline=False
        )
        
        embed.set_footer(text="Your response will be handled by our support team.")
        
        view = PanelView(self)
        await ctx.send(embed=embed, view=view)


class TicketActionView(discord.ui.View):
    """View for ticket action buttons."""
    
    def __init__(self, cog: TicketingCog, ticket_id: int):
        super().__init__(timeout=None)
        self.cog = cog
        self.ticket_id = ticket_id
    
    @discord.ui.button(label="Add Note", style=discord.ButtonStyle.primary, emoji="📝")
    async def add_note_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Add a note to the ticket."""
        await interaction.response.send_modal(NoteModal(self.cog, self.ticket_id))
    
    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger, emoji="🔒")
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Close the ticket."""
        ticket = self.cog.db.get_ticket(self.ticket_id)
        
        if not ticket:
            await interaction.response.send_message("Ticket not found.", ephemeral=True)
            return
        
        # Check permissions
        if (interaction.user.id != ticket['creator_id'] and
            not interaction.user.guild_permissions.manage_messages):
            await interaction.response.send_message(
                "You don't have permission to close this ticket.",
                ephemeral=True
            )
            return
        
        self.cog.db.update_ticket(
            self.ticket_id,
            status='closed',
            closed_at=datetime.utcnow().isoformat()
        )
        
        embed = discord.Embed(
            title="Ticket Closed",
            color=0xff0000
        )
        
        await interaction.response.send_message(embed=embed)


class NoteModal(discord.ui.Modal, title="Add Note"):
    """Modal for adding notes to tickets."""
    
    content = discord.ui.TextInput(
        label="Note Content",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=4000
    )
    
    def __init__(self, cog: TicketingCog, ticket_id: int):
        super().__init__()
        self.cog = cog
        self.ticket_id = ticket_id
    
    async def on_submit(self, interaction: discord.Interaction):
        """Submit the note."""
        ticket = self.cog.db.get_ticket(self.ticket_id)
        
        # Add note to database
        self.cog.db.add_note(self.ticket_id, interaction.user.id, self.content.value)
        
        embed = discord.Embed(
            title="Note Added",
            description=self.content.value,
            color=0x00ff00
        )
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        embed.timestamp = datetime.utcnow()
        
        await interaction.response.send_message(embed=embed)


class TicketRatingView(discord.ui.View):
    """View for ticket satisfaction rating."""
    
    def __init__(self, cog: TicketingCog, ticket_id: int):
        super().__init__(timeout=None)
        self.cog = cog
        self.ticket_id = ticket_id
    
    @discord.ui.button(label="1 Star", style=discord.ButtonStyle.primary)
    async def rate_1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._handle_rating(interaction, 1)
    
    @discord.ui.button(label="2 Stars", style=discord.ButtonStyle.primary)
    async def rate_2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._handle_rating(interaction, 2)
    
    @discord.ui.button(label="3 Stars", style=discord.ButtonStyle.primary)
    async def rate_3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._handle_rating(interaction, 3)
    
    @discord.ui.button(label="4 Stars", style=discord.ButtonStyle.primary)
    async def rate_4(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._handle_rating(interaction, 4)
    
    @discord.ui.button(label="5 Stars", style=discord.ButtonStyle.success)
    async def rate_5(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._handle_rating(interaction, 5)
    
    async def _handle_rating(self, interaction: discord.Interaction, rating: int):
        """Handle rating submission."""
        ticket = self.cog.db.get_ticket(self.ticket_id)
        
        if not ticket or ticket['creator_id'] != interaction.user.id:
            await interaction.response.send_message(
                "You don't have permission to rate this ticket.",
                ephemeral=True
            )
            return
        
        self.cog.db.add_rating(self.ticket_id, interaction.user.id, rating)
        
        embed = discord.Embed(
            title="Rating Submitted",
            description=f"Thank you for rating this ticket: {'⭐' * rating}",
            color=0x00ff00
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


class PanelView(discord.ui.View):
    """View for ticket creation panel with category buttons."""
    
    def __init__(self, cog: TicketingCog):
        super().__init__(timeout=None)
        self.cog = cog
        
        # Add buttons for each category
        for category, emoji in cog.CATEGORIES.items():
            button = discord.ui.Button(
                label=category.capitalize(),
                emoji=emoji,
                style=discord.ButtonStyle.primary
            )
            button.callback = self._create_callback(category)
            self.add_item(button)
    
    def _create_callback(self, category: str):
        """Create callback for category button."""
        async def callback(interaction: discord.Interaction):
            await interaction.response.send_modal(
                TicketCreationModal(self.cog, category)
            )
        return callback


class TicketCreationModal(discord.ui.Modal):
    """Modal for creating tickets from panel."""
    
    def __init__(self, cog: TicketingCog, category: str):
        super().__init__(title=f"Create {category.capitalize()} Ticket")
        self.cog = cog
        self.category = category
        
        self.title_input = discord.ui.TextInput(
            label="Ticket Title",
            style=discord.TextStyle.short,
            required=True,
            max_length=100
        )
        
        self.description_input = discord.ui.TextInput(
            label="Description",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=4000
        )
        
        self.add_item(self.title_input)
        self.add_item(self.description_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        """Submit ticket creation."""
        ticket_number = self.cog.get_next_ticket_number(interaction.guild.id)
        ticket_id = self.cog.db.create_ticket(
            ticket_number=ticket_number,
            guild_id=interaction.guild.id,
            creator_id=interaction.user.id,
            category=self.category,
            title=self.title_input.value,
            description=self.description_input.value,
            priority='medium'
        )
        
        if not ticket_id:
            await interaction.response.send_message(
                "Failed to create ticket.",
                ephemeral=True
            )
            return
        
        # Create private ticket channel
        try:
            support_role = discord.utils.find(
                lambda r: r.name.lower() in ['support', 'staff', 'moderator'],
                interaction.guild.roles
            ) or interaction.guild.default_role
            
            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                self.cog.bot.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                support_role: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
            
            channel = await interaction.guild.create_text_channel(
                name=f"ticket-{ticket_number.lower()}",
                overwrites=overwrites,
                category=discord.utils.get(interaction.guild.categories, name='tickets')
            )
            
            self.cog.db.update_ticket(ticket_id, channel_id=channel.id)
            
            # Send initial message
            embed = discord.Embed(
                title=f"Ticket #{ticket_number}",
                description=self.title_input.value,
                color=self.cog.STATUSES['open']
            )
            embed.add_field(name="Category", value=self.category.capitalize(), inline=True)
            embed.add_field(name="Status", value="Open", inline=True)
            embed.add_field(name="Priority", value="Medium", inline=True)
            embed.add_field(name="Creator", value=interaction.user.mention, inline=True)
            embed.add_field(name="Description", value=self.description_input.value, inline=False)
            embed.timestamp = datetime.utcnow()
            
            await channel.send(embed=embed)
            
            # Add action buttons
            view = TicketActionView(self.cog, ticket_id)
            await channel.send(view=view)
            
            await interaction.response.send_message(
                f"✅ Ticket created! {channel.mention}",
                ephemeral=True
            )
            
        except Exception as e:
            logger.error(f"Failed to create ticket channel: {e}")
            await interaction.response.send_message(
                f"Ticket created but failed to create channel: {e}",
                ephemeral=True
            )


async def setup(bot):
    """Setup function for the cog."""
    await bot.add_cog(TicketingCog(bot))
