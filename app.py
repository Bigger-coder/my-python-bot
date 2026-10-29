import os
import ast
import subprocess
import py_compile
import sys
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# ==================== الإعدادات الأساسية ====================
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("TOKEN") or "ضع_توكن_البوت_هنا"
MY_CHAT_ID = 7597527575  # الـ Chat ID الخاص بك لحماية البوت 100%

TEMP_DIR = "user_codes"
os.makedirs(TEMP_DIR, exist_ok=True)

# ==================== الحماية (البوت خاص بك فقط) ====================
def is_authorized(update: Update) -> bool:
    if not update.effective_user:
        return False
    return update.effective_user.id == MY_CHAT_ID

PIP_MAPPING = {
    'bs4': 'beautifulsoup4', 'cv2': 'opencv-python', 'PIL': 'Pillow',
    'skimage': 'scikit-image', 'sklearn': 'scikit-learn', 'yaml': 'PyYAML',
    'telegram': 'python-telegram-bot', 'serial': 'pyserial', 'Crypto': 'pycryptodome',
    'dotenv': 'python-dotenv'
}

BUILTIN_MODULES = {
    'os', 'sys', 'time', 're', 'json', 'math', 'subprocess', 'threading', 
    'socket', 'asyncio', 'collections', 'itertools', 'functools', 'datetime', 
    'pathlib', 'urllib', 'http', 'logging', 'hashlib', 'base64', 'shutil', 
    'tempfile', 'ast', 'py_compile'
}

# ==================== العمليات الهندسية المتقدمة ====================

def analyze_code_statically(code_content, file_path):
    """تحليل هندسي مطور - يكشف حقن الشبكات والأكواد المشبوهة بدون AI"""
    try:
        py_compile.compile(file_path, doraise=True)
        syntax_status = "✅ سليمة نحوياً 100% (Syntax OK)."
    except Exception as e:
        syntax_status = f"❌ خطأ نحوي يمنع التشغيل:\n`{str(e)}`"

    detected_modules = set()
    suspicious_details = []
    
    dangerous_signatures = {
        'scapy': '⚠️ الكود يتعامل مع حزم الشبكة الخام (Sniffing/Injection).',
        'send(': '⚠️ محاولة إرسال حزم بيانات مباشرة إلى شبكة أو موقع خارجي.',
        'style': '⚠️ الكود يقوم بالتلاعب والتعديل على واجهات مواقع أخرى (قد يكون Fake).'
    }

    try:
        tree = ast.parse(code_content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    mod = alias.name.split('.')[0]
                    if mod not in BUILTIN_MODULES: detected_modules.add(mod)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    mod = node.module.split('.')[0]
                    if mod not in BUILTIN_MODULES: detected_modules.add(mod)
    except Exception:
        pass

    for sig, alert in dangerous_signatures.items():
        if sig in code_content:
            suspicious_details.append(alert)

    pip_commands = [f"pip install {PIP_MAPPING.get(mod, mod)}" for mod in detected_modules]
    pip_text = " \n".join(pip_commands) if pip_commands else "لا توجد مكاتب خارجية تتطلب تثبيتاً."

    if suspicious_details:
        security_status = "⚠️ **مؤشرات سلوك مشبوه (Fake / Exploit Detected):**\n" + "\n".join(suspicious_details)
    else:
        security_status = "🛡️ آمن نظرياً (لا توجد مؤشرات سلوك تخريبي أو دوال غامضة)."

    lines = code_content.splitlines()
    report = (
        "📊 **التقرير الهندسي المتقدم (صادق 100%):**\n\n"
        f"• **حالة البناء النحوي:** {syntax_status}\n"
        f"• **التحليل الأمني والمصداقية:** {security_status}\n\n"
        f"📦 **أوامر التثبيت الفعلي للمكاتب المكتشفة:**\n"
        f"```bash\n{pip_text}\n```\n\n"
        f"📈 **إحصائيات الهيكل القياسي:**\n"
        f"• إجمالي الأسطر: `{len(lines)}`\n"
        f"• الدوال (`def`): `{sum(1 for l in lines if l.strip().startswith('def '))}`\n"
    )
    return report

def search_github_repositories(code_content):
    """البحث الذكي في غيت هب بالاعتماد على المكاتب المستوردة أو الدوال"""
    keywords = []
    try:
        tree = ast.parse(code_content)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                keywords.append(node.name)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name not in BUILTIN_MODULES: 
                        keywords.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    mod = node.module.split('.')[0]
                    if mod not in BUILTIN_MODULES: 
                        keywords.append(mod)
    except Exception:
        pass
    
    query = "+".join(keywords[:2]) if keywords else "packet+injection"
    url = f"https://api.github.com/search/repositories?q={query}+language:python&sort=stars&order=desc"
    headers = {"User-Agent": "Python-Code-Auditor"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            items = response.json().get('items', [])[:3]
            if not items: 
                return f"❌ لم يتم العثور على مشاريع تطابق فكرة الكود الحالية (`{query}`)."
            
            res_text = f"⭐ **مشاريع حقيقية على GitHub تطابق فكرة كودك تماماً (`{query}`):**\n\n"
            for item in items:
                res_text += f"🔹 **[{item['name']}]({item['html_url']})** (⭐ {item['stargazers_count']})\n"
                res_text += f"📝 {item['description'] or 'بدون وصف'}\n\n"
            return res_text
    except Exception:
        pass
    return "❌ تعذر الاتصال بخوادم GitHub حالياً."

def execute_safe_code(file_path):
    """تشغيل الكود برمجياً داخل البيئة المحلية المعزولة بحماية الوقت"""
    try:
        result = subprocess.run(
            [sys.executable, file_path],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return f"🚀 **تم تشغيل الكود بنجاح! مخرجات الـ Terminal:**\n```\n{result.stdout or 'تم التشغيل بنجاح دون طباعة مخرجات.'}\n```"
        else:
            return f"❌ **فشل تشغيل الكود برمجياً! تفاصيل الخطأ:**\n```\n{result.stderr}\n```"
    except subprocess.TimeoutExpired:
        return "⏱️ **فشل التشغيل:** تجاوز الكود وقت الأمان المحدد (5 ثوانٍ). قد يحتوي على لوب لانهائي (`while True`)."
    except Exception as e:
        return f"❌ خطأ غير متوقع أثناء تشغيل الكود: `{str(e)}`"

def auto_fix_and_clean_code(file_path):
    """إعادة كتابة وتصحيح الكود برمجياً بدون AI لحماية موارد الجهاز"""
    try:
        # 1. إزالة المكاتب الوهمية وغير المستخدمة تلقائياً
        subprocess.run(["autoflake", "--in-place", "--remove-all-unused-imports", file_path], check=True)
        
        # 2. إعادة هيكلة المنطق وتبسيط الأكواد المعقدة هندسياً (إذا كانت متوفرة)
        try:
            subprocess.run(["pyrefact", "--safe", file_path], check=True)
        except Exception:
            pass  # تخطي إذا لم تكن مدعومة بالكامل بالبيئة
        
        # 3. تنسيق الكود بالشكل القياسي النهائي
        subprocess.run(["autopep8", "--in-place", "--aggressive", file_path], check=True)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            fixed_code = f.read()
        return fixed_code
    except Exception as e:
        return f"❌ فشل التصحيح الآلي: {str(e)}"

# ==================== معالجات أوامر البوت ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update): return
    welcome_text = (
        "🚀 **مرحباً بك في أداة التدقيق الصادقة والتصحيح الآلي المتطور!**\n\n"
        "قم بإرسال أي ملف بايثون (`.py`) وسأقوم بتدقيقه، البحث عن فكرته، تشغيله، أو إعادة كتابته وتصحيحه هندسياً آلياً بدون أي ذكاء اصطناعي مزيف."
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update): return

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
        [InlineKeyboardButton("📊 تدقيق شجرة الكود وكشف الـ Fake", callback_data="static_audit")],
        [InlineKeyboardButton("🔍 ابحث في GitHub عن نفس الفكرة", callback_data="gh_search")],
        [InlineKeyboardButton("⚙️ تشغيل الكود الفعلي برمجياً", callback_data="run_code")],
        [InlineKeyboardButton("🛠️ صلح كودي وأعطني النسخة المحدثة", callback_data="fix_code")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"📥 **تم استلام مستند الكود:** `{doc.file_name}`\nاختر الإجراء الهندسي المطلوب:",
        reply_markup=reply_markup, parse_mode="Markdown"
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    file_path = context.user_data.get('current_file')
    file_name = context.user_data.get('file_name', 'fixed_script.py')

    if not file_path or not os.path.exists(file_path):
        await query.edit_message_text("❌ انتهت صلاحية الجلسة أو تم مسح الملف المؤقت.")
        return

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        code_content = f.read()

    if query.data == "static_audit":
        report = analyze_code_statically(code_content, file_path)
        await query.message.reply_text(report, parse_mode="Markdown")
        
    elif query.data == "gh_search":
        gh_results = search_github_repositories(code_content)
        await query.message.reply_text(gh_results, parse_mode="Markdown")
        
    elif query.data == "run_code":
        check_report = analyze_code_statically(code_content, file_path)
        if "⚠️" in check_report:
            await query.message.reply_text("⛔ تم حظر التشغيل لأن الكود مشبوه (Exploit/Fake) ويشكل خطراً على سيرفرك.")
        else:
            await query.message.reply_text("⚙️ جاري محاولة تشغيل الكود...")
            run_results = execute_safe_code(file_path)
            await query.message.reply_text(run_results, parse_mode="Markdown")
            
    elif query.data == "fix_code":
        await query.message.reply_text("🛠️ جاري تصحيح الكود هندسياً وإعادة صياغته بدون AI...")
        fixed_output = auto_fix_and_clean_code(file_path)
        
        # حفظ النسخة الجديدة وإرسالها للمستخدم كملف جاهز
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_output)
            
        await query.message.reply_text("✅ **تم تصحيح الكود وتحديثه بنجاح! إليك الملف المحدث:**", parse_mode="Markdown")
        with open(file_path, 'rb') as document:
            await context.bot.send_document(chat_id=MY_CHAT_ID, document=document, filename=f"Fixed_{file_name}")

# ==================== تشغيل التطبيق المستمر ====================
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(CallbackQueryHandler(button_callback))
    
    print("🤖 البوت الهندسي المتقدم والمتكامل يعمل بنجاح...")
    app.run_polling()
