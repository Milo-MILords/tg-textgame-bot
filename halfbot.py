import telebot
from telebot import types
import sqlite3

# Initialize the bot with your token
API_TOKEN = 'YOUR TOKEN'
ADMIN_ID = [11111111, 00000000]
CHANNEL_ID = "STATEMENT CHANNEL" #بیانیه 
CHANNEL_ID1 = "MARCHING CHANNEL" #لشکرکشی
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


bot_enabled = True
statementstats = True
mosshakstats = True
lashkarstats = True


@bot.message_handler(commands=['on', 'off', 'statement_on', 'statement_off', 'mooshak_on',
                               'mooshak_off', 'lashkar_on', 'lashkar_off'])
def command_handler(message):
    global bot_enabled
    global statementstats
    global mosshakstats
    global lashkarstats
    if message.from_user.id in ADMIN_ID:
        if message.text == '/on':
            bot_enabled = True
            bot.reply_to(message, "✅ ربات فعال شد.")
        elif message.text == '/off':
            bot_enabled = False
            bot.reply_to(message, "❌ ربات غیرفعال شد.")
        elif message.text == '/statement_on':
            statementstats = True
            bot.reply_to(message, "✅ بیانیه فعال شد.")
        elif message.text == '/statement_off':
            statementstats = False
            bot.reply_to(message, "❌ بیانیه غیرفعال شد.")
        elif message.text == '/mooshak_on':
            mosshakstats = True
            bot.reply_to(message, "✅ بخش موشکی فعال شد.")
        elif message.text == '/mooshak_off':
            mosshakstats = False
            bot.reply_to(message, "❌ بخش موشکی غیرفعال شد.")
        elif message.text == '/lashkar_on':
            lashkarstats = True
            bot.reply_to(message, "✅ بخش لشکرکشی فعال شد.")
        elif message.text == '/lashkar_off':
            lashkarstats = False
            bot.reply_to(message, "❌ بخش لشکرکشی غیرفعال شد.")


@bot.message_handler(commands=['setlord'])
def set_lord(message):
    if is_group_chat(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        if user_id in ADMIN_ID:
            if message.reply_to_message is None:
                bot.reply_to(message, "لطفاً این دستور را روی پیام شخصی که می‌خواهید لرد شود ریپلای کنید.")
                return
            lord_user_id = message.reply_to_message.from_user.id
            cursor.execute("SELECT * FROM users WHERE user_id=?", (lord_user_id,))
            user = cursor.fetchone()
            if user:
                bot.reply_to(message, "کاربر مورد نظر قبلا به عنوان یک لرد در یک گروه ثبت شده است.")
            else:
                cursor.execute(
                    "INSERT OR IGNORE INTO users (user_id, group_id) VALUES (?, ?)",
                    (lord_user_id, chat_id))
                conn.commit()
                bot.reply_to(message, "کاربر مورد نظر به عنوان یک لرد در این گروه ثبت شد.")
        else:
            bot.reply_to(message, "فقط ادمین‌ها می‌توانند از این دستور استفاده کنند.")
    else:
        bot.reply_to(message, "این دستور فقط در گروه‌ها قابل استفاده است.")


@bot.message_handler(commands=['unsetlord'])
def unset_lord(message):
    if is_group_chat(message):
        chat_id = message.chat.id
        user_id = message.from_user.id
        if user_id in ADMIN_ID:
            if message.reply_to_message is None:
                bot.reply_to(message,
                             "لطفاً این دستور را روی پیام شخصی که می‌خواهید از لرد بودن خارج کنید ریپلای کنید.")
                return
            lord_user_id = message.reply_to_message.from_user.id
            cursor.execute(
                "DELETE FROM users WHERE user_id = ? AND group_id = ?",
                (lord_user_id, chat_id))
            conn.commit()
            bot.reply_to(message, "کاربر مورد نظر از لرد بودن در این گروه خارج شد.")
        else:
            bot.reply_to(message, "فقط ادمین‌ها می‌توانند از این دستور استفاده کنند.")
    else:
        bot.reply_to(message, "این دستور فقط در گروه‌ها قابل استفاده است.")


@bot.message_handler(func=lambda message: 'پنل' in message.text and message.chat.type == 'supergroup')
def start(message):
    if is_group_chat(message):
        start_start(message)
    else:
        bot.reply_to(message, "این ربات فقط در گروه‌ها قابل استفاده است.")


def start_start(message):
    user_id = message.from_user.id
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()
    paneldokme = []
    if user:
        paneldokme.append(types.InlineKeyboardButton("🙌 بیانیه", callback_data='statement'))
        paneldokme.append(types.InlineKeyboardButton("🚀 حمله موشکی", callback_data='missileattack'))
        paneldokme.append(types.InlineKeyboardButton("⚔️ لشکرکشی", callback_data='lashkar'))
        paneldokme.append(types.InlineKeyboardButton("🚨 دستور حمله", callback_data='attack'))
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(*paneldokme)
        markup.add(types.InlineKeyboardButton("❌ بستن پنل ❌", callback_data='closepanel'))
        try:
            bot.send_message(message.chat.id, "خوش آمدین قربان", reply_markup=markup)
        except AttributeError:
            bot.send_message(message.message.chat.id, "خوش آمدین قربان", reply_markup=markup)
    else:
        bot.reply_to(message, "شما ابتدا باید با /setlord ثبت نام کنید.")


@bot.callback_query_handler(func=lambda call: bot_enabled)
def callback_query(call):
    user_id = call.from_user.id
    data_parts = call.data.split('_')
    if data_parts[0] == 'closepanel':
        bot.edit_message_text("پنل با موفقیت بسته شد😎.", call.message.chat.id, call.message.message_id,
                              reply_markup=None)
    elif data_parts[0] == 'lashkar':
        if lashkarstats:
            if len(data_parts) == 1:
                ask_for_lashkar_type(call.message)
            elif data_parts[1] == 'type':
                bot.delete_message(call.message.chat.id, call.message.message_id)
                handle_lashkar_type_selection(call)
            elif data_parts[1] == 'confirm':
                bot.delete_message(call.message.chat.id, call.message.message_id)
                send_attack_details(call.message, user_id)
        else:
            bot.answer_callback_query(call.id, "لشکرکشی خاموش است.")
    elif data_parts[0] == 'attack':
        if lashkarstats:
            if len(data_parts) == 1:
                ask_for_attack_type(call.message)
            elif data_parts[1] == 'type':
                bot.delete_message(call.message.chat.id, call.message.message_id)
                handle_attack_type_selection(call)
            elif data_parts[1] == 'confirm':
                bot.delete_message(call.message.chat.id, call.message.message_id)
                send_att_details(call.message, user_id)
        else:
            bot.answer_callback_query(call.id, "لشکرکشی خاموش است.")
    elif data_parts[0] == 'statement':
        if statementstats:
            if len(data_parts) == 1:
                bot.delete_message(call.message.chat.id, call.message.message_id)
                ask_for_statement(call.message, user_id)
            elif len(data_parts) == 2:
                bot.delete_message(call.message.chat.id, call.message.message_id)
                handle_confirmation(call, user_id)
        else:
            bot.answer_callback_query(call.id, "بیانیه خاموش است.")
    elif data_parts[0] == 'missileattack':
        if mosshakstats:
            if len(data_parts) == 1:
                handle_missile_attack(call.message, user_id)
            else:
                send_missile_attack_details(call.message, user_id)
        else:
            bot.answer_callback_query(call.id, "حمله موشکی خاموش است.")
    elif data_parts[0] == 'backtomain':
        back_to_main(call)
    elif data_parts[0] == 'delete':
        if len(data_parts) == 1:
            delete_statement(call)
    else:
        bot.answer_callback_query(call.id, "دستور نامعتبر است.")


def back_to_main(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    start_start(call.message)


def handle_missile_attack(message, user_id):
    missile_attack = ''
    user_context[user_id] = {'missile_attack': missile_attack}
    bot.send_message(message.chat.id, "🚀 نوع موشک مورد نظر خود را وارد کنید:")
    bot.register_next_step_handler(message, lambda msg: get_missile_attack_origin(msg, user_id))


def get_missile_attack_origin(message, user_id):
    missile_type = message.text
    user_context[user_id]['missile_type'] = missile_type
    bot.send_message(message.chat.id, "🚀 تعداد موشک‌های شلیک شده را وارد کنید:")
    bot.register_next_step_handler(message, lambda msg: get_missile_attack_origin2(msg, user_id))


def get_missile_attack_origin2(message, user_id):
    missile_count = message.text
    user_context[user_id]['missile_count'] = missile_count
    bot.send_message(message.chat.id, "🏠 لطفا کشور مبدا حمله موشکی را وارد کنید:")
    bot.register_next_step_handler(message, lambda msg: get_missile_attack_destination0(msg, user_id))


def get_missile_attack_destination0(message, user_id):
    attacker_country = message.text
    user_context[user_id]['attacker_country'] = attacker_country
    bot.send_message(message.chat.id, "📌 لطفا کشور مقصد حمله موشکی را وارد کنید:")
    bot.register_next_step_handler(message, lambda msg: get_missile_attack_destination(msg, user_id))


def get_missile_attack_destination(message, user_id):
    target_country = message.text
    user_context[user_id]['target_country'] = target_country
    bot.send_message(message.chat.id, "📌 لطفا شهر مقصد حمله موشکی را وارد کنید:")
    bot.register_next_step_handler(message, lambda msg: confirm_missileattack_message(msg, user_id))


def confirm_missileattack_message(message, user_id):
    target_city = message.text
    user_context[user_id]['target_city'] = target_city
    group_id = message.chat.id
    dok1 = types.InlineKeyboardButton("تایید ✅", callback_data=f'missileattack_confirm')
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(dok1)
    markup.add(types.InlineKeyboardButton("🔙 بازگشت", callback_data='backtomain'))
    bot.send_message(group_id, "آیا این حمله موشکی را تایید می کنید؟", reply_markup=markup)


def send_missile_attack_details(message, user_id):
    missile_photo_url = "https://t.me/bsnsjwjwiiwjwjw92u2b29hwnwns/307"
    target_city = user_context[user_id]['target_city']
    missile_type = user_context[user_id]['missile_type']
    attacker_country = user_context[user_id]['attacker_country']
    missile_count = user_context[user_id]['missile_count']
    target_country = user_context[user_id]['target_country']
    # Get user info
    user_info = bot.get_chat(user_id)
    user_name = f"<a href='tg://user?id={user_id}'>{user_info.first_name}</a>"

    # Send details to admin
    for adminid in ADMIN_ID:
        bot.send_message(adminid,
                         f"☠️کشور {attacker_country} به کشور {target_country} حمله موشکی کرد\n<blockquote>"
                         f"🏢• شهر: {target_city}\n"
                         f"🚀• نوع موشک: {missile_type}\n"
                         f"🚀• تعداد موشک شلیک شده: {missile_count}</blockquote>\n"
                         f"🔥مسئول این حمله: {user_name}",
                         parse_mode='HTML')

    # Send details to attacker group
    bot.send_photo(message.chat.id, missile_photo_url, caption=
    f"✅حمله موشکی به پایان رسید.\n\n"
    f"نوع موشک: {missile_type}\n"
    f"کشور مقصد: {target_country}\n"
    f"شهر مقصد: {target_city}\n"
    f"تعداد موشک‌های شلیک شده: {missile_count}\n"
                   )

    # Send summary to channel
    bot.send_photo(CHANNEL_ID1, missile_photo_url, caption=
    f"☠️کشور {attacker_country} به کشور {target_country} حمله موشکی کرد\n<blockquote>"
    f"🏢• شهر: {target_city}\n"
    f"🚀• نوع موشک: {missile_type}\n"
    f"🚀• تعداد موشک شلیک شده: {missile_count}</blockquote>\n"
    f"🔥مسئول این حمله: {user_name}",
                   parse_mode='HTML')


def ask_for_statement(message, user_id):
    bot.send_message(message.chat.id, "<b>لطفا بیانیه خود را ارسال کنید</b>", parse_mode='HTML')
    bot.register_next_step_handler(message, lambda msg: preview_statement(msg, user_id))


def preview_statement(message, user_id):
    # ایجاد دکمه تایید
    confirm_button = types.InlineKeyboardMarkup(row_width=2)
    confirm_button.add(types.InlineKeyboardButton(text="✅ تایید ارسال", callback_data="statement_confirm"),
                       types.InlineKeyboardButton("🔙 بازگشت", callback_data='backtomain'))

    # ذخیره اطلاعات پیام برای ارسال در مرحله بعد
    user_info = bot.get_chat(user_id)
    user_link = f"<a href='tg://user?id={user_id}'>{user_info.first_name}</a>"
    group_name = message.chat.title if message.chat.title else "نامشخص"

    additional_caption = f"\n\n🌍 از {group_name}\n👤 فرمانده: {user_link}"

    # ساختن محتوای پیام برای پیش‌نمایش
    if message.text:
        statement_content = f"{message.text}{additional_caption}"
    elif message.photo:
        statement_content = message.caption if message.caption else " "
        statement_content = f"{statement_content}{additional_caption}"
    elif message.video:
        statement_content = message.caption if message.caption else " "
        statement_content = f"{statement_content}{additional_caption}"
    elif message.document:
        statement_content = message.caption if message.caption else " "
        statement_content = f"{statement_content}{additional_caption}"
    elif message.audio:
        statement_content = message.caption if message.caption else " "
        statement_content = f"{statement_content}{additional_caption}"
    elif message.voice:
        statement_content = message.caption if message.caption else " "
        statement_content = f"{statement_content}{additional_caption}"
    else:
        bot.send_message(message.chat.id, "🔴 پیام پشتیبانی نشده است!")
        return

    # ذخیره محتوای پیام در context
    user_context[message.chat.id] = {'content': statement_content, 'media_type': message.content_type, 'media': message}

    # ارسال پیام پیش‌نمایش با دکمه تایید
    bot.send_message(message.chat.id, f"🔍 <b>پیش‌نمایش متن بیانیه:</b>\n\n<blockquote>{statement_content}</blockquote>",
                     parse_mode='HTML', reply_markup=confirm_button)


def handle_confirmation(call, user_id):
    global sent_message
    if call.message.chat.id in user_context:
        content = user_context[call.message.chat.id]['content']
        media = user_context[call.message.chat.id]['media']
        media_type = user_context[call.message.chat.id]['media_type']

        delete_button = types.InlineKeyboardMarkup()
        delete_button.add(types.InlineKeyboardButton(text="حذف پست", callback_data="delete"))

        # ارسال بیانیه به کانال
        if media_type == 'text':
            sent_message = bot.send_message(CHANNEL_ID, content, parse_mode='HTML', reply_markup=delete_button)
        elif media_type == 'photo':
            sent_message = bot.send_photo(CHANNEL_ID, media.photo[-1].file_id, caption=content, parse_mode='HTML',
                                          reply_markup=delete_button)
        elif media_type == 'video':
            sent_message = bot.send_video(CHANNEL_ID, media.video.file_id, caption=content, parse_mode='HTML',
                                          reply_markup=delete_button)
        elif media_type == 'document':
            sent_message = bot.send_document(CHANNEL_ID, media.document.file_id, caption=content, parse_mode='HTML',
                                             reply_markup=delete_button)
        elif media_type == 'audio':
            sent_message = bot.send_audio(CHANNEL_ID, media.audio.file_id, caption=content, parse_mode='HTML',
                                          reply_markup=delete_button)
        elif media_type == 'voice':
            sent_message = bot.send_voice(CHANNEL_ID, media.voice.file_id, caption=content, parse_mode='HTML',
                                          reply_markup=delete_button)

        bot_message_id = sent_message.message_id
        user_context[bot_message_id] = {'user_id': user_id, 'channel_id': CHANNEL_ID}
        # اطلاع‌رسانی به کاربر
        bot.send_message(call.message.chat.id, "✅ بیانیه شما ارسال شد!")


def delete_statement(call):
    bot_message_id = call.message.message_id
    if call.from_user.id == user_context[bot_message_id]['user_id'] or call.from_user.id in ADMIN_ID:
        bot.delete_message(user_context[bot_message_id]['channel_id'], bot_message_id)
        del user_context[bot_message_id]
    else:
        bot.answer_callback_query(call.id, "شما اجازه حذف این پیام را ندارید.")


def ask_for_lashkar_type(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("زمینی 💂‍♀", callback_data='lashkar_type_زمینی'))
    markup.add(types.InlineKeyboardButton("دریایی⛴", callback_data='lashkar_type_دریایی'))
    markup.add(types.InlineKeyboardButton("هوایی🛩", callback_data='lashkar_type_هوایی'))
    markup.add(types.InlineKeyboardButton("🔙 بازگشت", callback_data='backtomain'))
    bot.send_message(message.chat.id, "نوع لشکرکشی را انتخاب کنید:", reply_markup=markup)


def handle_lashkar_type_selection(call):
    user_id = call.from_user.id
    attack_type = call.data.split('_')[2]
    user_context[user_id] = {'attack_type': attack_type}
    if attack_type == "زمینی":
        photo_url = "https://t.me/bsnsjwjwiiwjwjw92u2b29hwnwns/309"
        user_context[user_id]['photo_url'] = photo_url
    elif attack_type == "دریایی":
        photo_url = "https://t.me/bsnsjwjwiiwjwjw92u2b29hwnwns/310"
        user_context[user_id]['photo_url'] = photo_url
    elif attack_type == "هوایی":
        photo_url = "https://t.me/bsnsjwjwiiwjwjw92u2b29hwnwns/312"
        user_context[user_id]['photo_url'] = photo_url
    bot.send_message(call.message.chat.id, "🪖📝 لطفا اطلاعات ارتش خود را وارد کنید:")
    bot.register_next_step_handler(call.message, lambda msg: get_attack_origin(msg, user_id))


def get_attack_origin(message, user_id):
    attack_details = message.text
    user_context[user_id]['attack_details'] = attack_details
    bot.send_message(message.chat.id, "🏠 لطفا شهر مبدا لشکرکشی را وارد کنید:")
    bot.register_next_step_handler(message, lambda msg: get_attack_origin2(msg, user_id))


def get_attack_origin2(message, user_id):
    attacker_city = message.text
    user_context[user_id]['attacker_city'] = attacker_city
    bot.send_message(message.chat.id, "🏠 لطفا کشور مبدا لشکرکشی را وارد کنید:")
    bot.register_next_step_handler(message, lambda msg: get_attack_destination0(msg, user_id))


def get_attack_destination0(message, user_id):
    attacker_country = message.text
    user_context[user_id]['attacker_country'] = attacker_country
    bot.send_message(message.chat.id, "📌 لطفا کشور مقصد لشکرکشی را وارد کنید:")
    bot.register_next_step_handler(message, lambda msg: get_attack_destination(msg, user_id))


def get_attack_destination(message, user_id):
    target_country = message.text
    user_context[user_id]['target_country'] = target_country
    bot.send_message(message.chat.id, "📌 لطفا شهر مقصد لشکرکشی را وارد کنید:")
    bot.register_next_step_handler(message, lambda msg: get_attack_time(msg, user_id))


def get_attack_time(message, user_id):
    target_city = message.text
    user_context[user_id]['target_city'] = target_city
    bot.send_message(message.chat.id, "⏱️ زمان رسیدن را وارد کنید:")
    bot.register_next_step_handler(message, lambda msg: get_attack_statement(msg, user_id))


def get_attack_statement(message, user_id):
    attack_time = message.text
    user_context[user_id]['attack_time'] = attack_time
    bot.send_message(message.chat.id, "📝 بیانیه خود را درباره این لشکرکشی ارسال کنید:")
    bot.register_next_step_handler(message, lambda msg: confirm_attack_message(msg, user_id))


def confirm_attack_message(message, user_id):
    attack_statement = message.text
    user_context[user_id]['attack_statement'] = attack_statement
    group_id = message.chat.id
    dok1 = types.InlineKeyboardButton("تایید ✅", callback_data=f'lashkar_confirm')
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(dok1)
    markup.add(types.InlineKeyboardButton("🔙 بازگشت", callback_data='backtomain'))
    bot.send_message(group_id, "آیا ارسال این لشکرکشی را تایید می کنید؟", reply_markup=markup)


def send_attack_details(message, user_id):
    attack_statement = user_context[user_id]['attack_statement']
    attack_time = user_context[user_id]['attack_time']
    attack_type = user_context[user_id]['attack_type']
    attack_details = user_context[user_id]['attack_details']
    attacker_country = user_context[user_id]['attacker_country']
    attacker_city = user_context[user_id]['attacker_city']
    target_country = user_context[user_id]['target_country']
    target_city = user_context[user_id]['target_city']
    photo_url = user_context[user_id]['photo_url']
    # Get user info
    user_info = bot.get_chat(user_id)
    user_name = f"<a href='tg://user?id={user_id}'>{user_info.first_name}</a>"
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton(" لغو حمله ❌", callback_data='delete'))

    # Send details to admin
    for adminid in ADMIN_ID:
        bot.send_message(adminid,
                         f"🔖 نیروهای نظامی کشور {attacker_country} از شهر {attacker_city} به مقصد شهر {target_city} در کشور {target_country} به صورت {attack_type} حرکت کردند.\n\n"
                         f"<blockquote>بیانیه لشکرکشی :\n{attack_statement}\n"
                         f"⌛️ زمان رسیدن: {attack_time}\n📝 جزئیات: {attack_details}</blockquote>\n\n⚜️ "
                         f"فرمانده: {user_name}",
                         parse_mode='HTML')
    # Send details to attacker group
    bot.send_photo(message.chat.id, photo_url, caption=
    f"🔖 نیروهای نظامی کشور شما از شهر {attacker_city} به مقصد شهر {target_city} در کشور {target_country} به صورت {attack_type} حرکت کردند.\n\n"
    f"<blockquote>بیانیه لشکرکشی :\n{attack_statement}\n"
    f"⌛️ زمان رسیدن: {attack_time}\n📝 جزئیات: {attack_details}</blockquote>\n\n⚜️ "
    f"فرمانده: {user_name}",
                   parse_mode='HTML')

    # Send summary to channel
    sent_message = bot.send_photo(CHANNEL_ID1, photo_url, caption=
    f"🔖 نیروهای نظامی کشور {attacker_country} از شهر {attacker_city} به مقصد شهر {target_city} در کشور {target_country} به صورت {attack_type} حرکت کردند.\n\n"
    f"<blockquote>بیانیه لشکرکشی :\n{attack_statement}\n"
    f"⌛️ زمان رسیدن: {attack_time}</blockquote>\n\n⚜️ "
    f"فرمانده: {user_name}",
                                  parse_mode='HTML', reply_markup=markup)

    bot_message_id = sent_message.message_id
    user_context[bot_message_id] = {'user_id': user_id, 'channel_id': CHANNEL_ID1}
    bot.send_message(message.chat.id, "اطلاعات لشکرکشی ارسال شد.")


def ask_for_attack_type(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("زمینی 💂‍♀", callback_data='attack_type_زمینی'))
    markup.add(types.InlineKeyboardButton("دریایی⛴", callback_data='attack_type_دریایی'))
    markup.add(types.InlineKeyboardButton("هوایی🛩", callback_data='attack_type_هوایی'))
    markup.add(types.InlineKeyboardButton("🔙 بازگشت", callback_data='backtomain'))
    bot.send_message(message.chat.id, "نوع حمله را انتخاب کنید:", reply_markup=markup)


def handle_attack_type_selection(call):
    user_id = call.from_user.id
    attack_type = call.data.split('_')[2]
    user_context[user_id] = {'attack_type': attack_type}
    if attack_type == "زمینی":
        photo_url = "https://t.me/bsnsjwjwiiwjwjw92u2b29hwnwns/308"
        user_context[user_id]['photo_url'] = photo_url
    elif attack_type == "دریایی":
        photo_url = "https://t.me/bsnsjwjwiiwjwjw92u2b29hwnwns/311"
        user_context[user_id]['photo_url'] = photo_url
    elif attack_type == "هوایی":
        photo_url = "https://t.me/bsnsjwjwiiwjwjw92u2b29hwnwns/313"
        user_context[user_id]['photo_url'] = photo_url
    bot.send_message(call.message.chat.id, "🪖📝 لطفا اطلاعات ارتش خود را وارد کنید:")
    bot.register_next_step_handler(call.message, lambda msg: get_att_origin(msg, user_id))


def get_att_origin(message, user_id):
    attack_details = message.text
    user_context[user_id]['attack_details'] = attack_details
    bot.send_message(message.chat.id, "🏠 لطفا شهر مبدا حمله را وارد کنید:")
    bot.register_next_step_handler(message, lambda msg: get_att_origin2(msg, user_id))


def get_att_origin2(message, user_id):
    attacker_city = message.text
    user_context[user_id]['attacker_city'] = attacker_city
    bot.send_message(message.chat.id, "🏠 لطفا کشور مبدا حمله را وارد کنید:")
    bot.register_next_step_handler(message, lambda msg: get_att_destination0(msg, user_id))


def get_att_destination0(message, user_id):
    attacker_country = message.text
    user_context[user_id]['attacker_country'] = attacker_country
    bot.send_message(message.chat.id, "📌 لطفا کشور مقصد حمله را وارد کنید:")
    bot.register_next_step_handler(message, lambda msg: get_att_destination(msg, user_id))


def get_att_destination(message, user_id):
    target_country = message.text
    user_context[user_id]['target_country'] = target_country
    bot.send_message(message.chat.id, "📌 لطفا شهر مقصد حمله را وارد کنید:")
    bot.register_next_step_handler(message, lambda msg: get_att_time(msg, user_id))


def get_att_time(message, user_id):
    target_city = message.text
    user_context[user_id]['target_city'] = target_city
    bot.send_message(message.chat.id, "⏱️ زمان رسیدن را وارد کنید:")
    bot.register_next_step_handler(message, lambda msg: get_att_statement(msg, user_id))


def get_att_statement(message, user_id):
    attack_time = message.text
    user_context[user_id]['attack_time'] = attack_time
    bot.send_message(message.chat.id, "📝 بیانیه خود را درباره این حمله ارسال کنید:")
    bot.register_next_step_handler(message, lambda msg: confirm_att_message(msg, user_id))


def confirm_att_message(message, user_id):
    attack_statement = message.text
    user_context[user_id]['attack_statement'] = attack_statement
    group_id = message.chat.id
    dok1 = types.InlineKeyboardButton("تایید ✅", callback_data=f'attack_confirm')
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(dok1)
    markup.add(types.InlineKeyboardButton("🔙 بازگشت", callback_data='backtomain'))
    bot.send_message(group_id, "آیا ارسال این حمله را تایید می کنید؟", reply_markup=markup)


def send_att_details(message, user_id):
    attack_statement = user_context[user_id]['attack_statement']
    attack_time = user_context[user_id]['attack_time']
    attack_type = user_context[user_id]['attack_type']
    attack_details = user_context[user_id]['attack_details']
    attacker_country = user_context[user_id]['attacker_country']
    attacker_city = user_context[user_id]['attacker_city']
    target_country = user_context[user_id]['target_country']
    target_city = user_context[user_id]['target_city']
    photo_url = user_context[user_id]['photo_url']
    # Get user info
    user_info = bot.get_chat(user_id)
    user_name = f"<a href='tg://user?id={user_id}'>{user_info.first_name}</a>"
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton(" لغو حمله ❌", callback_data='delete'))

    # Send details to admin
    for adminid in ADMIN_ID:
        bot.send_message(adminid,
                         f"🔖 نیروهای نظامی کشور {attacker_country} از شهر {attacker_city} به مقصد شهر {target_city} در کشور {target_country} به صورت {attack_type} دستور حمله داد.\n\n"
                         f"<blockquote>بیانیه حمله :\n{attack_statement}\n"
                         f"⌛️ زمان رسیدن: {attack_time}\n📝 جزئیات: {attack_details}</blockquote>\n\n⚜️ "
                         f"فرمانده: {user_name}",
                         parse_mode='HTML')
    # Send details to attacker group
    bot.send_photo(message.chat.id, photo_url, caption=
    f"🔖 نیروهای نظامی کشور شما از شهر {attacker_city} به مقصد شهر {target_city} در کشور {target_country} به صورت {attack_type} دستور حمله داد.\n\n"
    f"<blockquote>بیانیه حمله :\n{attack_statement}\n"
    f"⌛️ زمان رسیدن: {attack_time}\n📝 جزئیات: {attack_details}</blockquote>\n\n⚜️ "
    f"فرمانده: {user_name}",
                   parse_mode='HTML')

    # Send summary to channel
    sent_message = bot.send_photo(CHANNEL_ID1, photo_url, caption=
    f"🔖 نیروهای نظامی کشور {attacker_country} از شهر {attacker_city} به مقصد شهر {target_city} در کشور {target_country} به صورت {attack_type} دستور حمله داد.\n\n"
    f"<blockquote>بیانیه حمله :\n{attack_statement}\n"
    f"⌛️ زمان رسیدن: {attack_time}</blockquote>\n\n⚜️ "
    f"فرمانده: {user_name}",
                                  parse_mode='HTML', reply_markup=markup)

    bot_message_id = sent_message.message_id
    user_context[bot_message_id] = {'user_id': user_id, 'channel_id': CHANNEL_ID1}
    bot.send_message(message.chat.id, "اطلاعات حمله ارسال شد.")


# Start the bot
bot.infinity_polling(skip_pending=True)
