import logging
import os
from threading import Thread
from flask import Flask

# --- Flask Web Server for UptimeRobot ---
app = Flask("")


@app.route("/")
def home():
  return "KY Bot is Alive!"


def run():
  app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))


def keep_alive():
  t = Thread(target=run)
  t.daemon = True
  t.start()


keep_alive()

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    Update,
)
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

TOKEN = "8993924043:AAHtYJM0TBJJm7wM1VAe4YdOvNPj6pNtc0o"
WEBAPP_URL = "https://ky-digital-equb-new.vercel.app"
CHANNEL_URL = "https://t.me/ky_digital_equb_channel"

# የአድሚን Telegram User ID
ADMIN_CHAT_ID = 883306072

# የተመዘገቡ ተጠቃሚዎችን ID መያዣ (In-Memory Database)
registered_users = set()

# የውይይት ደረጃዎች
FULL_NAME, PHONE, DORM, ID_PHOTO, RECEIPT_PHOTO = range(5)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  user_id = update.effective_user.id
  registered_users.add(user_id)  # ተጠቃሚውን ለሪማይንደር መዝግብ
  user_name = update.effective_user.first_name

  # የፈጣን ሊንክ ክትትል (/start ref_XXXXXX)
  args = context.args
  if args and args[0].startswith("ref_"):
    referrer_id = args[0].split("_")[1]
    context.user_data["referrer_id"] = referrer_id
    logging.info(f"User {user_id} came via referrer {referrer_id}")

  keyboard = [
      [KeyboardButton("📝 በዕቁብ መመዝገብ")],
      [KeyboardButton("📊 የዕቁብ ሠንጠረዥ & ዕጣ")],
      [KeyboardButton("🔗 የሼር ሊንክ")],
      [KeyboardButton("💰 የብድር አገልግሎት")],
      [KeyboardButton("💳 ክፍያ ማስታወቂያ / ሪፖርት")],
  ]
  reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

  welcome_text = (
      f"ሰላም <b>{user_name}</b>! ✨\n\n"
      f"🏦 የተማሪዎችን ህይወት የሚያቃልል፡ አስተማማኝና"
      f" ፈጣን የዲጂታል ዕቁብ እና የብድር አገልግሎት::\n"
      f"──────────────── 🌟 <b>ልዩ ጥቅሞች</b> 🌟"
      f"────────────────\n"
      f"◆ <b>የዕቁብ ሽልማት፦</b> ቀድሞ 5 ሰው ላመጣ"
      f" የ 500 ብር / የ 2% ቅናሽ ሙሉ ለሙሉ ይሰጣል!\n"
      f"◆ <b>የብድር አገልግሎት፦</b> እስከ 20,000 ብር"
      f" የሚደርስ የብድር አገልግሎት\n"
      f"◆ <b>ግልጽ አሰራር፦</b> የቀጥታ (Live) ዕጣ"
      f" ማውጫ እና የሠንጠረዥ ክትትል\n\n"
      f"👇 <b>ለመጀመር ከዚህ በታች ካሉ አማራጮች አንዱን"
      f" ይምረጡ፦</b>"
  )

  await update.message.reply_text(
      welcome_text, parse_mode="HTML", reply_markup=reply_markup
  )


# --- የምዝገባ ፍሰት (Registration Flow) ---


async def start_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await update.message.reply_text("👤 እባክዎን ሙሉ ስምዎን ያስገቡ:-")
  return FULL_NAME


async def get_full_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data["full_name"] = update.message.text
  await update.message.reply_text("📱 እባክዎን ስልክ ቁጥርዎን ያስገቡ:-")
  return PHONE


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data["phone"] = update.message.text
  await update.message.reply_text(
      "🏢 እባክዎን ብሎክ እና የዶርም ቁጥርዎን ያስገቡ:-"
  )
  return DORM


async def get_dorm(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data["dorm"] = update.message.text
  await update.message.reply_text(
      "🆔 እባክዎን የዩኒቨርሲቲ መታወቂያ (Student ID) ፎቶ ይላኩ:-"
  )
  return ID_PHOTO


async def get_id_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
  if not update.message.photo:
    await update.message.reply_text("⚠️ እባክዎን የመታወቂያዎን ፎቶ ይላኩ!")
    return ID_PHOTO

  context.user_data["id_photo"] = update.message.photo[-1].file_id

  payment_instruction = (
      "ወደ KY Digital Equb አባላት ለመቀላቀል የሚከተሉትን"
      " ክፍያዎች ይፈፅሙ:-\n\n"
      "💳 <b>የሚከፈል ክፍያ:</b>\n"
      "• የአንድ ጊዜ የመመዝገቢያ ክፍያ: 50 ብር\n"
      "• የመጀመሪያው ሳምንት ዕቁብ ክፍያ: [50 - 100 ብር]\n\n"
      "📌 <b>መክፈል ያለብዎት:</b> የመመዝገቢያ"
      " (50 ብር) + የዕቁብ ክፍያ\n"
      "• 📲 <b>Telebirr:</b> <code>0985625604</code> (Kaleab Haile W/Abrha)\n"
      "• 🏦 <b>CBE (ንግድ ባንክ):</b>"
      " <code>1000657786342</code> (Kaleab Haile W/Abrha)\n\n"
      "ክፍያውን ከፈፀሙ በኋላ ከታች ያለውን '💳 ክፍያ"
      " ማስታወቂያ / ሪፖርት' ቁልፍ በመንካት የትራንዛክሽኑን ደረሰኝ"
      " ይላኩ!"
  )

  await update.message.reply_text(payment_instruction, parse_mode="HTML")
  return ConversationHandler.END


# --- የክፍያ ሪፖርት ፍሰት (Payment Report Flow) ---


async def start_payment_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await update.message.reply_text(
      "📸 እባክዎን የክፍያውን የትራንዛክሽን ደረሰኝ ፎቶ ይላኩ:-"
  )
  return RECEIPT_PHOTO


async def process_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
  if not update.message.photo:
    await update.message.reply_text("⚠️ እባክዎን ደረሰኝዎን በፎቶ መልክ ይላኩ!")
    return RECEIPT_PHOTO

  receipt_photo_id = update.message.photo[-1].file_id
  user = update.effective_user

  full_name = context.user_data.get("full_name", "አልተገለጸም")
  phone = context.user_data.get("phone", "አልተገለጸም")
  dorm = context.user_data.get("dorm", "አልተገለጸም")
  referrer = context.user_data.get("referrer_id", "በቀጥታ የመጣ (ሪፈራል የለውም)")

  admin_msg = (
      f"📥 <b>አዲስ የምዝገባ እና የክፍያ ማመልከቻ!</b>\n\n"
      f"👤 <b>ስም:</b> {full_name}\n"
      f"📱 <b>ስልክ:</b> {phone}\n"
      f"🏢 <b>ብሎክ/ዶርም:</b> {dorm}\n"
      f"🆔 <b>User ID:</b> <code>{user.id}</code>\n"
      f"👤 <b>Telegram:</b> @{user.username if user.username else 'የለውም'}\n"
      f"🔗 <b>የጋበዘው ሰው (Referrer ID):</b>"
      f" <code>{referrer}</code>"
  )

  keyboard = [
      [
          InlineKeyboardButton(
              "✅ አጽድቅ (Approve)", callback_data=f"approve_{user.id}"
          ),
          InlineKeyboardButton(
              "❌ አትቀበል (Reject)", callback_data=f"reject_{user.id}"
          ),
      ]
  ]
  reply_markup = InlineKeyboardMarkup(keyboard)

  try:
    await context.bot.send_photo(
        chat_id=ADMIN_CHAT_ID,
        photo=receipt_photo_id,
        caption=admin_msg,
        parse_mode="HTML",
        reply_markup=reply_markup,
    )
  except Exception as e:
    logging.error(f"Failed to send to admin: {e}")

  await update.message.reply_text(
      "⏳ <b>መረጃዎ እና የክፍያ ደረሰኝዎ ተቀብለናል! (Pending)</b>\n\n"
      "በአድሚን ተመርምሮ እስኪረጋገጥ በትዕግስት ይጠብቁ!",
      parse_mode="HTML",
  )
  return ConversationHandler.END


# --- አድሚን Approve/Reject ሎጂክ ---


async def handle_admin_approval(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
  query = update.callback_query
  await query.answer()

  data = query.data
  action, target_user_id = data.split("_")
  target_user_id = int(target_user_id)

  bot_username = (await context.bot.get_me()).username
  ref_link = f"https://t.me/{bot_username}?start=ref_{target_user_id}"

  if action == "approve":
    success_text = (
        "🎉 <b>እንኳን ደስ አለዎት!</b> አሁን ሙሉ ለሙሉ የ"
        " <b>KY Digital Equb</b> አባል ሆነዋል::\n\n"
        f"🎲 <b>የዕቁብ Live ዕጣ ማውጫ ገፅ:-</b>\n{WEBAPP_URL}\n\n"
        f"📢 <b>የቴሌግራም ቻናላችን:-</b>\n{CHANNEL_URL}\n\n"
        f"🔗 <b>የእርስዎ ልዩ የሼር ሊንክ:-</b>\n<code>{ref_link}</code>\n\n"
        "📌 ይህንን ሊንክ ለ 5 ሰው በማጋራትና በመጋበዝ የ 500 ብር"
        " ወይም የ 2% ቅናሽ ያግኙ!"
    )
    await context.bot.send_message(
        chat_id=target_user_id, text=success_text, parse_mode="HTML"
    )
    await query.edit_message_caption(
        caption=query.message.caption + "\n\n✅ <b>ጸድቋል (Approved)!</b>",
        parse_mode="HTML",
    )

  elif action == "reject":
    reject_text = (
        "❌ <b>ይቅርታ!</b> የክፍያ ወይም የምዝገባ"
        " መረጃዎ በአድሚን አልፀደቀም::\n\n"
        "እባክዎን መረጃውን አስተካክለው እንደገና ይላኩ ወይም"
        " አድሚንን ያነጋግሩ:- @KY_market_admin"
    )
    await context.bot.send_message(
        chat_id=target_user_id, text=reject_text, parse_mode="HTML"
    )
    await query.edit_message_caption(
        caption=query.message.caption + "\n\n❌ <b>ተሰርዟል (Rejected)!</b>",
        parse_mode="HTML",
    )


# --- የአድሚን የብሮድካስት ማሳሰቢያ (Reminder) ---


async def send_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
  if update.effective_user.id != ADMIN_CHAT_ID:
    await update.message.reply_text("⛔ ይህ ትዕዛዝ ለአድሚን ብቻ የተፈቀደ ነው!")
    return

  reminder_msg = (
      "⚠️ <b>የክፍያ ማሳሰቢያ!</b>\n\n"
      "የመክፈያ ጊዜው እስከ ማታ 3:00 ሰዓት ድረስ ብቻ ስለሆነ"
      " እባክዎን ክፍያዎን በጊዜ ይፈፅሙ!\n\n"
      "ክፍያውን እንደፈጸሙ የትራንዛክሽን ደረሰኝዎን ከታች ባለው"
      " '💳 ክፍያ ማስታወቂያ / ሪፖርት' ቁልፍ በመጫን ይላኩ።"
  )

  success_count = 0
  for uid in registered_users:
    try:
      await context.bot.send_message(
          chat_id=uid, text=reminder_msg, parse_mode="HTML"
      )
      success_count += 1
    except Exception as e:
      logging.error(f"Could not send reminder to {uid}: {e}")

  await update.message.reply_text(
      f"✅ ማሳሰቢያው ለ {success_count} ተጠቃሚዎች በስኬት ተላክ!"
  )


# --- አጠቃላይ አክሰሶች ---


async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
  text = update.message.text
  registered_users.add(update.effective_user.id)

  if text == "📊 የዕቁብ ሠንጠረዥ & ዕጣ":
    inline_keyboard = [
        [InlineKeyboardButton("🌐 የዕቁብ ዌብሳይት ክፈት (Live)", url=WEBAPP_URL)]
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard)
    await update.message.reply_text(
        "📊 <b>የቀጥታ (Live) የዕቁብ ሠንጠረዥ እና ዕጣ"
        " ማውጫ ገፅ:</b>\n\n"
        "ከዚህ በታች ባለው ሊንክ በመግባት ሂደቱን መከታተል እና ዕጣ"
        " መመልከት ይችላሉ!",
        parse_mode="HTML",
        reply_markup=reply_markup,
    )

  elif text == "🔗 የሼር ሊንክ":
    bot_username = (await context.bot.get_me()).username
    user_id = update.effective_user.id
    referral_link = f"https://t.me/{bot_username}?start=ref_{user_id}"

    ref_text = (
        f"🔗 <b>የእርስዎ ልዩ የሼር ሊንክ:</b>\n"
        f"<code>{referral_link}</code>\n\n"
        f"📌 ቀድመው 5 ሰው በመጋበዝ የ 500 ብር / የ"
        f" 2% ቅናሽ ተጠቃሚ ይሁኑ!"
    )
    await update.message.reply_text(ref_text, parse_mode="HTML")

  elif text == "💰 የብድር አገልግሎት":
    loan_text = (
        f"💰 <b>የብድር አገልግሎት መመሪያ:</b>\n\n"
        f"• ለዕቁብ አባላት ብቻ እስከ 20,000 ብር የሚደርስ"
        f" ብድር እንሰጣለን::\n"
        f"• ጥያቄ ለማቅረብ አድሚናችንን ማነጋገር ይቻላል::\n"
        f"አድሚን: @KY_market_admin"
    )
    await update.message.reply_text(loan_text, parse_mode="HTML")


def main():
  application = ApplicationBuilder().token(TOKEN).build()

  reg_handler = ConversationHandler(
      entry_points=[
          MessageHandler(filters.Regex("^📝 በዕቁብ መመዝገብ$"), start_registration)
      ],
      states={
          FULL_NAME: [
              MessageHandler(filters.TEXT & ~filters.COMMAND, get_full_name)
          ],
          PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
          DORM: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_dorm)],
          ID_PHOTO: [MessageHandler(filters.PHOTO, get_id_photo)],
      },
      fallbacks=[],
  )

  pay_handler = ConversationHandler(
      entry_points=[
          MessageHandler(
              filters.Regex("^💳 ክፍያ ማስታወቂያ / ሪፖርት$"), start_payment_report
          )
      ],
      states={RECEIPT_PHOTO: [MessageHandler(filters.PHOTO, process_receipt)]},
      fallbacks=[],
  )

  application.add_handler(CommandHandler("start", start))
  application.add_handler(CommandHandler("remind", send_reminder))  # ማሳሰቢያ መላኪያ
  application.add_handler(reg_handler)
  application.add_handler(pay_handler)
  application.add_handler(
      CallbackQueryHandler(handle_admin_approval, pattern="^(approve|reject)_")
  )
  application.add_handler(
      MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons)
  )

  print("Bot is running successfully...")
  application.run_polling()


if __name__ == "__main__":
  main()
