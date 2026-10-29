import os
import ast
import subprocess
import py_compile
import threading
import requests
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
    return "🤖 Advanced Logic Code Reviewer Bot is running 24/7!"

def run_web():
    app_web.run(host='0.0.0.0', port=7860)

# ==================== الحماية (البوت خاص بك فقط) ====================
def is_authorized(update: Update) -> bool:
    if not update.effective_user:
        return False
    return update.effective_user.id == MY_CHAT_ID

# جدول ربط المكاتب
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

BUILTIN_MODULES = {
    'os', 'sys', 'time', 're', 'json', 'math', 'subprocess', 'threading', 
    'socket', 'asyncio', 'collections', 'itertools', 'functools', 'datetime', 
    'pathlib', 'urllib', 'http', 'logging', 'hashlib', 'base64', 'shutil', 
    'tempfile', 'ast', 'py_compile'
}

def deep_logic_audit(code_content, file_path):
    """فحص المنطق البرمجي، كشف الأكواد الوهمية، وتحليل البنية بعمق"""
    report = []
    
    # 1. فحص البناء النحوي
    try:
        py_compile.compile(file_path, doraise=True)
        syntax_status = "✅ سليمة نححياً (Syntax OK)."
    except Exception as e:
        syntax_status = f"❌ خطأ نحوي خطير:\n`{str(e)}`"

    # 2. كشف الأخطاء المنطقية الشائعة (Anti-Patterns & Fake Logic)
    fake_indicators = []
    if "scapy" in code_content.lower() and "send(" in code_content and "http" not in code_content.lower():
        fake_indicators.append("⚠️ **تحذير منطقي محتمل:** استخدام `scapy.send()` لإرسال بيانات ويب خام دون بناء بروتوكول HTTP حقيقي قد يكون غير فعال أو مجرد وهم.")
    if "requests.get" in code_content and "html" in code_content.lower() and "inject" in code_content.lower():
        fake_indicators.append("⚠️ **تحذير منطقي:** جلب صفحة بـ requests ثم محاولة حقنها لا يغير الخادم البعيد أبداً، بل يغير الذاكرة المحلية فقط.")

    # 3. استخراج المكاتب عبر AST
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

    pip_commands = [f"pip install {PIP_MAPPING.get(mod, mod)}" for mod in detected_modules]
    pip_text = " \n".join(pip_commands) if pip_commands else "لا توجد مكاتب خارجية."

    # الإحصائيات
    lines = code_content.splitlines()
    total_lines = len(lines)
    func_count = sum(1 for l in lines if l.strip().startswith('def '))

    audit_result = (
        "🔬 **التقرير الهشلي والتحليل المعماري للكود:**\n\n"
        f"• **الحالة النحوية:** {syntax_status}\n"
        f"• **إجمالي الأسطر والدوال:** `{total_lines}` أسطر | `{func_count}` دالة\n\n"
    )

    if fake_indicators:
        audit_result += "🚨 **كشف المنطق المزيف أو غير الواقعي:**\n"
        for ind in fake_indicators:
            audit_result += f"{ind}\n"
        audit_result += "\n"

    audit_result += (
        f"📦 **المكاتب الحقيقية المطلوبة:**\n```bash\n{pip_text}\n```\n\n"
        "💡 **الخلاصة:** تم فحص الكود محلياً لكشف أي تلاعب أو منطق وهمي لا يطابق قواعد العمل الحقيقية للشبكات والويب."
    )
    return audit_result

def search_github_advanced(code_content):
    """بحث ذكي في غيت هب عن مشاريع حقيقية مطابقة لنفس فكرة الكود"""
    keywords = "python"
    for line in code_content.splitlines():
        if "import " in line or "from " in line:
            parts = line.split()
            if len(parts) > 1 and parts[1] not in ['os', 'sys', 'time', 're', 'json', 'math', 'subprocess']:
                keywords = parts[1].split('.')[0]
                break

    url = f"https://api.github.com/search/repositories?q={keywords}+language:python&sort=stars&order=desc"
    headers = {"User-Agent": "Python-Code-Auditor"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            items = response.json().get('items', [])[:3]
            if not items:
                return "❌ لم يتم العثور على مشاريع مطابقة في GitHub."
            
            res_text = f"⭐ **أبرز المشاريع الحقيقية والموثوقة في GitHub حول (`{keywords}`):**\n\n"
            for item in items:
                res_text += f"🔹 **[{item['name']}]({item['html_url']})** (⭐ {item['stargazers_count']})\n"
                res_text += f"📝 {item['description'] or 'بدون وصف'}\n\n"
            return res_text
    except Exception:
        pass
    return "❌ تعذر الاتصال بـ GitHub حالياً."

# ==================== الأوامر والمعالجات ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        await update.message.reply_text("⛔ عذراً، هذا البوت خاص ولا يمكنك استخدامه.")
        return

    welcome_text = (
        "🛡 **أهلاً بك في المحلل المعماري المتقدم لأكواد Python!**\n\n"
        "📁 أرسل لي أي ملف بايثون وسأقوم بـ:\n"
        "1️⃣ **كشف الأكواد الوهمية أو المزيفة** (التي تدعي أشياء غير واقعية مثل الحقن الوهمي).\n"
        "2️⃣ **التدقيق المعماري والمنطقي** للتأكد أن الكود سيعمل فعلياً.\n"
        "3️⃣ **البحث المتقدم في GitHub** عن أفضل المشاريع الحقيقية والموثوقة ذات النجوم العالية."
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
        [InlineKeyboardButton("🔬 فحص المنطق وكشف الأكواد الوهمية", callback_data="deep_audit")],
        [InlineKeyboardButton("⭐ البحث المتقدم في GitHub عن المشاريع الأصلية", callback_data="github_search")],
        [InlineKeyboardButton("🛠 تنسيق وتنظيف الكود (Autopep8)", callback_data="format_code")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"📥 **تم استلام الملف بنجاح:** `{doc.file_name}`\nاختر نوع التدقيق المطلوب:",
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

    if query.data == "deep_audit":
        await query.edit_message_text("⏳ جاري تفكيك الكود والتحقق من منطقه البرمجي وكشف أي خدع...")
        report = deep_logic_audit(code_content, file_path)
        await query.message.reply_text(report, parse_mode="Markdown")

    elif query.data == "github_search":
        await query.edit_message_text("🔍 جاري البحث في مستودعات GitHub عن المشاريع الأصلية الموثوقة...")
        gh_results = search_github_advanced(code_content)
        await query.message.reply_text(gh_results, parse_mode="Markdown", disable_web_page_preview=True)

    elif query.data == "format_code":
        await query.edit_message_text("⏳ جاري إعادة تنسيق وترتيب الكود الحقيقي...")
        subprocess.run(["autopep8", "--in-place", "--aggressive", "--aggressive", file_path])
        
        with open(file_path, 'rb') as f:
            await query.message.reply_document(
                document=f,
                filename=f"clean_{file_name}",
                caption="✅ **تم تنسيق الكود وترتيبه بنجاح مع الحفاظ على هيكله الأساسي!**",
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

    print("⚡ بوت التدقيق المعماري المتقدم يعمل بنجاح...")
    app.run_polling()
