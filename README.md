# Time Clock Bot

## Overview
This Discord bot is designed to provide simple time tracking functionality for users in a Discord server. This was made for a friend who needed to track the working hours of their contractors for their online business. It allows users to check in and check out, tracking their total time spent and the number of check-ins. The bot also provides a leaderboard to display top users by total time and individual user statistics. 

## Features
- **Check-In/Check-Out**: Users can record their session start and end times.
- **User Statistics**: Displays total time, total check-ins, last check-out, and last session time for a user.
- **Leaderboard**: Shows a leaderboard of users sorted by total time.
- **Discord Embeds**: Responses are formatted with Discord Embeds for better readability.

## Setup and Installation
1. **Install Dependencies**: Run `pip install -r requirements.txt`.
2. **Environment Variables**: Create a `.env` file in the root directory with your Discord bot token:
```TOKEN=your_discord_bot_token```
3. **Database Initialization**: The script will automatically create the `timeclock` table in `timeclock.db` if it doesn't exist.
4. **Deployment**: Read [here](https://medium.com/analytics-vidhya/how-to-host-a-discord-py-bot-on-heroku-and-github-d54a4d62a99e) to host your bot in heroku.

## Running the Bot Locally
Execute the bot by running `python main.py`. Ensure the bot token is correctly set in the `.env` file.

## Bot Commands
- `!check-in`: Record the current time as the user's check-in time.
- `!check-out`: Calculate and record the session duration since the last check-in.
- `!stats [@user]`: Display the total time, total check-ins, last check-out, and last session time. If `@user` is not specified, display stats for the message author.
- `!leaderboard`: Display a leaderboard of users by total time.

## Deployment
This bot is configured for deployment on Heroku. The `Procfile` in the directory specifies the command to run the bot on Heroku.

---
