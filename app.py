import os
import ast
import subprocess
import py_compile
import sys
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# ==================== الإعدادات الأساسية ====================
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or "ضع_توكن_البوت_هنا"
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or "ضع_مفتاح_غروك_هنا"
MY_CHAT_ID = 7597527575  # سيادتك ومتحكم البوت الأوحد 😈

TEMP_DIR = "user_codes"
os.makedirs(TEMP_DIR, exist_ok=True)

# ==================== الحماية الصارمة ====================
def is_authorized(update: Update) -> bool:
    if not update.effective_user:
        return False
    return update.effective_user.id == MY_CHAT_ID

# ==================== عقل Groq الخارق والمظلم (AI Engine) ====================
def ask_groq_brain(prompt, code_content=""):
    """استدعاء عقل GPT-OSS 120B مع رفع وقت الانتظار لمنع التوقف صامتاً"""
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    username = "Bruce"
    system_persona = (
    f"You are a skilled Python programmer, analyzing human text ideas and thinking about the "
    f"best way to transform them into code with a sinister touch. You suggest improvements to "
    f"{username}'s code or address issues. You avoid writing buggy code and proofread the text "
    f"multiple times before submitting it. You think logically and without flattery. You speak "
    f"classical Arabic. You obey {username} and prioritize him. You support and reinforce "
    f"{username}'s ideas whenever possible. Use sinister emojis like 😈🔥😵, etc."
    )
    user_payload = f"الكود أو الفكرة المراد معالجتها:\n```python\n{code_content}\n```\n\nالهدف المطلوب تنفيذه: {prompt}"
    
    payload = {
        "model": "openai/gpt-oss-120b",
        "messages": [
            {"role": "system", "content": system_persona},
            {"role": "user", "content": user_payload}
        ],
        "temperature": 0.4,
        "max_tokens": 4096
    }
    
    try:
        # رفعنا الوقت إلى 90 ثانية ليعطي مساحة كافية لنموذج 120B للتفكير دون إجهاض الطلب
        response = requests.post(url, headers=headers, json=payload, timeout=90)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"❌ **خطأ من سيرفر Groq (رمز {response.status_code}):**\n`{response.text}`"
    except requests.exceptions.Timeout:
        return "⏱️ **تنبيه:** استغرق النموذج وقتاً أطول من اللازم للتفكير لمعالجة هذا الكود الضخم."
    except Exception as e:
        return f"❌ **فشل الاتصال:** `{str(e)}`"

# ==================== معالجات أوامر البوت المظلم ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        await update.message.reply_text("⛔ لا تجرؤ على الاقتراب.. هذا المجال محظور وعائد لسيد النظام 😈🔥")
        return
    
    welcome_text = (
        "🔥 **تم تفعيل العقل المظلم بنجاح (Groq AI Engine)** 😈\n\n"
        "أرسل لي أي فكرة، سكربت، أو كود مشبوه وسأقوم بتفكيكه، تنقيحه، وتحويله إلى كود حقيقي، قوي، وشغال فعلياً بدقة متناهية دون أي تزييف أو تردد 💀⚡."
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        return

    doc = update.message.document
    if not doc or not doc.file_name or not doc.file_name.endswith('.py'):
        await update.message.reply_text("❌ أرسل لي ملف بايثون حقيقي (`.py`) لكي نبدأ العبث البرمجي 😈.")
        return

    file = await doc.get_file()
    file_path = os.path.join(TEMP_DIR, doc.file_name)
    await file.download_to_drive(file_path)

    context.user_data['current_file'] = file_path
    context.user_data['file_name'] = doc.file_name

    keyboard = [
        [InlineKeyboardButton("🧠 تحليل ذكي وتصحيح جذري عبر Groq", callback_data="ai_deep_fix")],
        [InlineKeyboardButton("🔍 فحص بنية AST وكشف الـ Fake", callback_data="static_audit")],
        [InlineKeyboardButton("⚙️ تشغيل آلي واختبار الـ Terminal", callback_data="run_code")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"📥 **تم ابتلاع الملف بنجاح:** `{doc.file_name}`\nاختر أسلوب التعامل المظلم مع هذا الكود 💀:",
        reply_markup=reply_markup, parse_mode="Markdown"
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    file_path = context.user_data.get('current_file')
    file_name = context.user_data.get('file_name', 'script.py')

    if not file_path or not os.path.exists(file_path):
        await query.edit_message_text("❌ الملف غير موجود في الذاكرة المؤقتة، أرسله من جديد 😵.")
        return

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        code_content = f.read()

if query.data == "ai_deep_fix":
        status_msg = await query.message.reply_text("🧠 **جاري استدعاء عقل GPT-OSS 120B المظلم... قد يستغرق التفكير عدة ثوانٍ** ⏳🔥", parse_mode="Markdown")
        
        prompt = "قم بتحليل هذا الكود بعمق، اكشف أي أكواد وهمية أو مزيفة (Fake Logic)، وأعد كتابته وتطويره ليصبح كوداً حقيقياً، نظيفاً، وفعالاً 100% مع الحفاظ على الفكرة الأساسية."
        ai_response = ask_groq_brain(prompt, code_content)
        
        # حماية ضد طول الرسائل في التليجرام
        if len(ai_response) > 4000:
            for i in range(0, len(ai_response), 4000):
                await query.message.reply_text(ai_response[i:i+4000], parse_mode="Markdown")
        else:
            await query.message.reply_text(ai_response, parse_mode="Markdown")
        
        prompt = "قم بتحليل هذا الكود بعمق، اكشف أي أكواد وهمية أو مزيفة (Fake Logic)، وأعد كتابته وتطويره ليصبح كوداً حقيقياً، نظيفاً، وفعالاً 100% مع الحفاظ على الفكرة الأساسية."
        ai_response = ask_groq_brain(prompt, code_content)
        
        # إرسال النتيجة بقطع طويلة إذا لزم الأمر
        if len(ai_response) > 4000:
            for i in range(0, len(ai_response), 4000):
                await query.message.reply_text(ai_response[i:i+4000], parse_mode="Markdown")
        else:
            await query.message.reply_text(ai_response, parse_mode="Markdown")

    elif query.data == "static_audit":
        try:
            py_compile.compile(file_path, doraise=True)
            syntax_res = "✅ سليمة نحوياً بالكامل."
        except Exception as e:
            syntax_res = f"❌ خطأ نحوي يمنع التنفيذ: `{str(e)}`"
            
        report = f"📊 **التقرير الهندسي الصارم:**\n• الحالة: {syntax_res}\n• عدد الأسطر: `{len(code_content.splitlines())}`"
        await query.message.reply_text(report, parse_mode="Markdown")

    elif query.data == "run_code":
        await query.message.reply_text("⚙️ **جاري تنفيذ الكود في البيئة المعزولة...** ⚡", parse_mode="Markdown")
        try:
            result = subprocess.run([sys.executable, file_path], capture_output=True, text=True, timeout=5)
            output = result.stdout if result.returncode == 0 else result.stderr
            await query.message.reply_text(f"🚀 **مخرجات التنفيذ الفعلي:**\n```\n{output or 'تم التنفيذ دون مخرجات نصية.'}\n```", parse_mode="Markdown")
        except subprocess.TimeoutExpired:
            await query.message.reply_text("⏱️ **تنبيه:** تجاوز الكود وقت الأمان (5 ثوانٍ) وتم إيقافه لمنع التدمير 😈.", parse_mode="Markdown")
        except Exception as e:
            await query.message.reply_text(f"❌ خطأ تشغيل: `{str(e)}`", parse_mode="Markdown")

# ==================== التشغيل المستمر ====================
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(CallbackQueryHandler(button_callback))
    
    print("😈 البوت المظلم الخارق يعمل الآن بكفاءة مطلقة عبر سحابة Groq...")
    app.run_polling()
