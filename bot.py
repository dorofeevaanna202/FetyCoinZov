import telebot
import random
import json
import os
from telebot import types

TOKEN = "8723076939:AAG6vYuzyM4OMf3T25wGo_r7_5Y4oeHsXG4"
bot = telebot.TeleBot(TOKEN)

DATA_FILE = 'players.json'
ADMIN_ID = 8710765073

def load_players():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_players():
    with open(DATA_FILE, 'w') as f:
        json.dump(players, f)

def save_roulette_log():
    with open('roulette_log.json', 'w') as f:
        json.dump(roulette_log, f)

def load_roulette_log():
    global roulette_log
    if os.path.exists('roulette_log.json'):
        with open('roulette_log.json', 'r') as f:
            roulette_log = json.load(f)
    else:
        roulette_log = []

players = load_players()
roulette_log = []
load_roulette_log()

def get_player(user_id, username):
    if str(user_id) not in players:
        players[str(user_id)] = {'username': username, 'balance': 0, 'gtz': 0, 'games': 0, 'wins': 0, 'last_bonus': 0, 'last_gift': 0, 'exchange_state': None}
        save_players()
    return players[str(user_id)]

roulette_numbers = {0: '🟢', 1: '🔴', 2: '⚫', 3: '🔴', 4: '⚫', 5: '🔴', 6: '⚫', 7: '🔴', 8: '⚫', 9: '🟡', 10: '⚫', 11: '🔴', 12: '⚫', 13: '🔴', 14: '⚫', 15: '🔴'}

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    get_player(user_id, username)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("💰 Баланс"), types.KeyboardButton("🎮 Игры"))
    markup.add(types.KeyboardButton("🏆 Топ"), types.KeyboardButton("🎁 Бонус"))
    markup.add(types.KeyboardButton("💎 Обменять"))
    bot.send_message(message.chat.id, "👋 Добро пожаловать!", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "💰 Баланс" or m.text == "Б" or m.text == "б")
def show_balance(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    player = get_player(user_id, username)
    text = f"@{player['username']}\n🔥Баланс: {player['balance']:,} Hz⭐\n💎GtZ: {player['gtz']:,} 💎\n🎮Сыгранно игр: {player['games']}".replace(',', '.')
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda m: m.text == "🏆 Топ" or m.text == "ТопHZ" or m.text == "топHZ")
def show_top(message):
    sorted_players = sorted(players.items(), key=lambda x: x[1]['balance'], reverse=True)[:10]
    emojis = ["🥇", "🥈", "🥉", "⭐", "⭐", "🔥", "🔥", "🔥", "🔥", "🔥"]
    text = "🏆Топ Hz⭐🏆\n\n"
    for i, (uid, p) in enumerate(sorted_players):
        emoji = emojis[i] if i < len(emojis) else "🔥"
        text += f"{i+1}.{emoji} @{p['username']} — {p['balance']:,} Hz⭐\n".replace(',', '.')
    if not sorted_players:
        text += "Пока нет игроков"
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda m: m.text == "ТопGtZ" or m.text == "топGtZ" or m.text == "топgtz")
def show_top_gtz(message):
    sorted_players = sorted(players.items(), key=lambda x: x[1].get('gtz', 0), reverse=True)[:10]
    emojis = ["🥇", "🥈", "🥉", "⭐", "⭐", "🔥", "🔥", "🔥", "🔥", "🔥"]
    text = "🏆Топ GtZ💎🏆\n\n"
    for i, (uid, p) in enumerate(sorted_players):
        emoji = emojis[i] if i < len(emojis) else "🔥"
        text += f"{i+1}.{emoji} @{p['username']} — {p.get('gtz', 0):,} 💎\n".replace(',', '.')
    if not sorted_players:
        text += "Пока нет игроков"
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda m: m.text == "🎁 Бонус" or m.text == "БонусHZ" or m.text == "бонусHZ")
def claim_bonus(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    player = get_player(user_id, username)
    import time as t
    current_time = t.time()
    if current_time - player['last_bonus'] < 7200:
        wait = int(7200 - (current_time - player['last_bonus']))
        bot.send_message(message.chat.id, f"⏳ Бонус будет через {wait//60} мин {wait%60} сек")
        return
    bonus = random.randint(24935, 55750)
    player['balance'] += bonus
    player['last_bonus'] = current_time
    save_players()
    bot.send_message(message.chat.id, f"@{player['username']}\n🎁Ты получил бонус: {bonus:,} Hz⭐".replace(',', '.'))

@bot.message_handler(func=lambda m: m.text == "HzПодарок" or m.text == "подарок" or m.text == "Подарок")
def claim_gift(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    player = get_player(user_id, username)
    import time as t
    current_time = t.time()
    if current_time - player['last_gift'] < 1800:
        wait = int(1800 - (current_time - player['last_gift']))
        bot.send_message(message.chat.id, f"⏳ Подарок будет через {wait//60} мин {wait%60} сек")
        return
    player['last_gift'] = current_time
    save_players()
    rand = random.random()
    if rand < 0.05:
        bot.send_message(message.chat.id, "🎁Ты забрал подарок🎁\n❌К сожалению, он пустой!")
        return
    elif rand < 0.25:
        amount = random.randint(5000, 7500)
        player['balance'] += amount
        save_players()
        bot.send_message(message.chat.id, f"🎁Ты забрал подарок🎁\n🎉Ты получил: {amount:,} Hz⭐ с шансом 95%".replace(',', '.'))
    elif rand < 0.50:
        amount = random.randint(10000, 25000)
        player['balance'] += amount
        save_players()
        bot.send_message(message.chat.id, f"🎁Ты забрал подарок🎁\n🎉Ты получил: {amount:,} Hz⭐ с шансом 75%".replace(',', '.'))
    elif rand < 0.65:
        amount = random.randint(25000, 50000)
        player['balance'] += amount
        save_players()
        bot.send_message(message.chat.id, f"🎁Ты забрал подарок🎁\n🎉Ты получил: {amount:,} Hz⭐ с шансом 50%".replace(',', '.'))
    elif rand < 0.75:
        if random.random() < 0.5:
            amount = random.randint(50000, 150000)
            player['balance'] += amount
            save_players()
            bot.send_message(message.chat.id, f"🎁Ты забрал подарок🎁\n🎉Ты получил: {amount:,} Hz⭐ с шансом 25%".replace(',', '.'))
        else:
            amount = 5
            player['gtz'] = player.get('gtz', 0) + amount
            save_players()
            bot.send_message(message.chat.id, f"🎁Ты забрал подарок🎁\n🎉Ты получил: {amount} GtZ💎 с шансом 25%")
    elif rand < 0.90:
        if random.random() < 0.5:
            amount = random.randint(150000, 500000)
            player['balance'] += amount
            save_players()
            bot.send_message(message.chat.id, f"🎁Ты забрал подарок🎁\n🎉Ты получил: {amount:,} Hz⭐ с шансом 10%".replace(',', '.'))
        else:
            amount = 15
            player['gtz'] = player.get('gtz', 0) + amount
            save_players()
            bot.send_message(message.chat.id, f"🎁Ты забрал подарок🎁\n🎉Ты получил: {amount} GtZ💎 с шансом 10%")
    elif rand < 0.97:
        if random.random() < 0.5:
            amount = random.randint(1000000, 2000000)
            player['balance'] += amount
            save_players()
            bot.send_message(message.chat.id, f"🎁Ты забрал подарок🎁\n🎉Ты получил: {amount:,} Hz⭐ с шансом 3%".replace(',', '.'))
        else:
            amount = 50
            player['gtz'] = player.get('gtz', 0) + amount
            save_players()
            bot.send_message(message.chat.id, f"🎁Ты забрал подарок🎁\n🎉Ты получил: {amount} GtZ💎 с шансом 3%")
    else:
        if random.random() < 0.5:
            amount = 5000000
            player['balance'] += amount
            save_players()
            bot.send_message(message.chat.id, f"🎁Ты забрал подарок🎁\n🎉Ты получил: {amount:,} Hz⭐ с шансом 1%".replace(',', '.'))
        else:
            amount = 150
            player['gtz'] = player.get('gtz', 0) + amount
            save_players()
            bot.send_message(message.chat.id, f"🎁Ты забрал подарок🎁\n🎉Ты получил: {amount} GtZ💎 с шансом 1%")

@bot.message_handler(func=lambda m: m.text == "🎮 Игры" or m.text == "Игры" or m.text == "игры")
def show_games(message):
    text = """💎Все игры на данный момент🎁

🎰РулеткаHz
Чтобы играть тебе надо выбрать ⚫,🔴,🟡,🟢
🟢 — Падает с шансом 0.50%‼️ (сумма выйграша х30)
🟡 — Падает с шансом 5%❗ (сумма выйграша 5х)
⚫ И 🔴 — падают с шансом 50% (сумма выйграша 2х)
ч(⚫),к(🔴),ж(🟡),з(🟢)
Пример:
РулеткаHz 2000 ч
РулеткаHz 5000 ж

🚀HzКрашнуть (сумма) (кофицент)
Пример: HzКрашнуть 38844 1.21

🪙Орёл или решка?
Твоя цель выбрать правильную монетку.
Пример: орёл 200 / решка 500
Минимальная ставка 100 монет

❓Скоро новая игра"""
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda m: m.text == "💎 Обменять" or m.text == "Обменять" or m.text == "обменять")
def start_exchange(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    player = get_player(user_id, username)
    player['exchange_state'] = 'waiting'
    save_players()
    bot.send_message(message.chat.id, "👋Привет это обмен GtZ💎\nКурс: 1💎 = 25.000 Hz⭐\nСколько хочешь обменять?")

@bot.message_handler(func=lambda m: players.get(str(m.from_user.id), {}).get('exchange_state') == 'waiting')
def process_exchange(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    player = get_player(user_id, username)
    try:
        amount_gtz = int(message.text)
    except:
        bot.send_message(message.chat.id, "❌ Введите число!")
        return
    if amount_gtz <= 0:
        bot.send_message(message.chat.id, "❌ Введите положительное число!")
        return
    if amount_gtz > player['gtz']:
        bot.send_message(message.chat.id, "❌ Недостаточно GtZ!")
        player['exchange_state'] = None
        save_players()
        return
    hz_amount = amount_gtz * 25000
    player['gtz'] -= amount_gtz
    player['balance'] += hz_amount
    player['exchange_state'] = None
    save_players()
    bot.send_message(message.chat.id, f"✅Успешный обмен✅\nТы получил(а): {hz_amount:,} Hz⭐".replace(',', '.'))@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith(('орёл', 'орел', 'решка')))
def play_coin(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    player = get_player(user_id, username)
    parts = message.text.lower().split()
    if len(parts) < 2:
        bot.send_message(message.chat.id, "❌ Формат: орёл 200 / решка 500")
        return
    choice = parts[0]
    try:
        bet = int(parts[1])
    except:
        bot.send_message(message.chat.id, "❌ Неверная ставка!")
        return
    if bet < 100:
        bot.send_message(message.chat.id, "❌ Минимальная ставка 100!")
        return
    if bet > player['balance']:
        bot.send_message(message.chat.id, "❌ Недостаточно средств!")
        return
    player['balance'] -= bet
    player['games'] += 1
    save_players()
    result = random.choice(['орёл', 'решка'])
    if choice == 'орёл' or choice == 'орел':
        multiplier = 1.7
        player_choice = 'орёл'
    else:
        multiplier = 1.5
        player_choice = 'решка'
    if result == player_choice:
        win = int(bet * multiplier)
        player['balance'] += win
        player['wins'] += 1
        save_players()
        text = f"🪙 Монетка подброшена!\n\nРезультат: {'🦅 Орёл' if result == 'орёл' else '👑 Решка'}\nТвой выбор: {'🦅 Орёл' if player_choice == 'орёл' else '👑 Решка'}\n\n🎉 Ты выиграл! +{win:,} Hz⭐ ({multiplier}x)".replace(',', '.')
    else:
        text = f"🪙 Монетка подброшена!\n\nРезультат: {'🦅 Орёл' if result == 'орёл' else '👑 Решка'}\nТвой выбор: {'🦅 Орёл' if player_choice == 'орёл' else '👑 Решка'}\n\n❌ Ты проиграл! -{bet:,} Hz⭐".replace(',', '.')
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith('hzкрашнуть'))
def play_crash(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    player = get_player(user_id, username)
    parts = message.text.split()
    if len(parts) < 3:
        bot.send_message(message.chat.id, "❌ Формат: HzКрашнуть (сумма) (кофицент)\nПример: HzКрашнуть 38844 1.21")
        return
    try:
        bet = int(parts[1])
        target = float(parts[2])
    except:
        bot.send_message(message.chat.id, "❌ Неверный формат!")
        return
    if bet < 10:
        bot.send_message(message.chat.id, "❌ Минимальная ставка 10!")
        return
    if bet > player['balance']:
        bot.send_message(message.chat.id, "❌ Недостаточно средств!")
        return
    player['balance'] -= bet
    player['games'] += 1
    save_players()
    rand = random.random()
    if rand < 0.50:
        crash_point = 1.0
    elif rand < 0.75:
        crash_point = round(random.uniform(1.10, 1.50), 2)
    elif rand < 0.90:
        crash_point = round(random.uniform(1.51, 2.00), 2)
    elif rand < 0.95:
        crash_point = round(random.uniform(2.00, 4.00), 2)
    elif rand < 0.98:
        crash_point = round(random.uniform(4.00, 7.00), 2)
    elif rand < 0.999:
        crash_point = round(random.uniform(7.00, 10.00), 2)
    else:
        crash_point = 30.0
    if target >= crash_point:
        bot.send_message(message.chat.id, f"❌Ты пройграл❌\n🔴Проигранная сумма: {bet:,} Hz⭐\n‼️Ракета упала на {crash_point}".replace(',', '.'))
    else:
        win = int(bet * target)
        player['balance'] += win
        player['wins'] += 1
        save_players()
        bot.send_message(message.chat.id, f"✅Ты выйграл⭐\n💎Твой выйграшь: {win:,} Hz⭐\n🎉Ракета улетела на {crash_point}🔥".replace(',', '.'))

@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith('рулеткаhz'))
def play_roulette(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    player = get_player(user_id, username)
    parts = message.text.split()
    if len(parts) < 3:
        bot.send_message(message.chat.id, "❌ Формат: РулеткаHz (сумма) ч/к/ж/з")
        return
    try:
        bet = int(parts[1])
        choice = parts[2].lower()
    except:
        bot.send_message(message.chat.id, "❌ Неверный формат!")
        return
    if bet < 10:
        bot.send_message(message.chat.id, "❌ Минимальная ставка 10!")
        return
    if bet > player['balance']:
        bot.send_message(message.chat.id, "❌ Недостаточно средств!")
        return
    if choice == 'ч':
        player_color = '⚫'
        multiplier = 2
    elif choice == 'к':
        player_color = '🔴'
        multiplier = 2
    elif choice == 'ж':
        player_color = '🟡'
        multiplier = 5
    elif choice == 'з':
        player_color = '🟢'
        multiplier = 30
    else:
        bot.send_message(message.chat.id, "❌ Выбери: ч(⚫), к(🔴), ж(🟡), з(🟢)")
        return
    player['balance'] -= bet
    player['games'] += 1
    save_players()
    rand = random.random()
    if rand < 0.005:
        result_num = 0
    elif rand < 0.055:
        result_num = 9
    elif rand < 0.525:
        result_num = random.choice([1, 3, 5, 7, 11, 13, 15])
    else:
        result_num = random.choice([2, 4, 6, 8, 10, 12, 14])
    result_color = roulette_numbers[result_num]
    roulette_log.append(f"{result_num}{result_color}")
    if len(roulette_log) > 50:
        roulette_log = roulette_log[-50:]
    save_roulette_log()
    if result_color == player_color:
        win = int(bet * multiplier)
        player['balance'] += win
        player['wins'] += 1
        save_players()
        bot.send_message(message.chat.id, f"Поздравляю ты выйграл(а)✅\nВыпал: {result_num}{result_color}\nСумма выйграша: {win:,} Hz⭐".replace(',', '.'))
    else:
        bot.send_message(message.chat.id, f"Ты пройграл(а)❌\nВыпал: {result_num}{result_color}\nСумма пройгрыша: {bet:,} Hz⭐".replace(',', '.'))

@bot.message_handler(func=lambda m: m.text == "ЛогHz" or m.text == "логHz" or m.text == "Логhz")
def show_roulette_log(message):
    if not roulette_log:
        bot.send_message(message.chat.id, "📋 ЛогРулетки пуст")
        return
    text = "📋 ЛогРулетки:\n"
    for entry in roulette_log[-10:]:
        text += entry + "\n"
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith('hzвыдать'))
def transfer_hz(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    player = get_player(user_id, username)
    parts = message.text.split()
    if len(parts) < 2:
        bot.send_message(message.chat.id, "❌ Формат: HzВыдать (сумма) (@username или ответ)")
        return
    try:
        amount = int(parts[1])
    except:
        bot.send_message(message.chat.id, "❌ Неверная сумма!")
        return
    if amount <= 0:
        bot.send_message(message.chat.id, "❌ Сумма должна быть положительной!")
        return
    if amount > player['balance']:
        bot.send_message(message.chat.id, "❌ Недостаточно Hz⭐!")
        return
    if message.reply_to_message:
        target_id = message.reply_to_message.from_user.id
        target_username = message.reply_to_message.from_user.username or message.reply_to_message.from_user.first_name
    elif len(parts) > 2:
        target_username = parts[2].replace('@', '')
        target_id = None
        for uid, p in players.items():
            if p['username'].lower() == target_username.lower():
                target_id = int(uid)
                break
        if not target_id:
            bot.send_message(message.chat.id, f"❌ Игрок @{target_username} не найден!")
            return
    else:
        bot.send_message(message.chat.id, "❌ Укажи @username или ответь на сообщение!")
        return
    if target_id == user_id:
        bot.send_message(message.chat.id, "❌ Нельзя перевести самому себе!")
        return
    target = get_player(target_id, target_username)
    player['balance'] -= amount
    target['balance'] += amount
    save_players()
    bot.send_message(message.chat.id, f"✅ Переведено {amount:,} Hz⭐ игроку @{target['username']}\nТвой баланс: {player['balance']:,} Hz⭐".replace(',', '.'))

@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith('gtzвыдать'))
def transfer_gtz(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    player = get_player(user_id, username)
    parts = message.text.split()
    if len(parts) < 2:
        bot.send_message(message.chat.id, "❌ Формат: GtZВыдать (сумма) (@username или ответ)")
        return
    try:
        amount = int(parts[1])
    except:
        bot.send_message(message.chat.id, "❌ Неверная сумма!")
        return
    if amount <= 0:
        bot.send_message(message.chat.id, "❌ Сумма должна быть положительной!")
        return
    if amount > player.get('gtz', 0):
        bot.send_message(message.chat.id, "❌ Недостаточно GtZ!")
        return
    if message.reply_to_message:
        target_id = message.reply_to_message.from_user.id
        target_username = message.reply_to_message.from_user.username or message.reply_to_message.from_user.first_name
    elif len(parts) > 2:
        target_username = parts[2].replace('@', '')
        target_id = None
        for uid, p in players.items():
            if p['username'].lower() == target_username.lower():
                target_id = int(uid)
                break
        if not target_id:
            bot.send_message(message.chat.id, f"❌ Игрок @{target_username} не найден!")
            return
    else:
        bot.send_message(message.chat.id, "❌ Укажи @username или ответь на сообщение!")
        return
    if target_id == user_id:
        bot.send_message(message.chat.id, "❌ Нельзя перевести самому себе!")
        return
    target = get_player(target_id, target_username)
    player['gtz'] = player.get('gtz', 0) - amount
    target['gtz'] = target.get('gtz', 0) + amount
    save_players()
    bot.send_message(message.chat.id, f"✅ Переведено {amount:,} GtZ💎 игроку @{target['username']}\nТвой баланс GtZ: {player['gtz']:,} 💎".replace(',', '.'))

@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith('set'))
def admin_set(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        return
    parts = message.text.split()
    if len(parts) < 2:
        return
    amount_str = parts[1].lower()
    currency = parts[2].upper() if len(parts) > 2 else "HZ"
    if 'kk' in amount_str:
        amount = int(float(amount_str.replace('kk', '')) * 1000000)
    elif 'k' in amount_str:
        amount = int(float(amount_str.replace('k', '')) * 1000)
    else:
        try:
            amount = int(amount_str)
        except:
            return
    if currency == "GTZ":
        players[str(user_id)]['gtz'] = players[str(user_id)].get('gtz', 0) + amount
        save_players()
        bot.send_message(message.chat.id, f"✅ Получено: {amount:,} GtZ💎\nБаланс GtZ: {players[str(user_id)]['gtz']:,} 💎".replace(',', '.'))
    else:
        players[str(user_id)]['balance'] += amount
        save_players()
        bot.send_message(message.chat.id, f"✅ Получено: {amount:,} Hz⭐\nБаланс: {players[str(user_id)]['balance']:,} Hz⭐".replace(',', '.'))

@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith('hzttвыдать'))
def admin_give_hz(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        return
    parts = message.text.split()
    if len(parts) < 2:
        return
    try:
        amount = int(parts[1])
    except:
        return
    if amount <= 0:
        return
    if message.reply_to_message:
        target_id = message.reply_to_message.from_user.id
        target_username = message.reply_to_message.from_user.username or message.reply_to_message.from_user.first_name
    elif len(parts) > 2:
        target_username = parts[2].replace('@', '')
        target_id = None
        for uid, p in players.items():
            if p['username'].lower() == target_username.lower():
                target_id = int(uid)
                break
        if not target_id:
            bot.send_message(message.chat.id, f"❌ Игрок @{target_username} не найден!")
            return
    else:
        target_id = user_id
        target_username = message.from_user.username or message.from_user.first_name
    target = get_player(target_id, target_username)
    target['balance'] += amount
    save_players()
    bot.send_message(message.chat.id, f"✅ Выдано {amount:,} Hz⭐ игроку @{target['username']}\nЕго баланс: {target['balance']:,} Hz⭐".replace(',', '.'))

@bot.message_handler(func=lambda m: m.text and m.text.lower().startswith('gtzttвыдать'))
def admin_give_gtz(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        return
    parts = message.text.split()
    if len(parts) < 2:
        return
    try:
        amount = int(parts[1])
    except:
        return
    if amount <= 0:
        return
    if message.reply_to_message:
        target_id = message.reply_to_message.from_user.id
        target_username = message.reply_to_message.from_user.username or message.reply_to_message.from_user.first_name
    elif len(parts) > 2:
        target_username = parts[2].replace('@', '')
        target_id = None
        for uid, p in players.items():
            if p['username'].lower() == target_username.lower():
                target_id = int(uid)
                break
        if not target_id:
            bot.send_message(message.chat.id, f"❌ Игрок @{target_username} не найден!")
            return
    else:
        target_id = user_id
        target_username = message.from_user.username or message.from_user.first_name
    target = get_player(target_id, target_username)
    target['gtz'] = target.get('gtz', 0) + amount
    save_players()
    bot.send_message(message.chat.id, f"✅ Выдано {amount:,} GtZ💎 игроку @{target['username']}\nЕго баланс GtZ: {target['gtz']:,} 💎".replace(',', '.'))

print("Бот запущен!")
bot.polling(none_stop=True)
