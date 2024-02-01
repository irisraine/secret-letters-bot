# Secret Letters Bot

## Description

The Secret Letters Bot is a Discord bot designed to spread love and joy on the special occasions. This bot allows 
users to send anonymous private messages with greetings to their friends, crushes, or anyone they appreciate within 
the Discord server. Users can compose their messages ahead of time, and the bot will store them in a database to be 
automatically sent on given date.
By default, the bot settings are set to send messages on Valentine's Day, but you can change this via admin panel. 

## Features

- **Anonymity**: Senders' identities are kept confidential to maintain the surprise and fun of receiving an anonymous message.
- **Scheduled Delivery**: Messages are stored securely and sent out on Valentine's Day, ensuring timely delivery of warm wishes.
- **Custom Greetings**: Users can personalize their messages, making each greeting unique and heartfelt.
- **Easy to Use**: The bot provides simple interface for users to write and submit their Valentine's messages.

## Commands

- `!start_secret_letters` command - to publish the main menu of the bot.
- `!admin_secret_letters` command - to call the admin panel to set bot settings.

## Usage

Please make sure to specify the DISCORD_BOT_TOKEN environment variable.
Here is an example:
```
# Bot token
DISCORD_BOT_TOKEN='your-discord-bot-token-here'
```