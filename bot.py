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

# የውይይት ደረጃዎች
FULL_NAME, PHONE, DORM, ID_PHOTO, RECEIPT_PHOTO = range(5)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  user_name = update.effective_user.first_name

  # የፈጣን ሊንክ ክትትል (/start ref_XXXXXX)
  args = context.args
  if args and args[0].startswith("ref_"):
    referrer_id = args[0].split("_")[1]
    context.user_data["referrer_id"] = referrer_id
    logging.info(
        f"User {update.effective_user.id} came via referrer {referrer_id}"
    )

  keyboard = [
      [KeyboardButton("📝 በዕቁብ መመዝገብ")],
      [KeyboardButton("📊 የዕቁብ ስንጠርና & አጣ")],
      [KeyboardButton("🔗 የሼር ሊንክ")],
      [KeyboardButton("💰 የብድር አገልግሎት")],
      [KeyboardButton("💳 ክፍያ ማስታወቂያ / ሪፖርት")],
  ]
  reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

  welcome_text = (
      f"ሰላም <b>{user_name}</b>! ✨\n\n"
      f"🏦 የተማሪዎችን ህይወት የሚያቃልል፡ አስተማማኝና"
      f" ፈጣን የደጁዕ ዕቁብ እና የብድር አገልግሎት::\n"
      f"──────────────── 🌟 <b>ልዩ ጥቅሞች</b> 🌟"
      f"────────────────\n"
      f"◆ <b>የዕቁብ ድን፦</b> ቀደም 5 ሰው ላመጣኘ"
      f" የ 500 ብር / የ 2% ቅናሽ ሙሉለ ሙሉ ይሰጣል!\n"
      f"◆ <b>የብድር አገልግሎት፦</b> እስከ 20,000 ብር"
      f" የሚደርስ የብድር አገልግሎት\n"
      f"◆ <b>ግልፅ አሰራር፦</b> የቀጥታ (Live) አጣ"
      f" ማውጫ እና የስንጠርና ክትትል\n"
      f"👇 <b>ለመጀመር ከዚህ በታች ካሉ አማራጮች አንዱን"
      f" ይምረጡ፦</b>"
  )

  await update.message.reply_text(
      welcome_text, parse_mode="HTML", reply_markup=reply_markup
  )


# --- የምዝገባ ፍሰት (Registration Flow) ---


async def start_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await update.message.reply_text(
      "👤 አዎህን ሙሉ ስምዎን ያስገቡ:-"
  )
  return FULL_NAME


async def get_full_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data["full_name"] = update.message.text
  await update.message.reply_text("📱 አዎህን ስልክ ቁጥርዎን ያስገቡ:-")
  return PHONE


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data["phone"] = update.message.text
  await update.message.reply_text("🏢 አዎህን ብሎክ እና የድሮም ቁጥርዎን ያስገቡ:-")
  return DORM


async def get_dorm(update: Update, context: ContextTypes.DEFAULT_TYPE):
  context.user_data["dorm"] = update.message.text
  await update.message.reply_text("🆔 አዎህን የዩኒቨርሲቲ መታወቂያ (Student ID) ፎቶ ይላኩ:-")
  return ID_PHOTO


async def get_id_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
  if not update.message.photo:
    await update.message.reply_text("⚠️ አዎህን የመታወቂያዎን ፎቶ ይላኩ!")
    return ID_PHOTO

  context.user_data["id_photo"] = update.message.photo[-1].file_id

  payment_instruction = (
      "ወደ KY Digital Equb አባላት ለመቀላቀል የሚከተሉትን"
      " ክፍያዎች ይፈፅሙ:-\n\n"
      "💳 <b>የሚከፈል ክፍያ:</b>\n"
      "• አንዴ ጊዜ የመመዝገቢያ ክፍያ: 50 ብር\n"
      "• የመጀመሪያው ሳምንት እቁብ ክፍያ: [50 - 100 ብር]\n\n"
      "📌 <b>መክፈል ያለብዎት:</b> የመመዝገቢያ"
      " (50 ብር) + የእቁብ ክፍያ\n"
      "• 📲 <b>Telebirr:</b> <code>0985625604</code> (Kaleab Haile W/Abrha)\n"
      "• 🏦 <b>CBE (ንግድ ባንክ):</b>"
      " <code>1000657786342</code> (Kaleab Haile W/Abrha)\n\n"
      " ክፍያውን ከፈፀሙ በኋላ ከታች ያለውን '💳 ክፍያ"
      " ማስታወቂያ / ሪፖርት' ቁልፍ በመንካት የትራንዛክሽኑን ሩት/ደረሰኝ"
      " ይላኩ!"
  )

  await update.message.reply_text(payment_instruction, parse_mode="HTML")
  return ConversationHandler.END


# --- የክፍያ ሪፖርት ፍሰት (Payment Report Flow) ---


async def start_payment_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
  await update.message.reply_text(
      "📸 አዎህን የክፍያውን የተራንዛክሽን ሩት/ደረሰኝ ይላኩ:-"
  )
  return RECEIPT_PHOTO


async def process_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
  if not update.message.photo:
    await update.message.reply_text("⚠️ አዎህን ደረሰኝዎን በፎቶ መልክ ይላኩ!")
    return RECEIPT_PHOTO

  receipt_photo_id = update.message.photo[-1].file_id
  user = update.effective_user

  full_name = context.user_data.get("full_name", "አልተገለጸም")
  phone = context.user_data.get("phone", "አልተገለጸም")
  dorm = context.user_data.get("dorm", "አልተገለጸም")
  referrer = context.user_data.get("referrer_id", "በቀጥታ የመጣ (ሰፈራ የለውም)")

  admin_msg = (
      f"📥 <b>አዲስ የምዝገባ እና የክፍያ መልእክት!</b>\n\n"
      f"👤 <b>ስም:</b> {full_name}\n"
      f"📱 <b>ስልክ:</b> {phone}\n"
      f"🏢 <b>ብሎክ/ድሮም:</b> {dorm}\n"
      f"🆔 <b>User ID:</b> <code>{user.id}</code>\n"
      f"👤 <b>Telegram:</b> @{user.username if user.username else 'የለውም'}\n"
      f"🔗 <b>የየነሆ ሰው (Referrer ID):</b>"
      f" <code>{referrer}</code>"
  )

  keyboard = [
      [
          InlineKeyboardButton(
              "✅ Approve (አፀድቅ)", callback_data=f"approve_{user.id}"
          ),
          InlineKeyboardButton(
              "❌ Reject (አጥፍ)", callback_data=f"reject_{user.id}"
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
      "⏳ <b>መረጃ እና ክፍያ ተቀብለናል! (Pending)</b>\n\n"
      "በአድሚን ተመርምሮ እስኪረጋገጥ በፅዕነት ይጠብቁ!",
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
        "🎉 <b>እንኳን ደስ አለዎት!</b> አሁን ሙሉ ሙሉ የ"
        " <b>KY Digital Equb</b> አባል መ되ዋል::\n"
        f"🎲 <b>የዕቁብ Live አጣ ማውጫ ገፅ:-</b>\n{WEBAPP_URL}\n"
        f"📢 <b>የየተማሩም ቻናላችን:-</b>\n{CHANNEL_URL}\n"
        f"🔗 <b>የእርስዎ ልዩ ሼር ሊንክ:-</b>\n<code>{ref_link}</code>\n"
        "📌 በስርጭ 5 ሰው የሚመዘግቡበትን ሊንክ '🔗 ሼር'"
        " button በመንካት ስልዎትን የመመዝገቢያ ሊንክ ያግኙ!"
    )
    await context.bot.send_message(
        chat_id=target_user_id, text=success_text, parse_mode="HTML"
    )
    await query.edit_message_caption(
        caption=query.message.caption + "\n\n✅ <b>ተፅዷል (Approved)!</b>",
        parse_mode="HTML",
    )

  elif action == "reject":
    reject_text = (
        "❌ <b>ይቅርታ!</b> የክፍያ ወይም የምዝገባ"
        " መረጃ በአድሚን አልፀደቀም::\n"
        "አዎህን መረጃውን አሰተካክለው እንደገና ይላኩ ወይም"
        " አድሚንን ያነጋገሩ:- @KY_market_admin"
    )
    await context.bot.send_message(
        chat_id=target_user_id, text=reject_text, parse_mode="HTML"
    )
    await query.edit_message_caption(
        caption=query.message.caption + "\n\n❌ <b>ተሰርዟል (Rejected)!</b>",
        parse_mode="HTML",
    )


# --- አጠቃላይ አክሰሶች ---


async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
  text = update.message.text

  if text == "📊 የዕቁብ ስንጠርና & አጣ":
    inline_keyboard = [
        [InlineKeyboardButton("🌐 የዕቁብ ቅንይት ክፈት (Live)", url=WEBAPP_URL)]
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard)
    await update.message.reply_text(
        "📊 <b>የቀጥታ (Live) የዕቁብ ስንጠርና እና አጣ"
        " ማውጫ ገፅ:</b>\n\n"
        "ከዚህ በታች ባለው ሊንክ በመግባት ቀኑን መከታተል እና አጣ"
        " መመልከት ይችላሉ!",
        parse_mode="HTML",
        reply_markup=reply_markup,
    )

  elif text == "🔗 ሼር ሊንክ":
    bot_username = (await context.bot.get_me()).username
    user_id = update.effective_user.id
    referral_link = f"https://t.me/{bot_username}?start=ref_{user_id}"

    ref_text = (
        f"🔗 <b>የእርስዎ ልዩ ሼር ሊንክ:</b>\n"
        f"<code>{referral_link}</code>\n"
        f"📌 ቀደምሙ 5 ሰው በመጋበዝ የ 500 ብር / የ"
        f" 2% ቅናሽ ሙሉ ሙሉ ነፃ ይድርግ!"
    )
    await update.message.reply_text(ref_text, parse_mode="HTML")

  elif text == "💰 የብድር አገልግሎት":
    loan_text = (
        f"💰 <b>የብድር አገልግሎት መመሪያ:</b>\n"
        f"• ለዕቁብ አባላት ብቻ እስከ 20,000 ብር የሚደርስ"
        f" ብር እንሰጣለን::\n"
        f"• ጥያቄ ለማቅረብ አድሚናችንን ማነጋገር ይቻላል::\n"
        f"እድሚን: @KY_market_admin"
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
