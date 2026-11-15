import os
from dataclasses import dataclass
from enum import Enum
from dotenv import load_dotenv

load_dotenv()


class Mode(str, Enum):
    CODER = "coder"
    NEWS = "news"
    CHAT = "chat"
    AGENT = "agent"


MODE_LABELS = {
    Mode.CODER: "👨‍💻 المبرمج والبحث",
    Mode.NEWS: "📰 الأخبار الحية",
    Mode.CHAT: "💬 دردشة ذكية",
    Mode.AGENT: "🚀 الوضع الشامل",
}

MODE_INFO = {
    Mode.CODER: "👨‍💻 <b>وضع المبرمج</b>\nاكتب طلبك البرمجي، أو ابحث في GitHub وReddit ويوتيوب.",
    Mode.NEWS: "📰 <b>الأخبار الحية</b>\nسأرسل لك آخر أخبار العراق والعالم تلقائياً.",
    Mode.CHAT: "💬 <b>الدردشة الذكية</b>\nتحدث معي بشكل طبيعي وسأتذكر سياق حديثنا.",
    Mode.AGENT: "🚀 <b>الوضع الشامل</b>\nدردشة + برمجة + أخبار + بحث حي في الإنترنت.",
}


@dataclass(frozen=True)
class Settings:
    bot_token: str
    owner_id: int
    groq_api_key: str
    groq_model: str
    github_token: str
    db_path: str
    news_interval_sec: int


def load_settings() -> Settings:
    token = os.getenv("BOT_TOKEN")
    owner = os.getenv("OWNER_ID")
    if not token or not owner:
        raise RuntimeError("BOT_TOKEN و OWNER_ID مطلوبان في .env")
    return Settings(
        bot_token=token,
        owner_id=int(owner),
        groq_api_key=os.getenv("GROQ_API_KEY", ""),
        groq_model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
        github_token=os.getenv("GITHUB_TOKEN", ""),
        db_path=os.getenv("DB_PATH", "data/bot.db"),
        news_interval_sec=int(os.getenv("NEWS_INTERVAL_SEC", "600")),
    )


settings = load_settings()
