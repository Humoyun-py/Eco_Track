import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self, db_path="../eco.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables - web bilan bir xil database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Web ilova bilan bir xil jadvallar
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                email TEXT,
                password_hash TEXT,
                role TEXT DEFAULT 'child',
                coins INTEGER DEFAULT 0,
                energy INTEGER DEFAULT 100,
                streak INTEGER DEFAULT 0,
                last_login TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS telegram_user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE,
                user_id INTEGER,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_user_by_telegram_id(self, telegram_id):
        """Get user by telegram ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT u.* FROM user u 
            JOIN telegram_user tu ON u.id = tu.user_id 
            WHERE tu.telegram_id = ?
        ''', (telegram_id,))
        user = cursor.fetchone()
        
        conn.close()
        return user
    
    def create_telegram_user(self, telegram_user_data, username=None):
        """Create new telegram user with registration"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Avval telegram foydalanuvchi mavjudligini tekshirish
        cursor.execute('SELECT * FROM telegram_user WHERE telegram_id = ?', (telegram_user_data['id'],))
        existing_user = cursor.fetchone()
        
        if existing_user:
            conn.close()
            return False  # Foydalanuvchi allaqachon mavjud
        
        # Yangi user yaratish (coins 0 bilan)
        cursor.execute('''
            INSERT INTO user (username, email, password_hash, role, coins, energy, streak)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            f"tg_{telegram_user_data['id']}",
            f"tg_{telegram_user_data['id']}@ecoverse.com",
            'telegram_user',  # Maxsus parol hash
            'child',
            0,  # Coins 0 dan boshlanadi
            100,
            0
        ))
        
        user_id = cursor.lastrowid
        
        # Telegram user yaratish
        cursor.execute('''
            INSERT INTO telegram_user (telegram_id, user_id, username, first_name, last_name)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            telegram_user_data['id'],
            user_id,
            telegram_user_data.get('username'),
            telegram_user_data.get('first_name'),
            telegram_user_data.get('last_name')
        ))
        
        conn.commit()
        conn.close()
        return True
    
    def update_user_coins(self, user_id, coins):
        """Update user coins"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE user SET coins = ? WHERE id = ?', (coins, user_id))
        
        conn.commit()
        conn.close()
    
    def get_user_stats(self, user_id):
        """Get user statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT coins, energy, streak FROM user WHERE id = ?', (user_id,))
        stats = cursor.fetchone()
        
        conn.close()
        return stats