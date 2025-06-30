# 🎮 HalfBot: Semi-Automated Telegram Text-Based Game Bot
⚔️ Dominate, Declare, and Deploy — all within your Telegram group.

A semi-automated bot for a text-based Telegram strategy game.

---

### 🌍 Languages
This bot is available in multiple languages.
* 🇬🇧 **English (Current)**
* 🇮🇷 [Persian Version (نسخه فارسی)](README.fa.md)

### 📌 Overview
HalfBot is a semi-automated Telegram bot for managing a text-based strategy war game. It empowers users, designated as "Lords," to perform strategic actions within their groups. It is designed for use only in Telegram supergroups.

Key actions include:
* ⚔️ **Conducting Military Marches:** Move troops across a virtual map.
* 🚀 **Launching Missile Strikes:** Execute targeted attacks.
* 📢 **Publishing Statements:** Broadcast official announcements to a public channel.
* 👑 **Assigning Lords:** Admins can grant users special command privileges.

### 🚀 Features
* ✅ **Admin Controls:** Easily toggle main features on or off.
* 📢 **Statement System:** A broadcast system with previews and a confirmation step.
* 🚀 **Missile Attack Planner:** A guided, multi-step process for launching missile strikes.
* ⚔️ **Military Deployment System:** Plan and announce Ground, Naval, or Aerial movements.
* 👑 **Lord System:** A group-specific role system to grant command access to users.
* 🗃 **Database Integration:** Uses SQLite3 to persist user and group data.
* 🖼 **Rich Formatting:** Provides clear visual feedback using images and styled HTML messages.

### 🛠 Setup Instructions

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/Milo-MILords/tg-textgame-bot.git](https://github.com/Milo-MILords/tg-textgame-bot.git)
    cd tg-textgame-bot
    ```

2.  **Install required dependencies:**
    ```bash
    pip install pyTelegramBotAPI
    ```

3.  **Configure your settings in `halfbot.en.py`:**
    * Replace `'YOUR TOKEN'` with your actual Telegram Bot Token.
    * Set your `ADMIN_ID` values (a list of Telegram user IDs with bot control permissions).
    * Set the `CHANNEL_ID` for statements and `CHANNEL_ID1` for attack/march broadcasts.

### 🧪 Usage

#### 🔧 Admin Commands
| Command               | Function                                           |
| --------------------- | -------------------------------------------------- |
| `/on` / `/off`        | Globally enable or disable the bot.                |
| `/statement_on/off`   | Toggle the statement system.                       |
| `/missile_on/off`     | Toggle the missile attack system.                  |
| `/marching_on/off`    | Toggle the military marching & attack order system.|
| `/setlord`            | Set a user as the group's lord.                    |
| `/unsetlord`          | Remove a user's lord status.                       |

**Note:** `/setlord` and `/unsetlord` must be used as a reply to another user's message in the group.

#### 🎮 Player Interaction
Registered "Lords" can interact with the bot by typing **`panel`** in the group chat. This opens a control panel with the following options:

* 🙌 **Submit Statement:** Publish an official announcement.
* 🚀 **Launch Missile Attack:** Begin the process of a missile strike.
* ⚔️ **Initiate Marching:** Deploy troops to a new location.
* 🚨 **Issue Attack Order:** Command your deployed troops to attack.

### 🗃 Database Schema
* **Database file:** `game_bot.db`
* **Table:** `users`
    * `user_id` (INTEGER, PRIMARY KEY): The Telegram user ID of the Lord.
    * `group_id` (INTEGER): The ID of the group where the user is a Lord.

### ✅ Example Preview
Here's how a missile attack summary looks after being sent to the channel:

> ☠️ The country USA has launched a missile attack on the country Russia
> <blockquote>
> 🏢• City: Moscow
> 🚀• Missile Type: Tomahawk
> 🚀• Number of Missiles Fired: 5
> </blockquote>
> 🔥Responsible for this attack: [Commander's Name]

### 📜 License
This project is licensed under the **MIT License**. Feel free to use, modify, and expand upon it for your own gameplay!
