"""
应用启动时需要补齐的默认数据
"""
import logging

import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import Setting

logger = logging.getLogger(__name__)


async def ensure_default_settings(session: AsyncSession) -> None:
    """在首次启动时补齐默认系统设置，避免 Render 等平台遗漏 init_db.py。"""
    result = await session.execute(select(Setting))
    existing_settings = {item.key for item in result.scalars().all()}

    password_hash = None
    if "admin_password_hash" not in existing_settings:
        password_hash = bcrypt.hashpw(
            settings.admin_password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

    default_settings = [
        ("initialized", "true", "数据库初始化标记"),
        ("proxy", settings.proxy, "代理地址 (支持 http:// 和 socks5://)"),
        ("proxy_enabled", str(settings.proxy_enabled).lower(), "是否启用代理"),
        ("log_level", settings.log_level, "日志级别"),
        ("default_team_max_members", "6", "新导入 Team 的默认总席位"),
        ("warranty_expiration_mode", "first_use", "质保时长计算模式: first_use/refresh_on_redeem"),
        ("token_refresh_interval_minutes", "30", "Token 预刷新执行间隔(分钟)"),
        ("token_refresh_window_hours", "2", "Token 预刷新窗口(小时)"),
        ("periodic_team_sync_enabled", "true", "是否启用 Team 周期状态同步"),
        ("periodic_team_sync_interval_hours", "12", "Team 周期状态同步检查间隔(小时)"),
        ("periodic_team_sync_days", "7", "Team 状态同步周期(天)"),
        ("welfare_common_code_used_count", "0", "福利通用兑换码已使用次数"),
        ("ui_theme", "ocean", "后台界面主题"),
    ]

    if password_hash is not None:
        default_settings.insert(
            1,
            ("admin_password_hash", password_hash, "管理员密码哈希")
        )

    pending = [
        Setting(key=key, value=value, description=description)
        for key, value, description in default_settings
        if key not in existing_settings
    ]

    if not pending:
        return

    session.add_all(pending)
    await session.commit()
    logger.info("已补齐 %s 项默认系统设置", len(pending))
