"""
Advanced Database Management for Giveaways and Logging
Handles SQLite-based storage for giveaway and log data.
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class AdvancedDatabase:
    """SQLite database for giveaway and logging management."""
    
    def __init__(self, db_path: str = "advanced.db"):
        """Initialize the database."""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Create necessary tables if they don't exist."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Giveaways table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS giveaways (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        giveaway_id TEXT UNIQUE NOT NULL,
                        guild_id INTEGER NOT NULL,
                        creator_id INTEGER NOT NULL,
                        message_id INTEGER,
                        channel_id INTEGER NOT NULL,
                        title TEXT NOT NULL,
                        description TEXT,
                        prizes TEXT NOT NULL,
                        winner_count INTEGER DEFAULT 1,
                        duration_seconds INTEGER NOT NULL,
                        entry_method TEXT DEFAULT 'button',
                        status TEXT DEFAULT 'active',
                        requires_roles TEXT,
                        exclude_roles TEXT,
                        min_account_age_days INTEGER,
                        min_server_join_days INTEGER,
                        blacklist_users TEXT,
                        whitelist_users TEXT,
                        blocked_users TEXT,
                        bonus_entries TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        ends_at TIMESTAMP,
                        paused_at TIMESTAMP,
                        resumed_at TIMESTAMP,
                        ended_at TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Giveaway entries table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS giveaway_entries (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        giveaway_id TEXT NOT NULL,
                        user_id INTEGER NOT NULL,
                        entry_count INTEGER DEFAULT 1,
                        entered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (giveaway_id) REFERENCES giveaways(giveaway_id),
                        UNIQUE(giveaway_id, user_id)
                    )
                ''')
                
                # Giveaway winners table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS giveaway_winners (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        giveaway_id TEXT NOT NULL,
                        user_id INTEGER NOT NULL,
                        prize TEXT NOT NULL,
                        position INTEGER,
                        claimed INTEGER DEFAULT 0,
                        claimed_at TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (giveaway_id) REFERENCES giveaways(giveaway_id)
                    )
                ''')
                
                # Giveaway templates table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS giveaway_templates (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        template_id TEXT UNIQUE NOT NULL,
                        guild_id INTEGER NOT NULL,
                        creator_id INTEGER NOT NULL,
                        name TEXT NOT NULL,
                        config TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Logs table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        guild_id INTEGER NOT NULL,
                        log_type TEXT NOT NULL,
                        action TEXT NOT NULL,
                        user_id INTEGER,
                        target_id INTEGER,
                        moderator_id INTEGER,
                        channel_id INTEGER,
                        message_id INTEGER,
                        before_state TEXT,
                        after_state TEXT,
                        details TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP
                    )
                ''')
                
                # Create indices for faster queries
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_giveaway_guild ON giveaways(guild_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_giveaway_status ON giveaways(status)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_entries_giveaway ON giveaway_entries(giveaway_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_winners_giveaway ON giveaway_winners(giveaway_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_guild ON logs(guild_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_type ON logs(log_type)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_user ON logs(user_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_created ON logs(created_at)')
                
                conn.commit()
                logger.info("Advanced database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize advanced database: {e}")
    
    # ========== GIVEAWAY OPERATIONS ==========
    
    def create_giveaway(
        self,
        giveaway_id: str,
        guild_id: int,
        creator_id: int,
        channel_id: int,
        title: str,
        prizes: List[str],
        duration_seconds: int,
        winner_count: int = 1,
        description: str = None,
        entry_method: str = "button",
        requires_roles: List[int] = None,
        exclude_roles: List[int] = None,
        min_account_age_days: int = None,
        min_server_join_days: int = None,
        whitelist_users: List[int] = None,
        blacklist_users: List[int] = None
    ) -> Optional[str]:
        """Create a new giveaway."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                from datetime import timedelta
                ends_at = (datetime.utcnow() + timedelta(seconds=duration_seconds)).isoformat()
                
                cursor.execute('''
                    INSERT INTO giveaways 
                    (giveaway_id, guild_id, creator_id, channel_id, title, description, prizes,
                     winner_count, duration_seconds, entry_method, requires_roles, exclude_roles,
                     min_account_age_days, min_server_join_days, whitelist_users, blacklist_users, ends_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    giveaway_id, guild_id, creator_id, channel_id, title, description,
                    json.dumps(prizes), winner_count, duration_seconds, entry_method,
                    json.dumps(requires_roles or []), json.dumps(exclude_roles or []),
                    min_account_age_days, min_server_join_days,
                    json.dumps(whitelist_users or []), json.dumps(blacklist_users or []),
                    ends_at
                ))
                conn.commit()
                logger.info(f"Created giveaway {giveaway_id}")
                return giveaway_id
        except Exception as e:
            logger.error(f"Failed to create giveaway: {e}")
            return None
    
    def get_giveaway(self, giveaway_id: str) -> Optional[Dict]:
        """Get giveaway by ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM giveaways WHERE giveaway_id = ?', (giveaway_id,))
                row = cursor.fetchone()
                if row:
                    data = dict(row)
                    # Parse JSON fields
                    data['prizes'] = json.loads(data['prizes'])
                    data['requires_roles'] = json.loads(data['requires_roles'])
                    data['exclude_roles'] = json.loads(data['exclude_roles'])
                    data['whitelist_users'] = json.loads(data['whitelist_users'])
                    data['blacklist_users'] = json.loads(data['blacklist_users'])
                    data['bonus_entries'] = json.loads(data['bonus_entries'] or '{}')
                    return data
                return None
        except Exception as e:
            logger.error(f"Failed to get giveaway: {e}")
            return None
    
    def update_giveaway(self, giveaway_id: str, **kwargs) -> bool:
        """Update giveaway fields."""
        try:
            valid_fields = {
                'title', 'description', 'status', 'message_id', 'paused_at',
                'resumed_at', 'ended_at', 'bonus_entries', 'blocked_users'
            }
            updates = {k: v for k, v in kwargs.items() if k in valid_fields}
            
            if not updates:
                return False
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                updates['updated_at'] = datetime.utcnow().isoformat()
                
                # Handle JSON fields
                if 'bonus_entries' in updates:
                    updates['bonus_entries'] = json.dumps(updates['bonus_entries'])
                if 'blocked_users' in updates:
                    updates['blocked_users'] = json.dumps(updates['blocked_users'])
                
                set_clause = ', '.join(f'{k} = ?' for k in updates.keys())
                values = list(updates.values()) + [giveaway_id]
                
                cursor.execute(f'UPDATE giveaways SET {set_clause} WHERE giveaway_id = ?', values)
                conn.commit()
                logger.info(f"Updated giveaway {giveaway_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to update giveaway: {e}")
            return False
    
    def get_active_giveaways(self, guild_id: int) -> List[Dict]:
        """Get all active giveaways for a guild."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT * FROM giveaways WHERE guild_id = ? AND status = ? ORDER BY created_at DESC',
                    (guild_id, 'active')
                )
                results = []
                for row in cursor.fetchall():
                    data = dict(row)
                    data['prizes'] = json.loads(data['prizes'])
                    results.append(data)
                return results
        except Exception as e:
            logger.error(f"Failed to get active giveaways: {e}")
            return []
    
    def add_entry(self, giveaway_id: str, user_id: int, bonus_count: int = 1) -> bool:
        """Add an entry to a giveaway."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Check if user already has entry
                cursor.execute(
                    'SELECT id, entry_count FROM giveaway_entries WHERE giveaway_id = ? AND user_id = ?',
                    (giveaway_id, user_id)
                )
                existing = cursor.fetchone()
                
                if existing:
                    new_count = existing[1] + bonus_count
                    cursor.execute(
                        'UPDATE giveaway_entries SET entry_count = ? WHERE giveaway_id = ? AND user_id = ?',
                        (new_count, giveaway_id, user_id)
                    )
                else:
                    cursor.execute(
                        'INSERT INTO giveaway_entries (giveaway_id, user_id, entry_count) VALUES (?, ?, ?)',
                        (giveaway_id, user_id, bonus_count)
                    )
                
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to add entry: {e}")
            return False
    
    def get_entries(self, giveaway_id: str) -> List[Dict]:
        """Get all entries for a giveaway."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT * FROM giveaway_entries WHERE giveaway_id = ?',
                    (giveaway_id,)
                )
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get entries: {e}")
            return []
    
    def add_winner(self, giveaway_id: str, user_id: int, prize: str, position: int) -> bool:
        """Add a winner to a giveaway."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO giveaway_winners (giveaway_id, user_id, prize, position) VALUES (?, ?, ?, ?)',
                    (giveaway_id, user_id, prize, position)
                )
                conn.commit()
                logger.info(f"Added winner {user_id} to giveaway {giveaway_id}")
                return True
        except Exception as e:
            logger.error(f"Failed to add winner: {e}")
            return False
    
    def get_winners(self, giveaway_id: str) -> List[Dict]:
        """Get all winners for a giveaway."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT * FROM giveaway_winners WHERE giveaway_id = ? ORDER BY position ASC',
                    (giveaway_id,)
                )
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get winners: {e}")
            return []
    
    def get_user_wins(self, guild_id: int, user_id: int) -> int:
        """Get number of wins for a user in a guild."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT COUNT(*) FROM giveaway_winners gw
                    JOIN giveaways g ON gw.giveaway_id = g.giveaway_id
                    WHERE g.guild_id = ? AND gw.user_id = ?
                ''', (guild_id, user_id))
                return cursor.fetchone()[0] or 0
        except Exception as e:
            logger.error(f"Failed to get user wins: {e}")
            return 0
    
    def save_template(self, template_id: str, guild_id: int, creator_id: int, name: str, config: Dict) -> bool:
        """Save a giveaway template."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO giveaway_templates (template_id, guild_id, creator_id, name, config)
                    VALUES (?, ?, ?, ?, ?)
                ''', (template_id, guild_id, creator_id, name, json.dumps(config)))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to save template: {e}")
            return False
    
    def get_templates(self, guild_id: int) -> List[Dict]:
        """Get all templates for a guild."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM giveaway_templates WHERE guild_id = ?', (guild_id,))
                results = []
                for row in cursor.fetchall():
                    data = dict(row)
                    data['config'] = json.loads(data['config'])
                    results.append(data)
                return results
        except Exception as e:
            logger.error(f"Failed to get templates: {e}")
            return []
    
    # ========== LOGGING OPERATIONS ==========
    
    def add_log(
        self,
        guild_id: int,
        log_type: str,
        action: str,
        user_id: int = None,
        target_id: int = None,
        moderator_id: int = None,
        channel_id: int = None,
        message_id: int = None,
        before_state: str = None,
        after_state: str = None,
        details: str = None,
        expires_at: datetime = None
    ) -> Optional[int]:
        """Add a log entry."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO logs
                    (guild_id, log_type, action, user_id, target_id, moderator_id, 
                     channel_id, message_id, before_state, after_state, details, expires_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    guild_id, log_type, action, user_id, target_id, moderator_id,
                    channel_id, message_id, before_state, after_state, details,
                    expires_at.isoformat() if expires_at else None
                ))
                conn.commit()
                logger.info(f"Added log: {log_type} - {action} in guild {guild_id}")
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Failed to add log: {e}")
            return None
    
    def search_logs(
        self,
        guild_id: int,
        log_type: str = None,
        user_id: int = None,
        action: str = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict]:
        """Search logs with filters."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                query = 'SELECT * FROM logs WHERE guild_id = ?'
                params = [guild_id]
                
                if log_type:
                    query += ' AND log_type = ?'
                    params.append(log_type)
                
                if user_id:
                    query += ' AND (user_id = ? OR target_id = ?)'
                    params.extend([user_id, user_id])
                
                if action:
                    query += ' AND action = ?'
                    params.append(action)
                
                query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
                params.extend([limit, offset])
                
                cursor.execute(query, params)
                results = []
                for row in cursor.fetchall():
                    data = dict(row)
                    if data['before_state']:
                        data['before_state'] = json.loads(data['before_state'])
                    if data['after_state']:
                        data['after_state'] = json.loads(data['after_state'])
                    if data['details']:
                        data['details'] = json.loads(data['details'])
                    results.append(data)
                return results
        except Exception as e:
            logger.error(f"Failed to search logs: {e}")
            return []
    
    def get_user_activity(self, guild_id: int, user_id: int, limit: int = 100) -> List[Dict]:
        """Get all activity for a specific user."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM logs 
                    WHERE guild_id = ? AND (user_id = ? OR target_id = ? OR moderator_id = ?)
                    ORDER BY created_at DESC LIMIT ?
                ''', (guild_id, user_id, user_id, user_id, limit))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get user activity: {e}")
            return []
    
    def get_log_stats(self, guild_id: int) -> Dict:
        """Get logging statistics for a guild."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total logs
                cursor.execute('SELECT COUNT(*) FROM logs WHERE guild_id = ?', (guild_id,))
                total_logs = cursor.fetchone()[0]
                
                # Logs by type
                cursor.execute('''
                    SELECT log_type, COUNT(*) as count FROM logs WHERE guild_id = ?
                    GROUP BY log_type
                ''', (guild_id,))
                logs_by_type = {row[0]: row[1] for row in cursor.fetchall()}
                
                # Recent activity (last 24 hours)
                cursor.execute('''
                    SELECT COUNT(*) FROM logs WHERE guild_id = ?
                    AND created_at > datetime('now', '-1 day')
                ''', (guild_id,))
                logs_24h = cursor.fetchone()[0]
                
                # Most common actions
                cursor.execute('''
                    SELECT action, COUNT(*) as count FROM logs WHERE guild_id = ?
                    GROUP BY action ORDER BY count DESC LIMIT 5
                ''', (guild_id,))
                top_actions = {row[0]: row[1] for row in cursor.fetchall()}
                
                return {
                    'total_logs': total_logs,
                    'logs_by_type': logs_by_type,
                    'logs_24h': logs_24h,
                    'top_actions': top_actions
                }
        except Exception as e:
            logger.error(f"Failed to get log stats: {e}")
            return {}
    
    def cleanup_expired_logs(self) -> int:
        """Delete expired logs and return count."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM logs WHERE expires_at IS NOT NULL AND expires_at < CURRENT_TIMESTAMP')
                conn.commit()
                deleted = cursor.rowcount
                logger.info(f"Cleaned up {deleted} expired logs")
                return deleted
        except Exception as e:
            logger.error(f"Failed to cleanup logs: {e}")
            return 0
    
    def export_logs(self, guild_id: int, format: str = 'json') -> Optional[str]:
        """Export logs to JSON or CSV format."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT * FROM logs WHERE guild_id = ? ORDER BY created_at DESC',
                    (guild_id,)
                )
                logs = [dict(row) for row in cursor.fetchall()]
                
                if format == 'json':
                    return json.dumps(logs, indent=2, default=str)
                elif format == 'csv':
                    import csv
                    import io
                    if not logs:
                        return None
                    
                    output = io.StringIO()
                    writer = csv.DictWriter(output, fieldnames=logs[0].keys())
                    writer.writeheader()
                    writer.writerows(logs)
                    return output.getvalue()
                
                return None
        except Exception as e:
            logger.error(f"Failed to export logs: {e}")
            return None
