"""
数据库初始化脚本
创建所有表并插入默认数据
"""
import asyncio
from app.database import init_db, AsyncSessionLocal
from app.bootstrap import ensure_default_settings


async def create_default_settings():
    """创建默认系统设置"""
    async with AsyncSessionLocal() as session:
        await ensure_default_settings(session)
        print("默认设置检查完成")


async def main():
    """主函数"""
    print("开始初始化数据库...")

    # 创建所有表
    await init_db()
    print("数据库表创建完成")

    # 插入默认数据
    await create_default_settings()

    print("数据库初始化完成!")


if __name__ == "__main__":
    asyncio.run(main())
