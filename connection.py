import datetime
import telebot
import sqlite3
import pickle

register_gift = 30
every_month_minimum = 10

admins = [1806892656]


####################  BOT  ####################

bot = telebot.TeleBot('7861682510:AAED4ge7pQCZ8UFISGSm44NiWM2HgY6glQE', parse_mode='HTML')

kmarkup = telebot.types.InlineKeyboardMarkup
kbm = telebot.types.ReplyKeyboardMarkup
kbm_btn = telebot.types.KeyboardButton
btn = telebot.types.InlineKeyboardButton


####################  DATABASE  ####################

class Database:
    def __init__(self):
        self.db = None
        self.sql = None

    def connect(self):
        self.db = sqlite3.connect('database.db')
        self.sql = self.db.cursor()

    def close(self):
        for i in [self.sql, self.db]:
            try:
                i.close()
            except:
                pass

    def __enter__(self):
        self.connect()
        return self.db, self.sql

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class UserDB:
    def __init__(self, user_id=None, balance=None, last_message=None, reg_date=None, status=None):
        self.user_id = user_id
        self.balance = balance
        self.last_message = last_message
        self.reg_date = reg_date
        self.status = status

    def exists(self) -> bool:
        with Database() as (db, sql):
            if self.user_id:
                sql.execute("SELECT * FROM users WHERE user_id=?", (self.user_id,))
                return bool(sql.fetchone())
            return False
        
    def get(self):
        with Database() as (db, sql):
            if self.user_id:
                sql.execute("SELECT * FROM users WHERE user_id=?", (self.user_id,))
                result = sql.fetchone()
                if result:
                    return UserDB(*result)
            elif self.status:
                sql.execute("SELECT * FROM users WHERE status=?", (self.status,))
                result = sql.fetchone()
                if result:
                    sql.execute("SELECT * FROM users WHERE status=?", (self.status,))
                    return [UserDB(*i) for i in sql.fetchall()]
            return None

    def get_all(self):
        with Database() as (db, sql):
            sql.execute("SELECT * FROM users")
            return [UserDB(*i) for i in sql.fetchall()]

    def add(self) -> None:
        with Database() as (db, sql):
            sql.execute("INSERT INTO users (user_id, balance, last_message, reg_date, status) VALUES (?, ?, ?, ?, ?)", (self.user_id, str(register_gift), self.last_message, str(datetime.datetime.now()), "regular"))
            db.commit()

    def update(self) -> None:
        with Database() as (db, sql):
            if self.balance:
                sql.execute("UPDATE users SET balance=? WHERE user_id=?", (self.balance, self.user_id))
            if self.last_message:
                sql.execute("UPDATE users SET last_message=? WHERE user_id=?", (self.last_message, self.user_id))
            if self.status:
                sql.execute("UPDATE users SET status=? WHERE user_id=?", (self.status, self.user_id))
            db.commit()


class Language:
    def __init__(self, user_id):
        self.user_id = user_id
        self.lang = "ru"

    def get(self):
        with Database() as (db, sql):
            sql.execute("SELECT * FROM lang WHERE user_id=?", (self.user_id,))
            result = sql.fetchone()
            if result:
                return result[1]
            return self.lang

    def set(self, lang):
        with Database() as (db, sql):
            sql.execute("SELECT * FROM lang WHERE user_id=?", (self.user_id,))
            if sql.fetchone() is None:
                sql.execute("INSERT INTO lang (user_id, lang) VALUES (?, ?)", (self.user_id, lang))
            else:
                sql.execute("UPDATE lang SET lang=? WHERE user_id=?", (lang, self.user_id))
            db.commit()
    

class Stage:
    def __init__(self, user_id):
        self.user_id = user_id
        self.stage = None

    def get(self):
        with Database() as (db, sql):
            sql.execute("SELECT * FROM stages WHERE user_id=?", (self.user_id,))
            result = sql.fetchone()
            if result:
                return result[1]
            return "None"

    def set(self, stage):
        with Database() as (db, sql):
            sql.execute("SELECT * FROM stages WHERE user_id=?", (self.user_id,))
            if sql.fetchone() is None:
                sql.execute("INSERT INTO stages (user_id, stage) VALUES (?, ?)", (self.user_id, stage))
            else:
                sql.execute("UPDATE stages SET stage=? WHERE user_id=?", (stage, self.user_id))
            db.commit()


class ConversationDB:
    def __init__(self, conversation_id=None, user_id=None, conversation_title=None):
        self.conversation_id = conversation_id
        self.user_id = user_id
        self.conversation_title = conversation_title

    def new(self):
        with Database() as (db, sql):
            sql.execute("INSERT INTO conversations (conversation_id, user_id, conversation_title) VALUES (?, ?, ?)", (self.conversation_id, self.user_id, self.conversation_title))
            db.commit()

    def update(self):
        with Database() as (db, sql):
            sql.execute("UPDATE conversations SET conversation_title=? WHERE conversation_id=?", (self.conversation_title, self.conversation_id))
            db.commit()

    def get(self):
        with Database() as (db, sql):
            if self.conversation_id:
                sql.execute("SELECT * FROM conversations WHERE conversation_id=?", (self.conversation_id,))
                result = sql.fetchone()
                if result:
                    return ConversationDB(*result)
            elif self.user_id:
                sql.execute("SELECT * FROM conversations WHERE user_id=?", (self.user_id,))
                return [ConversationDB(*i) for i in sql.fetchall()]
            return None

    def delete(self):
        with Database() as (db, sql):
            sql.execute("DELETE FROM conversations WHERE conversation_id=?", (self.conversation_id,))
            db.commit()


def prepare_db():
    with Database() as (db, sql):
        sql.execute("""CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            balance INTEGER DEFAULT 0,
            last_message TEXT,
            reg_date TEXT,
            status TEXT
        )""")
        sql.execute("""CREATE TABLE IF NOT EXISTS lang (
            user_id TEXT PRIMARY KEY,
            lang TEXT
        )""")
        sql.execute("""CREATE TABLE IF NOT EXISTS stages (
            user_id TEXT PRIMARY KEY,
            stage TEXT
        )""")
        sql.execute("""CREATE TABLE IF NOT EXISTS conversations (
            conversation_id TEXT PRIMARY KEY,
            user_id TEXT,
            conversation_title TEXT
        )""")
        db.commit()


prepare_db()


def unpick(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)


def pick(filename, obj):
    with open(filename, 'wb') as f:
        pickle.dump(obj, f)
