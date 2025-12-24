import os
from abc import ABC, abstractmethod
from typing import List, Any, Optional
from config import DB_URI, DB_NAME, DB_TYPE  # Add DB_TYPE to config

# Abstract Base Class for Database Operations
class DatabaseInterface(ABC):
    @abstractmethod
    async def present_user(self, user_id: int) -> bool:
        pass
    
    @abstractmethod
    async def add_user(self, user_id: int):
        pass
    
    @abstractmethod
    async def full_userbase(self) -> List[int]:
        pass
    
    @abstractmethod
    async def del_user(self, user_id: int):
        pass
    
    @abstractmethod
    def get_setting(self, key: str, default=None) -> Any:
        pass
    
    @abstractmethod
    def update_setting(self, key: str, value: Any):
        pass
    
    @abstractmethod
    async def close(self):
        pass


# MongoDB Implementation
class MongoDatabase(DatabaseInterface):
    def __init__(self, uri: str, db_name: str):
        import pymongo
        self.client = pymongo.MongoClient(uri)
        self.database = self.client[db_name]
        self.user_data = self.database['users']
        self.settings_collection = self.database['settings']
    
    async def present_user(self, user_id: int) -> bool:
        found = self.user_data.find_one({'_id': user_id})
        return bool(found)
    
    async def add_user(self, user_id: int):
        self.user_data.insert_one({'_id': user_id})
    
    async def full_userbase(self) -> List[int]:
        user_docs = self.user_data.find()
        return [doc['_id'] for doc in user_docs]
    
    async def del_user(self, user_id: int):
        self.user_data.delete_one({'_id': user_id})
    
    def get_setting(self, key: str, default=None) -> Any:
        setting = self.settings_collection.find_one({'_id': key})
        if setting:
            return setting.get('value', default)
        return default
    
    def update_setting(self, key: str, value: Any):
        self.settings_collection.update_one(
            {'_id': key},
            {'$set': {'value': value}},
            upsert=True
        )
    
    async def close(self):
        self.client.close()


# PostgreSQL Implementation (NeonDB, Supabase, etc.)
class PostgreSQLDatabase(DatabaseInterface):
    def __init__(self, uri: str, db_name: str = None):
        import asyncpg
        import json
        self.uri = uri
        self.pool = None
        self.json = json
        self._asyncpg = asyncpg
    
    async def _ensure_pool(self):
        if self.pool is None:
            self.pool = await self._asyncpg.create_pool(self.uri)
            await self._create_tables()
    
    async def _create_tables(self):
        async with self.pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY
                )
            ''')
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value JSONB
                )
            ''')
    
    async def present_user(self, user_id: int) -> bool:
        await self._ensure_pool()
        async with self.pool.acquire() as conn:
            result = await conn.fetchval(
                'SELECT 1 FROM users WHERE user_id = $1',
                user_id
            )
            return result is not None
    
    async def add_user(self, user_id: int):
        await self._ensure_pool()
        async with self.pool.acquire() as conn:
            await conn.execute(
                'INSERT INTO users (user_id) VALUES ($1) ON CONFLICT DO NOTHING',
                user_id
            )
    
    async def full_userbase(self) -> List[int]:
        await self._ensure_pool()
        async with self.pool.acquire() as conn:
            rows = await conn.fetch('SELECT user_id FROM users')
            return [row['user_id'] for row in rows]
    
    async def del_user(self, user_id: int):
        await self._ensure_pool()
        async with self.pool.acquire() as conn:
            await conn.execute('DELETE FROM users WHERE user_id = $1', user_id)
    
    def get_setting(self, key: str, default=None) -> Any:
        import asyncio
        return asyncio.run(self._get_setting_async(key, default))
    
    async def _get_setting_async(self, key: str, default=None) -> Any:
        await self._ensure_pool()
        async with self.pool.acquire() as conn:
            result = await conn.fetchval(
                'SELECT value FROM settings WHERE key = $1',
                key
            )
            return self.json.loads(result) if result else default
    
    def update_setting(self, key: str, value: Any):
        import asyncio
        asyncio.run(self._update_setting_async(key, value))
    
    async def _update_setting_async(self, key: str, value: Any):
        await self._ensure_pool()
        async with self.pool.acquire() as conn:
            await conn.execute(
                '''INSERT INTO settings (key, value) VALUES ($1, $2)
                   ON CONFLICT (key) DO UPDATE SET value = $2''',
                key, self.json.dumps(value)
            )
    
    async def close(self):
        if self.pool:
            await self.pool.close()


# MySQL Implementation
class MySQLDatabase(DatabaseInterface):
    def __init__(self, uri: str, db_name: str = None):
        import aiomysql
        import json
        from urllib.parse import urlparse
        
        self.json = json
        self._aiomysql = aiomysql
        
        # Parse the URI
        parsed = urlparse(uri)
        self.config = {
            'host': parsed.hostname,
            'port': parsed.port or 3306,
            'user': parsed.username,
            'password': parsed.password,
            'db': db_name or parsed.path.lstrip('/'),
        }
        self.pool = None
    
    async def _ensure_pool(self):
        if self.pool is None:
            self.pool = await self._aiomysql.create_pool(**self.config)
            await self._create_tables()
    
    async def _create_tables(self):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id BIGINT PRIMARY KEY
                    )
                ''')
                await cursor.execute('''
                    CREATE TABLE IF NOT EXISTS settings (
                        `key` VARCHAR(255) PRIMARY KEY,
                        value JSON
                    )
                ''')
                await conn.commit()
    
    async def present_user(self, user_id: int) -> bool:
        await self._ensure_pool()
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    'SELECT 1 FROM users WHERE user_id = %s',
                    (user_id,)
                )
                result = await cursor.fetchone()
                return result is not None
    
    async def add_user(self, user_id: int):
        await self._ensure_pool()
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    'INSERT IGNORE INTO users (user_id) VALUES (%s)',
                    (user_id,)
                )
                await conn.commit()
    
    async def full_userbase(self) -> List[int]:
        await self._ensure_pool()
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute('SELECT user_id FROM users')
                rows = await cursor.fetchall()
                return [row[0] for row in rows]
    
    async def del_user(self, user_id: int):
        await self._ensure_pool()
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute('DELETE FROM users WHERE user_id = %s', (user_id,))
                await conn.commit()
    
    def get_setting(self, key: str, default=None) -> Any:
        import asyncio
        return asyncio.run(self._get_setting_async(key, default))
    
    async def _get_setting_async(self, key: str, default=None) -> Any:
        await self._ensure_pool()
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute('SELECT value FROM settings WHERE `key` = %s', (key,))
                result = await cursor.fetchone()
                return self.json.loads(result[0]) if result else default
    
    def update_setting(self, key: str, value: Any):
        import asyncio
        asyncio.run(self._update_setting_async(key, value))
    
    async def _update_setting_async(self, key: str, value: Any):
        await self._ensure_pool()
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    '''INSERT INTO settings (`key`, value) VALUES (%s, %s)
                       ON DUPLICATE KEY UPDATE value = %s''',
                    (key, self.json.dumps(value), self.json.dumps(value))
                )
                await conn.commit()
    
    async def close(self):
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()


# SQLite Implementation
class SQLiteDatabase(DatabaseInterface):
    def __init__(self, uri: str, db_name: str = None):
        import aiosqlite
        import json
        self.db_path = db_name or 'bot_data.db'
        self.json = json
        self._aiosqlite = aiosqlite
        self.connection = None
    
    async def _ensure_connection(self):
        if self.connection is None:
            self.connection = await self._aiosqlite.connect(self.db_path)
            await self._create_tables()
    
    async def _create_tables(self):
        await self.connection.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY
            )
        ''')
        await self.connection.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        await self.connection.commit()
    
    async def present_user(self, user_id: int) -> bool:
        await self._ensure_connection()
        cursor = await self.connection.execute(
            'SELECT 1 FROM users WHERE user_id = ?',
            (user_id,)
        )
        result = await cursor.fetchone()
        return result is not None
    
    async def add_user(self, user_id: int):
        await self._ensure_connection()
        await self.connection.execute(
            'INSERT OR IGNORE INTO users (user_id) VALUES (?)',
            (user_id,)
        )
        await self.connection.commit()
    
    async def full_userbase(self) -> List[int]:
        await self._ensure_connection()
        cursor = await self.connection.execute('SELECT user_id FROM users')
        rows = await cursor.fetchall()
        return [row[0] for row in rows]
    
    async def del_user(self, user_id: int):
        await self._ensure_connection()
        await self.connection.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
        await self.connection.commit()
    
    def get_setting(self, key: str, default=None) -> Any:
        import asyncio
        return asyncio.run(self._get_setting_async(key, default))
    
    async def _get_setting_async(self, key: str, default=None) -> Any:
        await self._ensure_connection()
        cursor = await self.connection.execute(
            'SELECT value FROM settings WHERE key = ?',
            (key,)
        )
        result = await cursor.fetchone()
        return self.json.loads(result[0]) if result else default
    
    def update_setting(self, key: str, value: Any):
        import asyncio
        asyncio.run(self._update_setting_async(key, value))
    
    async def _update_setting_async(self, key: str, value: Any):
        await self._ensure_connection()
        await self.connection.execute(
            'INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)',
            (key, self.json.dumps(value))
        )
        await self.connection.commit()
    
    async def close(self):
        if self.connection:
            await self.connection.close()


# Factory function to create the appropriate database instance
def create_database(db_type: str = None, uri: str = None, db_name: str = None) -> DatabaseInterface:
    db_type = db_type or DB_TYPE or 'mongodb'
    uri = uri or DB_URI
    db_name = db_name or DB_NAME
    
    db_type = db_type.lower()
    
    if db_type in ['mongodb', 'mongo']:
        return MongoDatabase(uri, db_name)
    elif db_type in ['postgresql', 'postgres', 'neondb', 'neon', 'supabase']:
        return PostgreSQLDatabase(uri, db_name)
    elif db_type in ['mysql', 'mariadb']:
        return MySQLDatabase(uri, db_name)
    elif db_type in ['sqlite', 'sqlite3']:
        return SQLiteDatabase(uri, db_name)
    else:
        raise ValueError(f"Unsupported database type: {db_type}")


# Initialize the database instance
database = create_database()

# Wrapper functions for backward compatibility
async def present_user(user_id: int) -> bool:
    return await database.present_user(user_id)

async def add_user(user_id: int):
    return await database.add_user(user_id)

async def full_userbase() -> List[int]:
    return await database.full_userbase()

async def del_user(user_id: int):
    return await database.del_user(user_id)

def get_setting(key: str, default=None) -> Any:
    return database.get_setting(key, default)

def update_setting(key: str, value: Any):
    return database.update_setting(key, value)