
# tg-textgame-bot
A semi-automated bot for a text-based Telegram game.

---

# 🎮 HalfBot: Semi-Automated Telegram Text-Based Game Bot

> ⚔️ Dominate, Declare, and Deploy — all within your Telegram group.

📘 Available in other languages:
🇮🇷 [نسخه فارسی](./README.fa.md)

---

## 📌 Overview

**HalfBot** is a semi-automated Telegram bot for managing a **text-based strategy war game**. It empowers users to:
- ⚔️ Conduct military invasions
- 🚀 Launch missile strikes
- 📢 Publish public statements
- 👑 Assign “Lords” in Telegram groups

This bot is designed for use **only in Telegram supergroups**, offering a fun, role-based system of interaction, announcements, and strategic decision-making.

---

## 🚀 Features

- ✅ Admin commands to toggle features
- 📢 Statement broadcast system with preview and approval
- 🚀 Missile attack planner with multi-step inputs
- ⚔️ Army deployment system (Ground, Naval, Aerial)
- 👑 Group-specific lord assignment system
- 🗃 SQLite3 database integration
- 🖼 Visual feedback using images and styled HTML formatting

---

## 🛠 Setup Instructions

### 1. Clone the repository:
```bash
git clone https://github.com/Milo-MILords/tg-textgame-bot.git
cd tg-textgame-bot
```

### 2. Install required dependencies:

```bash
pip install pyTelegramBotAPI
```

### 3. Configure your settings:

* Replace `'YOUR TOKEN'` in the script with your [Telegram Bot Token](https://t.me/BotFather)
* Set your `ADMIN_ID` values (Telegram user IDs with bot control permissions)
* Set the `CHANNEL_ID` and `CHANNEL_ID1` for statement and attack broadcasts

---

## 🧪 Usage

### 🔧 Admin Commands

| Command             | Function                      |
| ------------------- | ----------------------------- |
| `/on` / `/off`      | Enable/disable the bot        |
| `/statement_on/off` | Toggle statement system       |
| `/mooshak_on/off`   | Toggle missile attack system  |
| `/lashkar_on/off`   | Toggle army deployment system |
| `/setlord`          | Set a user as group lord      |
| `/unsetlord`        | Remove a user's lord status   |

> 📝 `setlord` and `unsetlord` must be used as a **reply** to a user's message in group.

---

### 🎮 Player Interaction

Players interact with the bot by typing `پنل` in the group, which opens a control panel:

* 🙌 Submit Statements
* 🚀 Launch Missile Attacks
* ⚔️ Initiate Military Deployment
* 🚨 Issue Direct Attack Orders

---

## 🗃 Database Schema

SQLite3 database file: `game_bot.db`

| Table   | Fields                |
| ------- | --------------------- |
| `users` | `user_id`, `group_id` |

---

## 🌍 Localization

* 🔤 All bot replies and buttons are fully **localized in Persian (Farsi)** for immersive gameplay.
* ✅ HTML-based formatting for messages (e.g., `<blockquote>`, `<b>`, emojis)

---

## ✅ Example Preview

Here's how a missile attack summary looks in a group:

```
✅حمله موشکی به پایان رسید.

🚀 نوع موشک: شهاب ۳  
📍 کشور مقصد: ایران  
🏙 شهر مقصد: تبریز  
🔢 تعداد موشک‌های شلیک شده: ۵
```

And the statement is posted with formatted attribution to the group's lord 👑.

---

## 📜 License

MIT License - free to use, modify, and expand for your group’s gameplay!
