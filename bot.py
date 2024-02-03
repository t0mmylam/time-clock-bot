import os
import discord
from datetime import datetime
from dotenv import load_dotenv
import sqlite3

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.typing = True
intents.members = True  # Enable intents for accessing member information
bot = discord.Client(intents=intents)

# Database setup
conn = sqlite3.connect('timeclock.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS timeclock (
        user_id TEXT PRIMARY KEY,
        check_in TIMESTAMP,
        total_time INTEGER DEFAULT 0,
        total_checkins INTEGER DEFAULT 0,
        last_checkout TIMESTAMP
    )
''')
conn.commit()

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith('!check-in'):
        now = datetime.now()
        cursor.execute('''
            INSERT INTO timeclock (user_id, check_in)
            VALUES (?, ?)
            ON CONFLICT(user_id)
            DO UPDATE SET check_in = ?
        ''', (str(message.author.id), now, now))
        conn.commit()
        await message.channel.send(f'Check-in recorded at {now.strftime("%Y-%m-%d %H:%M:%S")}')

    elif message.content == '!check-out':
        cursor.execute('SELECT check_in FROM timeclock WHERE user_id = ?', (str(message.author.id),))
        check_in_time = cursor.fetchone()
        if check_in_time:
            check_in_time = datetime.fromisoformat(check_in_time[0])
            now = datetime.now()
            duration = now - check_in_time
            cursor.execute('''
                UPDATE timeclock
                SET total_time = total_time + ?,
                    total_checkins = total_checkins + 1,
                    check_in = NULL
                WHERE user_id = ?
            ''', (duration.seconds, str(message.author.id)))
            conn.commit()
            await message.channel.send(f'Check-out recorded at {now.strftime("%Y-%m-%d %H:%M:%S")}. Session Duration: {duration.seconds} seconds')

    elif message.content.startswith('!stats'):
        args = message.content.split()
        user_id = str(message.author.id)
        if len(args) > 1:
            member_name = args[1]
            member = discord.utils.get(message.guild.members, name=member_name)
            if member:
                user_id = str(member.id)

        cursor.execute('SELECT total_time, total_checkins, last_checkout FROM timeclock WHERE user_id = ?', (user_id,))
        stats = cursor.fetchone()
        if stats:
            total_time, total_checkins, last_checkout = stats
            last_checkout_str = last_checkout.strftime("%Y-%m-%d %H:%M:%S") if last_checkout else "N/A"
            response = f'**Total Time**: {total_time} seconds\n**Total Check-Ins**: {total_checkins}\n**Last Check-Out**: {last_checkout_str}'
            await message.channel.send(response)

    elif message.content == '!leaderboard':
        cursor.execute('SELECT user_id, total_time, total_checkins FROM timeclock ORDER BY total_time DESC')
        leaderboard = cursor.fetchall()
        response = "**Leaderboard**:\n"
        for idx, (user_id, total_time, total_checkins) in enumerate(leaderboard, 1):
            member = await bot.fetch_user(user_id)
            response += f'{idx}. {member.name} - Total Time: {total_time} seconds, Total Check-Ins: {total_checkins}\n'
        await message.channel.send(response)

bot.run(TOKEN)