"""
应用配置模块
使用 Pydantic Settings 管理配置
"""
from urllib.parse import urlsplit, urlunsplit

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """应用配置"""

    # 应用配置
    app_name: str = "GPT Team 管理系统"
    app_version: str = "0.1.0"
    app_host: str = "0.0.0.0"
    app_port: int = Field(8008, validation_alias=AliasChoices("APP_PORT", "PORT"))
    debug: bool = True

    # 数据库配置
    # 建议在 Docker 中使用 data 目录挂载，以避免文件挂载权限或类型问题
    database_url: str = f"sqlite+aiosqlite:///{BASE_DIR}/data/team_manage.db"

    # 安全配置
    secret_key: str = "your-secret-key-here-change-in-production"
    admin_password: str = "admin123"

    # 日志配置
    log_level: str = "INFO"
    database_echo: bool = False

    # 代理配置
    proxy: str = ""
    proxy_enabled: bool = False

    # JWT 配置
    jwt_verify_signature: bool = False

    # 时区配置
    timezone: str = "Asia/Shanghai"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


# 创建全局配置实例
settings = Settings()


def normalize_database_url(database_url: str) -> str:
    """规范化数据库连接串，兼容 Render/Neon 常见写法。"""
    raw_url = str(database_url or "").strip()
    if not raw_url:
        return raw_url

    if raw_url.startswith("postgresql+asyncpg://") or raw_url.startswith("sqlite+aiosqlite://"):
        return raw_url

    if raw_url.startswith("postgresql://"):
        return raw_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    if raw_url.startswith("postgres://"):
        return raw_url.replace("postgres://", "postgresql+asyncpg://", 1)

    return raw_url


def is_sqlite_url(database_url: str) -> bool:
    normalized = normalize_database_url(database_url)
    return normalized.startswith("sqlite")


def get_sqlite_file_path(database_url: str) -> Path | None:
    """获取 SQLite 数据库文件路径；内存库返回 None。"""
    normalized = normalize_database_url(database_url)
    if not is_sqlite_url(normalized):
        return None

    parsed = urlsplit(normalized)
    db_path = parsed.path or ""

    if db_path in {"/:memory:", ":memory:"}:
        return None

    if normalized.startswith("sqlite+aiosqlite:///./"):
        return (BASE_DIR / db_path.removeprefix("/./")).resolve()

    if normalized.startswith("sqlite+aiosqlite:///") and not normalized.startswith("sqlite+aiosqlite:////"):
        return (BASE_DIR / db_path.lstrip("/")).resolve()

    return Path(urlunsplit(("", "", db_path, "", ""))).resolve()
