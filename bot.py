import telebot
from telebot import types
import os
import json

TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

user_scores = {}

questions = [
"HTF Structure Aligned?",
"Valid POI Reaction?",
"Liquidity Sweep Taken?",
"Strong BOS + Displacement?",
"15m Entry Precision?",
"Minimum 1:3 R:R Available?",
"Correct Session?",
"Not Emotional?",
"Clean Structure?",
"Not Extended Entry?"
]

# START BOT
@bot.message_handler(commands=['start'])
def start(message):

    user_scores[message.chat.id] = 0
    ask_question(message.chat.id,0)

# ASK QUESTIONS
def ask_question(chat_id,index):

    if index < len(questions):

        markup = types.InlineKeyboardMarkup()

        yes = types.InlineKeyboardButton("✅ Yes",callback_data=f"yes_{index}")
        no = types.InlineKeyboardButton("❌ No",callback_data=f"no_{index}")

        markup.add(yes,no)

        bot.send_message(chat_id,questions[index],reply_markup=markup)

    else:
        final_score(chat_id)

# HANDLE ANSWERS
@bot.callback_query_handler(func=lambda call:True)
def callback(call):

    answer,index = call.data.split("_")
    index = int(index)

    if answer == "yes":
        user_scores[call.message.chat.id] += 10

    ask_question(call.message.chat.id,index+1)

# FINAL SCORE
def final_score(chat_id):

    score = user_scores[chat_id]

    if score >= 90:
        decision = "✅ A+ EXECUTE"
    elif score >= 80:
        decision = "⚠️ B Setup"
    else:
        decision = "❌ Reject"

    bot.send_message(chat_id,f"""
📊 A+ STRUCTURE RESULT

Score: {score}%

Decision: {decision}

Risk Per Trade: $100
Minimum RR: 1:3
""")

    bot.send_message(chat_id,"📸 Send trade screenshot")

# RECEIVE SCREENSHOT
@bot.message_handler(content_types=['photo'])
def photo(message):

    bot.send_message(message.chat.id,"Trade result?\n\nWin / Loss")

# SAVE RESULT
@bot.message_handler(func=lambda m: m.text.lower() in ["win","loss"])
def save_trade(message):

    result = message.text.lower()

    try:
        with open("journal.json","r") as f:
            data = json.load(f)
    except:
        data = []

    data.append({"result":result})

    with open("journal.json","w") as f:
        json.dump(data,f)

    bot.send_message(message.chat.id,"✅ Trade saved in journal")

# SHOW STATS
@bot.message_handler(commands=['stats'])
def stats(message):

    try:
        with open("journal.json","r") as f:
            data = json.load(f)
    except:
        data = []

    wins = sum(1 for x in data if x["result"]=="win")
    losses = sum(1 for x in data if x["result"]=="loss")

    total = wins + losses

    winrate = 0 if total==0 else round(wins/total*100,2)

    bot.send_message(message.chat.id,f"""
📈 TRADING STATS

Trades: {total}
Wins: {wins}
Losses: {losses}

Win Rate: {winrate}%
""")

# RR CALCULATOR
@bot.message_handler(commands=['rr'])
def rr(message):

    try:
        parts = message.text.split()

        entry = float(parts[1])
        stop = float(parts[2])
        target = float(parts[3])

        risk = abs(entry-stop)
        reward = abs(target-entry)

        rr = round(reward/risk,2)

        bot.send_message(message.chat.id,f"""
📊 RR CALCULATION

Entry: {entry}
Stop: {stop}
Target: {target}

Risk: {risk}
Reward: {reward}

RR Ratio: 1:{rr}

Max Risk Allowed: $100
""")

    except:
        bot.send_message(message.chat.id,"Usage:\n/rr entry stop target")

bot.infinity_polling()
