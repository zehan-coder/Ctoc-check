"""
Ticket Database Management
Handles SQLite-based storage for tickets and related data.
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class TicketDatabase:
    """SQLite database for ticket management."""
    
    def __init__(self, db_path: str = None):
        """Initialize the database."""
        if db_path is None:
            # Create data directory if it doesn't exist
            Path("data").mkdir(exist_ok=True)
            db_path = "data/tickets.db"
        else:
            # Create parent directories for custom paths
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Create necessary tables if they don't exist."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Tickets table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS tickets (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ticket_number TEXT UNIQUE NOT NULL,
                        guild_id INTEGER NOT NULL,
                        creator_id INTEGER NOT NULL,
                        category TEXT NOT NULL,
                        priority TEXT DEFAULT 'medium',
                        status TEXT DEFAULT 'open',
                        title TEXT NOT NULL,
                        description TEXT,
                        assignee_id INTEGER,
                        channel_id INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        closed_at TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Ticket notes/comments table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS ticket_notes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ticket_id INTEGER NOT NULL,
                        author_id INTEGER NOT NULL,
                        content TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (ticket_id) REFERENCES tickets(id)
                    )
                ''')
                
                # Ticket claims table (for staff to claim tickets)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS ticket_claims (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ticket_id INTEGER NOT NULL,
                        claimer_id INTEGER NOT NULL,
                        claimed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        released_at TIMESTAMP,
                        FOREIGN KEY (ticket_id) REFERENCES tickets(id)
                    )
                ''')
                
                # Ticket transcripts (saved history)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS ticket_transcripts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ticket_id INTEGER NOT NULL,
                        transcript TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (ticket_id) REFERENCES tickets(id)
                    )
                ''')
                
                # User ratings/feedback
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS ticket_ratings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ticket_id INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                        rating INTEGER,
                        feedback TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (ticket_id) REFERENCES tickets(id)
                    )
                ''')
                
                # User profile/stats
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_profiles (
                        user_id INTEGER PRIMARY KEY,
                        guild_id INTEGER NOT NULL,
                        tickets_created INTEGER DEFAULT 0,
                        avg_satisfaction_rating REAL DEFAULT 0,
                        last_activity TIMESTAMP,
                        UNIQUE(user_id, guild_id)
                    )
                ''')
                
                conn.commit()
                logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
    
    # ========== TICKET OPERATIONS ==========
    
    def create_ticket(
        self,
        ticket_number: str,
        guild_id: int,
        creator_id: int,
        category: str,
        title: str,
        description: str = None,
        priority: str = "medium",
        channel_id: int = None
    ) -> Optional[int]:
        """Create a new ticket."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO tickets 
                    (ticket_number, guild_id, creator_id, category, title, description, priority, channel_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (ticket_number, guild_id, creator_id, category, title, description, priority, channel_id))
                conn.commit()
                
                ticket_id = cursor.lastrowid
                logger.info(f"Created ticket #{ticket_number} (ID: {ticket_id})")
                return ticket_id
        except Exception as e:
            logger.error(f"Failed to create ticket: {e}")
            return None
    
    def get_ticket(self, ticket_id: int) -> Optional[Dict]:
        """Get ticket by ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM tickets WHERE id = ?', (ticket_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Failed to get ticket: {e}")
            return None
    
    def get_ticket_by_number(self, ticket_number: str) -> Optional[Dict]:
        """Get ticket by ticket number."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM tickets WHERE ticket_number = ?', (ticket_number,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Failed to get ticket by number: {e}")
            return None
    
    def update_ticket(self, ticket_id: int, **kwargs) -> bool:
        """Update ticket fields."""
        try:
            valid_fields = {
                'status', 'priority', 'assignee_id', 'title', 'description', 'closed_at'
            }
            updates = {k: v for k, v in kwargs.items() if k in valid_fields}
            
            if not updates:
                return False
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                updates['updated_at'] = datetime.utcnow().isoformat()
                
                set_clause = ', '.join(f'{k} = ?' for k in updates.keys())
                values = list(updates.values()) + [ticket_id]
                
                cursor.execute(f'UPDATE tickets SET {set_clause} WHERE id = ?', values)
                conn.commit()
                logger.info(f"Updated ticket ID: {ticket_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to update ticket: {e}")
            return False
    
    def get_guild_tickets(self, guild_id: int, status: Optional[str] = None) -> List[Dict]:
        """Get all tickets for a guild, optionally filtered by status."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                if status:
                    cursor.execute(
                        'SELECT * FROM tickets WHERE guild_id = ? AND status = ? ORDER BY created_at DESC',
                        (guild_id, status)
                    )
                else:
                    cursor.execute(
                        'SELECT * FROM tickets WHERE guild_id = ? ORDER BY created_at DESC',
                        (guild_id,)
                    )
                
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get guild tickets: {e}")
            return []
    
    def get_user_tickets(self, guild_id: int, creator_id: int) -> List[Dict]:
        """Get all tickets created by a user in a guild."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT * FROM tickets WHERE guild_id = ? AND creator_id = ? ORDER BY created_at DESC',
                    (guild_id, creator_id)
                )
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get user tickets: {e}")
            return []
    
    def get_assigned_tickets(self, assignee_id: int, status: Optional[str] = None) -> List[Dict]:
        """Get all tickets assigned to a user."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                if status:
                    cursor.execute(
                        'SELECT * FROM tickets WHERE assignee_id = ? AND status = ? ORDER BY created_at DESC',
                        (assignee_id, status)
                    )
                else:
                    cursor.execute(
                        'SELECT * FROM tickets WHERE assignee_id = ? ORDER BY created_at DESC',
                        (assignee_id,)
                    )
                
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get assigned tickets: {e}")
            return []
    
    def get_stats(self, guild_id: int) -> Dict:
        """Get ticket statistics for a guild."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total tickets
                cursor.execute('SELECT COUNT(*) FROM tickets WHERE guild_id = ?', (guild_id,))
                total = cursor.fetchone()[0]
                
                # Open tickets
                cursor.execute('SELECT COUNT(*) FROM tickets WHERE guild_id = ? AND status = ?', (guild_id, 'open'))
                open_tickets = cursor.fetchone()[0]
                
                # In-progress tickets
                cursor.execute('SELECT COUNT(*) FROM tickets WHERE guild_id = ? AND status = ?', (guild_id, 'in-progress'))
                in_progress = cursor.fetchone()[0]
                
                # Closed tickets
                cursor.execute('SELECT COUNT(*) FROM tickets WHERE guild_id = ? AND status = ?', (guild_id, 'closed'))
                closed = cursor.fetchone()[0]
                
                # Average satisfaction rating
                cursor.execute('SELECT AVG(rating) FROM ticket_ratings WHERE ticket_id IN (SELECT id FROM tickets WHERE guild_id = ?)', (guild_id,))
                avg_rating = cursor.fetchone()[0] or 0
                
                # Average resolution time
                cursor.execute('''
                    SELECT AVG(CAST((julianday(closed_at) - julianday(created_at)) AS REAL))
                    FROM tickets
                    WHERE guild_id = ? AND closed_at IS NOT NULL
                ''', (guild_id,))
                avg_resolution_hours = (cursor.fetchone()[0] or 0) * 24
                
                return {
                    'total': total,
                    'open': open_tickets,
                    'in_progress': in_progress,
                    'closed': closed,
                    'avg_satisfaction_rating': round(avg_rating, 2),
                    'avg_resolution_hours': round(avg_resolution_hours, 2)
                }
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {}
    
    # ========== TICKET NOTES ==========
    
    def add_note(self, ticket_id: int, author_id: int, content: str) -> Optional[int]:
        """Add a note/comment to a ticket."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO ticket_notes (ticket_id, author_id, content) VALUES (?, ?, ?)',
                    (ticket_id, author_id, content)
                )
                conn.commit()
                logger.info(f"Added note to ticket ID: {ticket_id}")
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Failed to add note: {e}")
            return None
    
    def get_notes(self, ticket_id: int) -> List[Dict]:
        """Get all notes for a ticket."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT * FROM ticket_notes WHERE ticket_id = ? ORDER BY created_at ASC',
                    (ticket_id,)
                )
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get notes: {e}")
            return []
    
    # ========== TICKET CLAIMS ==========
    
    def claim_ticket(self, ticket_id: int, claimer_id: int) -> bool:
        """Claim a ticket for support staff."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO ticket_claims (ticket_id, claimer_id) VALUES (?, ?)',
                    (ticket_id, claimer_id)
                )
                # Also update assignee
                cursor.execute('UPDATE tickets SET assignee_id = ? WHERE id = ?', (claimer_id, ticket_id))
                conn.commit()
                logger.info(f"Ticket ID {ticket_id} claimed by user {claimer_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to claim ticket: {e}")
            return False
    
    def get_active_claim(self, ticket_id: int) -> Optional[Dict]:
        """Get active claim for a ticket."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT * FROM ticket_claims WHERE ticket_id = ? AND released_at IS NULL',
                    (ticket_id,)
                )
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Failed to get active claim: {e}")
            return None
    
    def release_claim(self, claim_id: int) -> bool:
        """Release a ticket claim."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'UPDATE ticket_claims SET released_at = CURRENT_TIMESTAMP WHERE id = ?',
                    (claim_id,)
                )
                conn.commit()
                logger.info(f"Released claim ID: {claim_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to release claim: {e}")
            return False
    
    # ========== RATINGS & FEEDBACK ==========
    
    def add_rating(self, ticket_id: int, user_id: int, rating: int, feedback: str = None) -> bool:
        """Add satisfaction rating and feedback for a ticket."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO ticket_ratings (ticket_id, user_id, rating, feedback) VALUES (?, ?, ?, ?)',
                    (ticket_id, user_id, rating, feedback)
                )
                conn.commit()
                logger.info(f"Added rating {rating} for ticket ID: {ticket_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to add rating: {e}")
            return False
    
    def get_rating(self, ticket_id: int) -> Optional[Dict]:
        """Get rating for a ticket."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM ticket_ratings WHERE ticket_id = ?', (ticket_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Failed to get rating: {e}")
            return None
    
    # ========== TRANSCRIPTS ==========
    
    def save_transcript(self, ticket_id: int, transcript: str) -> bool:
        """Save transcript for a closed ticket."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO ticket_transcripts (ticket_id, transcript) VALUES (?, ?)',
                    (ticket_id, transcript)
                )
                conn.commit()
                logger.info(f"Saved transcript for ticket ID: {ticket_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to save transcript: {e}")
            return False
    
    def get_transcript(self, ticket_id: int) -> Optional[str]:
        """Get transcript for a ticket."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT transcript FROM ticket_transcripts WHERE ticket_id = ?', (ticket_id,))
                row = cursor.fetchone()
                return row[0] if row else None
        except Exception as e:
            logger.error(f"Failed to get transcript: {e}")
            return None
