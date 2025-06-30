import telebot
from telebot import types
import sqlite3

# Initialize the bot with your token
API_TOKEN = 'YOUR TOKEN'
ADMIN_ID = [11111111, 00000000]
CHANNEL_ID = "STATEMENT CHANNEL"  # Channel for statements
CHANNEL_ID1 = "MARCHING CHANNEL" # Channel for military movements
bot = telebot.TeleBot(API_TOKEN)

# Initialize the database
conn = sqlite3.connect('game_bot.db', check_same_thread=False)
cursor = conn.cursor()

# Create the necessary tables
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                   user_id INTEGER PRIMARY KEY,
                   group_id INTEGER
                   )''')
conn.commit()

user_context = {}


def is_group_chat(message):
    return message.chat.type in ['supergroup']


# --- Bot Status Flags ---
bot_enabled = True
statement_status = True
missile_status = True
marching_status = True


@bot.message_handler(commands=['on', 'off', 'statement_on', 'statement_off', 'missile_on',
                               'missile_off', 'marching_on', 'marching_off'])
def command_handler(message):
    global bot_enabled, statement_status, missile_status, marching_status
    if message.from_user.id in ADMIN_ID:
        command = message.text
        if command == '/on':
            bot_enabled = True
            bot.reply_to(message, "✅ Bot has been activated.")
        elif command == '/off':
            bot_enabled = False
            bot.reply_to(message, "❌ Bot has been deactivated.")
        elif command == '/statement_on':
            statement_status = True
            bot.reply_to(message, "✅ Statements have been enabled.")
        elif command == '/statement_off':
            statement_status = False
            bot.reply_to(message, "❌ Statements have been disabled.")
        elif command == '/missile_on':
            missile_status = True
            bot.reply_to(message, "✅ Missile attacks have been enabled.")
        elif command == '/missile_off':
            missile_status = False
            bot.reply_to(message, "❌ Missile attacks have been disabled.")
        elif command == '/marching_on':
            marching_status = True
            bot.reply_to(message, "✅ Military marching has been enabled.")
        elif command == '/marching_off':
            marching_status = False
            bot.reply_to(message, "❌ Military marching has been disabled.")


@bot.message_handler(commands=['setlord'])
def set_lord(message):
    if is_group_chat(message):
        if message.from_user.id in ADMIN_ID:
            if message.reply_to_message is None:
                bot.reply_to(message, "Please reply with this command to the message of the person you want to make a Lord.")
                return
            lord_user_id = message.reply_to_message.from_user.id
            cursor.execute("SELECT * FROM users WHERE user_id=?", (lord_user_id,))
            user = cursor.fetchone()
            if user:
                bot.reply_to(message, "The selected user is already registered as a Lord in a group.")
            else:
                cursor.execute(
                    "INSERT OR IGNORE INTO users (user_id, group_id) VALUES (?, ?)",
                    (lord_user_id, message.chat.id))
                conn.commit()
                bot.reply_to(message, "The selected user has been registered as a Lord in this group.")
        else:
            bot.reply_to(message, "Only admins can use this command.")
    else:
        bot.reply_to(message, "This command can only be used in groups.")


@bot.message_handler(commands=['unsetlord'])
def unset_lord(message):
    if is_group_chat(message):
        if message.from_user.id in ADMIN_ID:
            if message.reply_to_message is None:
                bot.reply_to(message,
                             "Please reply with this command to the message of the person you want to remove from being a Lord.")
                return
            lord_user_id = message.reply_to_message.from_user.id
            cursor.execute(
                "DELETE FROM users WHERE user_id = ? AND group_id = ?",
                (lord_user_id, message.chat.id))
            conn.commit()
            bot.reply_to(message, "The selected user has been removed from being a Lord in this group.")
        else:
            bot.reply_to(message, "Only admins can use this command.")
    else:
        bot.reply_to(message, "This command can only be used in groups.")


@bot.message_handler(func=lambda message: 'panel' in message.text.lower() and message.chat.type == 'supergroup')
def start(message):
    if is_group_chat(message):
        send_panel(message)
    else:
        bot.reply_to(message, "This bot can only be used in groups.")


def send_panel(message):
    user_id = message.from_user.id
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()
    if user:
        panel_buttons = [
            types.InlineKeyboardButton("🙌 Statement", callback_data='statement'),
            types.InlineKeyboardButton("🚀 Missile Attack", callback_data='missile_attack'),
            types.InlineKeyboardButton("⚔️ Marching", callback_data='marching'),
            types.InlineKeyboardButton("🚨 Attack Order", callback_data='attack'),
        ]
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(*panel_buttons)
        markup.add(types.InlineKeyboardButton("❌ Close Panel ❌", callback_data='close_panel'))
        try:
            bot.send_message(message.chat.id, "Welcome, Commander!", reply_markup=markup)
        except AttributeError:
            bot.send_message(message.message.chat.id, "Welcome, Commander!", reply_markup=markup)
    else:
        bot.reply_to(message, "You must first be registered as a Lord with /setlord.")


@bot.callback_query_handler(func=lambda call: bot_enabled)
def callback_query(call):
    user_id = call.from_user.id
    data_parts = call.data.split('_')
    action = data_parts[0]

    if action == 'close_panel':
        bot.edit_message_text("Panel closed successfully 😎.", call.message.chat.id, call.message.message_id,
                              reply_markup=None)
    elif action == 'marching':
        if marching_status:
            if len(data_parts) == 1:
                ask_for_marching_type(call.message)
            elif data_parts[1] == 'type':
                bot.delete_message(call.message.chat.id, call.message.message_id)
                handle_marching_type_selection(call)
            elif data_parts[1] == 'confirm':
                bot.delete_message(call.message.chat.id, call.message.message_id)
                send_marching_details(call.message, user_id)
        else:
            bot.answer_callback_query(call.id, "Military marching is currently disabled.")
    elif action == 'attack':
        if marching_status:
            if len(data_parts) == 1:
                ask_for_attack_type(call.message)
            elif data_parts[1] == 'type':
                bot.delete_message(call.message.chat.id, call.message.message_id)
                handle_attack_type_selection(call)
            elif data_parts[1] == 'confirm':
                bot.delete_message(call.message.chat.id, call.message.message_id)
                send_attack_order_details(call.message, user_id)
        else:
            bot.answer_callback_query(call.id, "Attack orders are currently disabled.")
    elif action == 'statement':
        if statement_status:
            if len(data_parts) == 1:
                bot.delete_message(call.message.chat.id, call.message.message_id)
                ask_for_statement(call.message, user_id)
            elif len(data_parts) == 2 and data_parts[1] == 'confirm':
                bot.delete_message(call.message.chat.id, call.message.message_id)
                handle_statement_confirmation(call, user_id)
        else:
            bot.answer_callback_query(call.id, "Statements are currently disabled.")
    elif action == 'missile_attack':
        if missile_status:
            if len(data_parts) == 1:
                handle_missile_attack(call.message, user_id)
            else:
                send_missile_attack_details(call.message, user_id)
        else:
            bot.answer_callback_query(call.id, "Missile attacks are currently disabled.")
    elif action == 'back_to_main':
        back_to_main_panel(call)
    elif action == 'delete':
        if len(data_parts) == 1:
            delete_channel_post(call)
    else:
        bot.answer_callback_query(call.id, "Invalid command.")


def back_to_main_panel(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    send_panel(call.message)

# --- Missile Attack Functions ---
def handle_missile_attack(message, user_id):
    user_context[user_id] = {}
    bot.send_message(message.chat.id, "🚀 Enter the type of missile:")
    bot.register_next_step_handler(message, lambda msg: get_missile_count(msg, user_id))

def get_missile_count(message, user_id):
    user_context[user_id]['missile_type'] = message.text
    bot.send_message(message.chat.id, "🚀 Enter the number of missiles fired:")
    bot.register_next_step_handler(message, lambda msg: get_missile_attack_origin_country(msg, user_id))

def get_missile_attack_origin_country(message, user_id):
    user_context[user_id]['missile_count'] = message.text
    bot.send_message(message.chat.id, "🏠 Please enter the origin country of the missile attack:")
    bot.register_next_step_handler(message, lambda msg: get_missile_attack_destination_country(msg, user_id))

def get_missile_attack_destination_country(message, user_id):
    user_context[user_id]['attacker_country'] = message.text
    bot.send_message(message.chat.id, "📌 Please enter the destination country of the missile attack:")
    bot.register_next_step_handler(message, lambda msg: get_missile_attack_destination_city(msg, user_id))

def get_missile_attack_destination_city(message, user_id):
    user_context[user_id]['target_country'] = message.text
    bot.send_message(message.chat.id, "📌 Please enter the destination city of the missile attack:")
    bot.register_next_step_handler(message, lambda msg: confirm_missile_attack_message(msg, user_id))

def confirm_missile_attack_message(message, user_id):
    user_context[user_id]['target_city'] = message.text
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton("Confirm ✅", callback_data='missile_attack_confirm'))
    markup.add(types.InlineKeyboardButton("🔙 Back", callback_data='back_to_main'))
    bot.send_message(message.chat.id, "Do you confirm this missile attack?", reply_markup=markup)

def send_missile_attack_details(message, user_id):
    missile_photo_url = "https://t.me/bsnsjwjwiiwjwjw92u2b29hwnwns/307"
    ctx = user_context[user_id]
    user_info = bot.get_chat(user_id)
    user_name = f"<a href='tg://user?id={user_id}'>{user_info.first_name}</a>"

    details = (
        f"☠️ {ctx['attacker_country']} has launched a missile attack on {ctx['target_country']}\n"
        f"<blockquote>"
        f"🏢• City: {ctx['target_city']}\n"
        f"🚀• Missile Type: {ctx['missile_type']}\n"
        f"🚀• Number of Missiles Fired: {ctx['missile_count']}"
        f"</blockquote>\n"
        f"🔥Responsible for this attack: {user_name}"
    )

    for admin_id in ADMIN_ID:
        bot.send_message(admin_id, details, parse_mode='HTML')

    group_confirmation = (
        f"✅ Missile attack completed.\n\n"
        f"Missile Type: {ctx['missile_type']}\n"
        f"Destination Country: {ctx['target_country']}\n"
        f"Destination City: {ctx['target_city']}\n"
        f"Number of Missiles Fired: {ctx['missile_count']}"
    )
    bot.send_photo(message.chat.id, missile_photo_url, caption=group_confirmation)
    bot.send_photo(CHANNEL_ID1, missile_photo_url, caption=details, parse_mode='HTML')

# --- Statement Functions ---
def ask_for_statement(message, user_id):
    bot.send_message(message.chat.id, "<b>Please send your statement.</b>", parse_mode='HTML')
    bot.register_next_step_handler(message, lambda msg: preview_statement(msg, user_id))

def preview_statement(message, user_id):
    confirm_button = types.InlineKeyboardMarkup(row_width=2)
    confirm_button.add(types.InlineKeyboardButton(text="✅ Confirm & Send", callback_data="statement_confirm"),
                       types.InlineKeyboardButton("🔙 Back", callback_data='back_to_main'))

    user_info = bot.get_chat(user_id)
    user_link = f"<a href='tg://user?id={user_id}'>{user_info.first_name}</a>"
    group_name = message.chat.title if message.chat.title else "Unknown"
    additional_caption = f"\n\n🌍 From: {group_name}\n👤 Commander: {user_link}"

    if message.text:
        content = f"{message.text}{additional_caption}"
    elif message.photo or message.video or message.document or message.audio or message.voice:
        caption = message.caption if message.caption else ""
        content = f"{caption}{additional_caption}"
    else:
        bot.send_message(message.chat.id, "🔴 Unsupported message type!")
        return

    user_context[message.chat.id] = {'content': content, 'media_type': message.content_type, 'media': message}
    bot.send_message(message.chat.id, f"🔍 <b>Statement Preview:</b>\n\n<blockquote>{content}</blockquote>",
                     parse_mode='HTML', reply_markup=confirm_button)

def handle_statement_confirmation(call, user_id):
    if call.message.chat.id in user_context:
        ctx = user_context[call.message.chat.id]
        content = ctx['content']
        media = ctx['media']
        media_type = ctx['media_type']
        sent_message = None

        delete_button = types.InlineKeyboardMarkup()
        delete_button.add(types.InlineKeyboardButton(text="Delete Post", callback_data="delete"))

        if media_type == 'text':
            sent_message = bot.send_message(CHANNEL_ID, content, parse_mode='HTML', reply_markup=delete_button)
        elif media_type == 'photo':
            sent_message = bot.send_photo(CHANNEL_ID, media.photo[-1].file_id, caption=content, parse_mode='HTML', reply_markup=delete_button)
        # Add other media types as needed (video, document, etc.)
        
        if sent_message:
            user_context[sent_message.message_id] = {'user_id': user_id, 'channel_id': CHANNEL_ID}
            bot.send_message(call.message.chat.id, "✅ Your statement has been sent!")

def delete_channel_post(call):
    bot_message_id = call.message.message_id
    if call.from_user.id == user_context.get(bot_message_id, {}).get('user_id') or call.from_user.id in ADMIN_ID:
        try:
            bot.delete_message(user_context[bot_message_id]['channel_id'], bot_message_id)
            del user_context[bot_message_id]
        except Exception as e:
            bot.answer_callback_query(call.id, f"Could not delete message. Maybe it's too old.")
    else:
        bot.answer_callback_query(call.id, "You are not authorized to delete this message.")

# --- Marching Functions ---
def ask_for_marching_type(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("Ground 💂‍♀", callback_data='marching_type_Ground'))
    markup.add(types.InlineKeyboardButton("Naval ⛴", callback_data='marching_type_Naval'))
    markup.add(types.InlineKeyboardButton("Air 🛩", callback_data='marching_type_Air'))
    markup.add(types.InlineKeyboardButton("🔙 Back", callback_data='back_to_main'))
    bot.send_message(message.chat.id, "Choose the type of march:", reply_markup=markup)

def handle_marching_type_selection(call):
    user_id = call.from_user.id
    attack_type = call.data.split('_')[2]
    user_context[user_id] = {'attack_type': attack_type}
    photo_urls = {
        "Ground": "https://t.me/bsnsjwjwiiwjwjw92u2b29hwnwns/309",
        "Naval": "https://t.me/bsnsjwjwiiwjwjw92u2b29hwnwns/310",
        "Air": "https://t.me/bsnsjwjwiiwjwjw92u2b29hwnwns/312"
    }
    user_context[user_id]['photo_url'] = photo_urls.get(attack_type)
    bot.send_message(call.message.chat.id, "🪖📝 Please enter your army's details:")
    bot.register_next_step_handler(call.message, lambda msg: get_marching_origin_details(msg, user_id))

def get_marching_origin_details(message, user_id):
    user_context[user_id]['attack_details'] = message.text
    bot.send_message(message.chat.id, "🏠 Please enter the origin city of the march:")
    bot.register_next_step_handler(message, lambda msg: get_marching_origin_country(msg, user_id))

def get_marching_origin_country(message, user_id):
    user_context[user_id]['attacker_city'] = message.text
    bot.send_message(message.chat.id, "🏠 Please enter the origin country of the march:")
    bot.register_next_step_handler(message, lambda msg: get_marching_destination_country(msg, user_id))

def get_marching_destination_country(message, user_id):
    user_context[user_id]['attacker_country'] = message.text
    bot.send_message(message.chat.id, "📌 Please enter the destination country of the march:")
    bot.register_next_step_handler(message, lambda msg: get_marching_destination_city(msg, user_id))

def get_marching_destination_city(message, user_id):
    user_context[user_id]['target_country'] = message.text
    bot.send_message(message.chat.id, "📌 Please enter the destination city of the march:")
    bot.register_next_step_handler(message, lambda msg: get_marching_arrival_time(msg, user_id))

def get_marching_arrival_time(message, user_id):
    user_context[user_id]['target_city'] = message.text
    bot.send_message(message.chat.id, "⏱️ Enter the arrival time:")
    bot.register_next_step_handler(message, lambda msg: get_marching_statement(msg, user_id))

def get_marching_statement(message, user_id):
    user_context[user_id]['attack_time'] = message.text
    bot.send_message(message.chat.id, "📝 Send your statement about this march:")
    bot.register_next_step_handler(message, lambda msg: confirm_marching_message(msg, user_id))

def confirm_marching_message(message, user_id):
    user_context[user_id]['attack_statement'] = message.text
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton("Confirm ✅", callback_data='marching_confirm'))
    markup.add(types.InlineKeyboardButton("🔙 Back", callback_data='back_to_main'))
    bot.send_message(message.chat.id, "Do you confirm sending this march announcement?", reply_markup=markup)

def send_marching_details(message, user_id):
    ctx = user_context[user_id]
    user_info = bot.get_chat(user_id)
    user_name = f"<a href='tg://user?id={user_id}'>{user_info.first_name}</a>"
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("Cancel March ❌", callback_data='delete'))

    details_template = (
        "🔖 Military forces of {attacker_country} have marched from {attacker_city} "
        "towards {target_city} in {target_country} via a {attack_type} route.\n\n"
        "<blockquote>Marching Statement:\n{attack_statement}\n"
        "⌛️ Arrival Time: {attack_time}\n{details_line}</blockquote>\n\n⚜️ "
        "Commander: {user_name}"
    )
    
    admin_details = details_template.format(details_line=f"📝 Details: {ctx['attack_details']}", **ctx, user_name=user_name)
    group_details = admin_details # Same details for the group
    channel_details = details_template.format(details_line="", **ctx, user_name=user_name) # No details in public channel

    for admin_id in ADMIN_ID:
        bot.send_message(admin_id, admin_details, parse_mode='HTML')

    bot.send_photo(message.chat.id, ctx['photo_url'], caption=group_details, parse_mode='HTML')

    sent_message = bot.send_photo(CHANNEL_ID1, ctx['photo_url'], caption=channel_details, parse_mode='HTML', reply_markup=markup)
    user_context[sent_message.message_id] = {'user_id': user_id, 'channel_id': CHANNEL_ID1}
    bot.send_message(message.chat.id, "Marching information has been sent.")

# --- Attack Order Functions ---
def ask_for_attack_type(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("Ground 💂‍♀", callback_data='attack_type_Ground'))
    markup.add(types.InlineKeyboardButton("Naval ⛴", callback_data='attack_type_Naval'))
    markup.add(types.InlineKeyboardButton("Air 🛩", callback_data='attack_type_Air'))
    markup.add(types.InlineKeyboardButton("🔙 Back", callback_data='back_to_main'))
    bot.send_message(message.chat.id, "Choose the attack type:", reply_markup=markup)

def handle_attack_type_selection(call):
    user_id = call.from_user.id
    attack_type = call.data.split('_')[2]
    user_context[user_id] = {'attack_type': attack_type}
    photo_urls = {
        "Ground": "https://t.me/bsnsjwjwiiwjwjw92u2b29hwnwns/308",
        "Naval": "https://t.me/bsnsjwjwiiwjwjw92u2b29hwnwns/311",
        "Air": "https://t.me/bsnsjwjwiiwjwjw92u2b29hwnwns/313"
    }
    user_context[user_id]['photo_url'] = photo_urls.get(attack_type)
    bot.send_message(call.message.chat.id, "🪖📝 Please enter your army's details:")
    bot.register_next_step_handler(call.message, lambda msg: get_attack_order_details(msg, user_id))

def get_attack_order_details(message, user_id):
    user_context[user_id]['attack_details'] = message.text
    bot.send_message(message.chat.id, "🏠 Please enter the origin city of the attack:")
    bot.register_next_step_handler(message, lambda msg: get_attack_order_origin_country(msg, user_id))

def get_attack_order_origin_country(message, user_id):
    user_context[user_id]['attacker_city'] = message.text
    bot.send_message(message.chat.id, "🏠 Please enter the origin country of the attack:")
    bot.register_next_step_handler(message, lambda msg: get_attack_order_destination_country(msg, user_id))

def get_attack_order_destination_country(message, user_id):
    user_context[user_id]['attacker_country'] = message.text
    bot.send_message(message.chat.id, "📌 Please enter the destination country of the attack:")
    bot.register_next_step_handler(message, lambda msg: get_attack_order_destination_city(msg, user_id))

def get_attack_order_destination_city(message, user_id):
    user_context[user_id]['target_country'] = message.text
    bot.send_message(message.chat.id, "📌 Please enter the destination city of the attack:")
    bot.register_next_step_handler(message, lambda msg: get_attack_order_arrival_time(msg, user_id))

def get_attack_order_arrival_time(message, user_id):
    user_context[user_id]['target_city'] = message.text
    bot.send_message(message.chat.id, "⏱️ Enter the arrival time:")
    bot.register_next_step_handler(message, lambda msg: get_attack_order_statement(msg, user_id))

def get_attack_order_statement(message, user_id):
    user_context[user_id]['attack_time'] = message.text
    bot.send_message(message.chat.id, "📝 Send your statement about this attack:")
    bot.register_next_step_handler(message, lambda msg: confirm_attack_order_message(msg, user_id))

def confirm_attack_order_message(message, user_id):
    user_context[user_id]['attack_statement'] = message.text
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton("Confirm ✅", callback_data='attack_confirm'))
    markup.add(types.InlineKeyboardButton("🔙 Back", callback_data='back_to_main'))
    bot.send_message(message.chat.id, "Do you confirm sending this attack order?", reply_markup=markup)

def send_attack_order_details(message, user_id):
    ctx = user_context[user_id]
    user_info = bot.get_chat(user_id)
    user_name = f"<a href='tg://user?id={user_id}'>{user_info.first_name}</a>"
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("Cancel Attack ❌", callback_data='delete'))

    details_template = (
        "🔖 Military forces from {attacker_country} in {attacker_city} "
        "have been ordered to attack {target_city} in {target_country} via a {attack_type} route.\n\n"
        "<blockquote>Attack Statement:\n{attack_statement}\n"
        "⌛️ Arrival Time: {attack_time}\n{details_line}</blockquote>\n\n⚜️ "
        "Commander: {user_name}"
    )
    
    admin_details = details_template.format(details_line=f"📝 Details: {ctx['attack_details']}", **ctx, user_name=user_name)
    group_details = admin_details # Same details for the group
    channel_details = details_template.format(details_line="", **ctx, user_name=user_name) # No details in public channel

    for admin_id in ADMIN_ID:
        bot.send_message(admin_id, admin_details, parse_mode='HTML')

    bot.send_photo(message.chat.id, ctx['photo_url'], caption=group_details, parse_mode='HTML')

    sent_message = bot.send_photo(CHANNEL_ID1, ctx['photo_url'], caption=channel_details, parse_mode='HTML', reply_markup=markup)
    user_context[sent_message.message_id] = {'user_id': user_id, 'channel_id': CHANNEL_ID1}
    bot.send_message(message.chat.id, "Attack information has been sent.")


# Start the bot
bot.infinity_polling(skip_pending=True)
