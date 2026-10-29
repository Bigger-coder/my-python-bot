import os
import ast
import subprocess
import py_compile
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# ==================== الإعدادات الأساسية ====================
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("TOKEN") or "توكن"
MY_CHAT_ID = 7597527575  # Chat ID الخاص بك

TEMP_DIR = "user_codes"
os.makedirs(TEMP_DIR, exist_ok=True)

# ==================== خادم ويب لإبقاء البوت 24/7 ====================
app_web = Flask('')

@app_web.route('/')
def home():
    return "🤖 Local Python Analyzer Bot is running 24/7 successfully!"

def run_web():
    app_web.run(host='0.0.0.0', port=7860)

# ==================== الحماية (البوت خاص بك فقط) ====================
def is_authorized(update: Update) -> bool:
    if not update.effective_user:
        return False
    return update.effective_user.id == MY_CHAT_ID

# ==================== جدول ربط أسماء المكاتب بأوامر الـ pip الصحيحة ====================
PIP_MAPPING = {
    'bs4': 'beautifulsoup4',
    'cv2': 'opencv-python',
    'PIL': 'Pillow',
    'skimage': 'scikit-image',
    'sklearn': 'scikit-learn',
    'yaml': 'PyYAML',
    'telegram': 'python-telegram-bot',
    'serial': 'pyserial',
    'Crypto': 'pycryptodome',
    'dotenv': 'python-dotenv'
}

# قائمة المكاتب المدمجة في بايثون (لا تحتاج لتثبيت)
BUILTIN_MODULES = {
    'os', 'sys', 'time', 're', 'json', 'math', 'subprocess', 'threading', 
    'socket', 'asyncio', 'collections', 'itertools', 'functools', 'datetime', 
    'pathlib', 'urllib', 'http', 'logging', 'hashlib', 'base64', 'shutil', 
    'tempfile', 'ast', 'py_compile'
}

def analyze_code_locally(code_content, file_path):
    """تحليل محلي ذكي وصارم بدون أي قيود أو تدخلات خارجية"""
    report = []
    
    # 1. فحص الأخطاء النحوية (Syntax Check)
    try:
        py_compile.compile(file_path, doraise=True)
        syntax_status = "✅ سليمة 100% (لا توجد أخطاء نحوية تمنع التشغيل)."
    except Exception as e:
        syntax_status = f"❌ خطأ نحوي (SyntaxError):\n`{str(e)}`"

    # 2. استخراج المكاتب عبر AST بدقة متناهية
    detected_modules = set()
    try:
        tree = ast.parse(code_content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    mod = alias.name.split('.')[0]
                    if mod not in BUILTIN_MODULES:
                        detected_modules.add(mod)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    mod = node.module.split('.')[0]
                    if mod not in BUILTIN_MODULES:
                        detected_modules.add(mod)
    except Exception:
        pass

    # تجهيز أوامر التثبيت الدقيقة
    pip_commands = []
    for mod in detected_modules:
        pkg_name = PIP_MAPPING.get(mod, mod)
        pip_commands.append(f"pip install {pkg_name}")

    pip_text = " \n".join(pip_commands) if pip_commands else "لا توجد مكاتب خارجية تتطلب تثبيتاً."

    # 3. إحصائيات الكود
    lines = code_content.splitlines()
    total_lines = len(lines)
    code_lines = sum(1 for l in lines if l.strip() and not l.strip().startswith('#'))
    comment_lines = sum(1 for l in lines if l.strip().startswith('#'))
    func_count = sum(1 for l in lines if l.strip().startswith('def '))
    class_count = sum(1 for l in lines if l.strip().startswith('class '))

    # بناء التقرير الشامل
    result = (
        "📊 **التقرير التحليلي الشامل لكودك:**\n\n"
        f"🛠 **حالة البناء:** {syntax_status}\n\n"
        f"📦 **المكاتب الخارجية المكتشفة وأوامر تثبيتها:**\n"
        f"```bash\n{pip_text}\n```\n\n"
        f"📈 **إحصائيات الهيكل البرمجي:**\n"
        f"• إجمالي الأسطر: `{total_lines}`\n"
        f"• أسطر الأكواد الفعالة: `{code_lines}`\n"
        f"• أسطر التعليقات: `{comment_lines}`\n"
        f"• عدد الدوال (`def`): `{func_count}`\n"
        f"• عدد الكلاسات (`class`): `{class_count}`\n\n"
        "💡 **ملاحظة:** تم تحليل كودك محلياً دون أي قيود أو تعديل على فكرتك الأساسية."
    )
    return result

# ==================== الأوامر والمعالجات ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        await update.message.reply_text("⛔ عذراً، هذا البوت خاص ولا يمكنك استخدامه.")
        return

    welcome_text = (
        "🚀 **أهلاً بك في محلل أكواد Python المحلي (بدون قيود وبدقة كاملة)!**\n\n"
        "📁 أرسل لي أي ملف بايثون (`.py`) بغض النظر عن محتواه (شبكات، أدوات أمنية، بوتات، إلخ) وسأقوم بـ:\n"
        "1️⃣ **فحص الأخطاء النحوية.**\n"
        "2️⃣ **استخراج المكاتب وإعطاؤك أوامر `pip install` الدقيقة.**\n"
        "3️⃣ **حفظ فكرة الكود الأصلية 100% دون أي تخريب.**"
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
        [InlineKeyboardButton("📊 تحليل الكود وإظهار أوامر التثبيت", callback_data="analyze_local")],
        [InlineKeyboardButton("🛠 تظبيط وتنسيق الكود (Autopep8)", callback_data="format_code")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"📥 **تم استلام الملف بنجاح:** `{doc.file_name}`\nاختر العملية المطلوبة:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    file_path = context.user_data.get('current_file')
    file_name = context.user_data.get('file_name', 'script.py')

    if not file_path or not os.path.exists(file_path):
        await query.edit_message_text("❌ انتهت صلاحية الملف، يرجى إرساله من جديد.")
        return

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        code_content = f.read()

    if query.data == "analyze_local":
        await query.edit_message_text("⏳ جاري تحليل الكود واستخراج المكاتب محلياً...")
        report = analyze_code_locally(code_content, file_path)
        await query.message.reply_text(report, parse_mode="Markdown")

    elif query.data == "format_code":
        await query.edit_message_text("⏳ جاري إعادة تنسيق وتتظبيط الكود...")
        # تنسيق آلي نظيف عبر autopep8 دون تغيير المنطق
        subprocess.run(["autopep8", "--in-place", "--aggressive", "--aggressive", file_path])
        
        with open(file_path, 'rb') as f:
            await query.message.reply_document(
                document=f,
                filename=f"clean_{file_name}",
                caption="✅ **تم تنسيق الكود وترتيبه بنجاح مع الحفاظ على فكرته الأصلية تماماً!**",
                parse_mode="Markdown"
            )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    print(f"Error: {context.error}")

# ==================== التشغيل الرئيسي ====================
if __name__ == '__main__':
    t = threading.Thread(target=run_web)
    t.daemon = True
    t.start()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_error_handler(error_handler)

    print("⚡ البوت المحلي المطور يعمل بنجاح...")
    app.run_polling()
