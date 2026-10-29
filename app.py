import os
import requests
import subprocess
import py_compile
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# ==================== الإعدادات الأساسية ====================
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("TOKEN") or "توكن"
MY_CHAT_ID = 7597527575  # Chat ID الخاص بك

# مجلد مؤقت لحفظ الملفات المرسلة
TEMP_DIR = "user_codes"
os.makedirs(TEMP_DIR, exist_ok=True)

# ==================== خادم ويب لإبقاء البوت 24/7 ====================
app_web = Flask('')

@app_web.route('/')
def home():
    return "🤖 Python Debug Bot is running 24/7 successfully!"

def run_web():
    app_web.run(host='0.0.0.0', port=7860)

# ==================== الحماية (البوت خاص بك فقط) ====================
def is_authorized(update: Update) -> bool:
    if not update.effective_user:
        return False
    return update.effective_user.id == MY_CHAT_ID

# ==================== الأوامر والمعالجات ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        await update.message.reply_text("⛔ عذراً، هذا البوت خاص ولا يمكنك استخدامه.")
        return

    welcome_text = (
        "🚀 **أهلاً بك في بوت تطوير وتصحيح كود Python!**\n\n"
        "📁 أرسل لي أي ملف بايثون (`.py`) وسأوفر لك الأدوات التالية:\n"
        "1️⃣ **التنسيق والتصحيح الآلي:** عبر `autopep8` و `pylint`.\n"
        "2️⃣ **فحص الأخطاء النحوية وإحصائيات الكود.**\n"
        "3️⃣ **دليل التطوير والهندسة البرمجية.**\n"
        "4️⃣ **بحث GitHub الذكي.**"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return

    doc = update.message.document
    if not doc or not doc.file_name or not doc.file_name.endswith('.py'):
        await update.message.reply_text("❌ يرجى إرسال ملف بصيغة `.py` فقط.")
        return

    file = await doc.get_file()
    file_path = os.path.join(TEMP_DIR, doc.file_name)
    await file.download_to_drive(file_path)

    context.user_data['current_file'] = file_path
    context.user_data['file_name'] = doc.file_name

    keyboard = [
        [InlineKeyboardButton("🛠 تصحيح وتنسيق الكود (Fix & Lint)", callback_data="fix_code")],
        [InlineKeyboardButton("📊 تحليل الإحصائيات وفحص الأخطاء", callback_data="check_syntax")],
        [InlineKeyboardButton("🚀 دليل التطوير والهندسة البرمجية", callback_data="enhance_code")],
        [InlineKeyboardButton("🔍 البحث في GitHub عن مكتبات ذات صلة", callback_data="search_github")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"📥 **تم استلام الملف بنجاح:** `{doc.file_name}`\nاختر العملية التي تريد تنفيذها:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    file_path = context.user_data.get('current_file')
    file_name = context.user_data.get('file_name', 'script.py')

    if not file_path or not os.path.exists(file_path):
        await query.edit_message_text("❌ لم يتم العثور على الملف أو انتهت صلاحيته. يرجى إرساله من جديد.")
        return

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        code_content = f.read()

    # 1️⃣ خيار تصحيح وتنسيق الكود
    if query.data == "fix_code":
        await query.edit_message_text("⏳ جاري إعادة تنسيق الكود وفحصه...")

        # تصليح التنسيق عبر autopep8
        subprocess.run(["autopep8", "--in-place", "--aggressive", "--aggressive", file_path])

        # فحص الأخطاء عبر pylint (قص التقرير ليناسب حد تليجرام 1024 حرف للـ caption)
        pylint_res = subprocess.run(["pylint", file_path], capture_output=True, text=True)
        raw_report = pylint_res.stdout if pylint_res.stdout else "الكود ممتاز ولا توجد ملاحظات."
        report = raw_report[:600] if len(raw_report) > 600 else raw_report

        with open(file_path, 'rb') as f:
            await query.message.reply_document(
                document=f,
                filename=f"fixed_{file_name}",
                caption=f"✅ **تم التصحيح بنجاح!**\n\n📋 **تقرير الأخطاء المختصر:**\n```\n{report}\n```",
                parse_mode="Markdown"
            )

    # 2️⃣ خيار تحليل الإحصائيات وفحص الأخطاء النحوية
    elif query.data == "check_syntax":
        await query.edit_message_text("⏳ جاري تحليل الكود واستخراج الإحصائيات...")

        try:
            py_compile.compile(file_path, doraise=True)
            syntax_status = "✅ سليمة 100% (لا توجد أخطاء نحوية)."
        except Exception as e:
            syntax_status = f"❌ توجد مشكلة نحوية:\n`{str(e)}`"

        lines = code_content.splitlines()
        total_lines = len(lines)
        code_lines = sum(1 for l in lines if l.strip() and not l.strip().startswith('#'))
        comment_lines = sum(1 for l in lines if l.strip().startswith('#'))
        func_count = sum(1 for l in lines if l.strip().startswith('def '))
        class_count = sum(1 for l in lines if l.strip().startswith('class '))

        stats_text = (
            "📊 **إحصائيات وفحص الكود البرمجي:**\n\n"
            f"• **حالة البناء النحوي:** {syntax_status}\n"
            f"• **إجمالي الأسطر:** `{total_lines}`\n"
            f"• **أسطر الأكواد الفعالة:** `{code_lines}`\n"
            f"• **أسطر التعليقات:** `{comment_lines}`\n"
            f"• **عدد الدوال (`def`):** `{func_count}`\n"
            f"• **عدد الكلاسات (`class`):** `{class_count}`"
        )
        await query.message.reply_text(stats_text, parse_mode="Markdown")

    # 3️⃣ خيار دليل التطوير والهندسة البرمجية
    elif query.data == "enhance_code":
        await query.edit_message_text("⏳ جاري تجهيز دليل هندسة وتطوير الكود...")

        imports = [line.strip() for line in code_content.splitlines() if line.startswith(('import ', 'from '))]
        imports_list = "\n".join(imports) if imports else "لا توجد مكاتب خارجية مستوردة."

        instructions = (
            "🚀 **دليل هندسة وتطوير الكود:**\n\n"
            "📌 **المكاتب المكتشفة:**\n"
            f"```python\n{imports_list}\n```\n\n"
            "💡 **توصيات لتحسين الأداء:**\n"
            "1. **معالجة الاستثناءات:** استخدام `try...except` للعمليات الحساسة.\n"
            "2. **التوثيق:** إضافة وصف (`Docstrings`) تحت الدوال لتسهيل القراءة."
        )
        await query.message.reply_text(instructions, parse_mode="Markdown")

    # 4️⃣ خيار البحث في GitHub
    elif query.data == "search_github":
        await query.edit_message_text("🔍 جاري البحث في مستودعات GitHub...")

        keywords = "python"
        for line in code_content.splitlines():
            if line.startswith("import ") or line.startswith("from "):
                parts = line.split()
                if len(parts) > 1 and parts[1] not in ['os', 'sys', 'time', 're', 'json', 'math']:
                    keywords = parts[1].split('.')[0]
                    break

        url = f"https://api.github.com/search/repositories?q={keywords}+language:python&sort=stars&order=desc"
        headers = {"User-Agent": "Python-Telegram-Bot"}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])[:3]

            res_text = f"🔎 **أبرز مشاريع GitHub المرتبطة بـ (`{keywords}`):**\n\n"
            for item in items:
                res_text += f"⭐ **[{item['name']}]({item['html_url']})**\n"
                res_text += f"📝 {item['description'] or 'بدون وصف'}\n\n"
        else:
            res_text = "❌ عذراً، تعذر الوصول إلى بحث GitHub حالياً."

        await query.message.reply_text(res_text, parse_mode="Markdown", disable_web_page_preview=True)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """معالج الأخطاء العام لمنع توقف البوت"""
    print(f"Update {update} caused error {context.error}")

# ==================== التشغيل الرئيسي ====================
if __name__ == '__main__':
    # 1. تشغيل سيرفر الويب الخلفي
    t = threading.Thread(target=run_web)
    t.daemon = True
    t.start()

    # 2. تشغيل بوت تليجرام
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_error_handler(error_handler)

    print("⚡ البوت المطور يعمل بنجاح ومحمي بالكامل...")
    app.run_polling()
