import os
import discord
from datetime import datetime
from dotenv import load_dotenv
import sqlite3

load_dotenv()
TOKEN = os.environ["TOKEN"]

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.typing = True
intents.members = True
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
        last_checkout TIMESTAMP,
        last_session_time TEXT
    )
''')
conn.commit()

def isCheckedIn(user_id) -> bool:
    cursor.execute('SELECT check_in FROM timeclock WHERE user_id = ?', (user_id,))
    check_in_time = cursor.fetchone()
    return check_in_time is not None

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith('!check-in'):
        if isCheckedIn(str(message.author.id)):
            await message.channel.send(f"<@{str(message.author.id)}> is already checked in.")
            return
        
        now = datetime.now()
        cursor.execute('''
            INSERT INTO timeclock (user_id, check_in)
            VALUES (?, ?)
            ON CONFLICT(user_id)
            DO UPDATE SET check_in = ?
        ''', (str(message.author.id), now, now))
        conn.commit()
        embed = discord.Embed(title="Check-In", description=f"<@{str(message.author.id)}> has checked in.", color=0x00ff00)
        embed.add_field(name="Time", value=now.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
        await message.channel.send(embed=embed)


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
                    check_in = NULL,
                    last_checkout = ?,
                    last_session_time = ?
                WHERE user_id = ?
            ''', (duration.seconds, now, str(duration), str(message.author.id)))
            conn.commit()
            embed = discord.Embed(title="Check-Out", description=f"<@{str(message.author.id)}>'s session has ended.", color=0xff0000)
            embed.add_field(name="Check-out Time", value=now.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
            embed.add_field(name="Session Duration", value=f"{duration.seconds} seconds", inline=True)
            await message.channel.send(embed=embed)
    
    elif message.content.startswith('!stats'):
        args = message.content.split()
        user_id = str(message.author.id)

        if len(args) > 1:
            mention = args[1]
            # Strip characters to get the user ID from the mention
            mentioned_id = mention.strip('<@!>')
            member = message.guild.get_member(int(mentioned_id))
            if member:
                user_id = str(member.id)

        cursor.execute('SELECT total_time, total_checkins, last_checkout, last_session_time FROM timeclock WHERE user_id = ?', (user_id,))
        stats = cursor.fetchone()
        if stats:
            total_time, total_checkins, last_checkout_str, last_session_time = stats
            if last_checkout_str:
                last_checkout = datetime.fromisoformat(last_checkout_str)
                last_checkout_str = last_checkout.strftime("%Y-%m-%d %H:%M:%S")
            else:
                last_checkout_str = "N/A"

            embed = discord.Embed(title="User Statistics", description=f"Stats for <@{user_id}>", color=0x00ff00)
            embed.add_field(name="Total Time", value=f"{total_time} seconds", inline=True)
            embed.add_field(name="Total Check-Ins", value=str(total_checkins), inline=True)
            embed.add_field(name="Last Check-Out", value=last_checkout_str, inline=False)
            embed.add_field(name="Last Session Time", value=last_session_time, inline=False)
            await message.channel.send(embed=embed)

    elif message.content == '!leaderboard':
        cursor.execute('SELECT user_id, total_time, total_checkins FROM timeclock ORDER BY total_time DESC')
        leaderboard = cursor.fetchall()
        embed = discord.Embed(title="Leaderboard", description="Top Users by Total Time", color=0xffc0cb)
        for idx, (user_id, total_time, total_checkins) in enumerate(leaderboard, 1):
            member = await bot.fetch_user(user_id)
            embed.add_field(name=f"{idx}. {str(member.display_name)}", value=f"Total Time: {total_time} seconds, Total Check-Ins: {total_checkins}", inline=False)
        await message.channel.send(embed=embed)

bot.run(TOKEN)