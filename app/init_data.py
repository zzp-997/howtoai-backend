"""
初始化数据脚本
在数据库中创建测试用户
"""
import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal, engine, Base
from app.models.models import (
    User, MeetingRoom, Announcement,
    AttendanceConfig, CityConfig, HolidayConfig
)
from datetime import datetime
import bcrypt


async def init_data():
    """初始化数据"""
    async with AsyncSessionLocal() as db:
        # 检查是否已有用户
        result = await db.execute(select(User).limit(1))
        if result.scalar_one_or_none():
            print("数据已存在，跳过初始化")
            return

        print("开始初始化数据...")

        # 创建用户
        admin_password = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode()
        user_password = bcrypt.hashpw("123456".encode(), bcrypt.gensalt()).decode()

        users = [
            User(
                username="admin",
                password=admin_password,
                name="管理员",
                role="admin",
                department="技术部",
                position="系统管理员",
                annual_leave_balance=15,
                sick_leave_balance=10
            ),
            User(
                username="zhangsan",
                password=user_password,
                name="张三",
                role="user",
                department="研发部",
                position="工程师",
                annual_leave_balance=10,
                sick_leave_balance=5
            ),
            User(
                username="lisi",
                password=user_password,
                name="李四",
                role="user",
                department="产品部",
                position="产品经理",
                annual_leave_balance=8,
                sick_leave_balance=3
            )
        ]

        for user in users:
            db.add(user)

        # 创建会议室
        rooms = [
            MeetingRoom(
                name="会议室A",
                capacity=10,
                location="3楼301",
                equipment='["投影仪","白板","视频会议"]',
                description="小型会议室"
            ),
            MeetingRoom(
                name="会议室B",
                capacity=20,
                location="3楼302",
                equipment='["投影仪","白板","视频会议","音响"]',
                description="中型会议室"
            ),
            MeetingRoom(
                name="大会议室",
                capacity=50,
                location="4楼401",
                equipment='["投影仪","白板","视频会议","音响","麦克风"]',
                description="大型会议室，适合全员会议"
            )
        ]

        for room in rooms:
            db.add(room)

        # 创建公告
        announcements = [
            Announcement(
                title="公司春节放假通知",
                content="根据国家法定节假日安排，公司春节放假时间为2026年1月28日至2月3日，共7天。请各部门提前做好工作安排。",
                summary="春节放假安排",
                category="notice",
                category_label="通知",
                is_top=True,
                publish_time=datetime.now()
            ),
            Announcement(
                title="2026年度培训计划",
                content="为提升员工专业技能，公司将于2026年开展系列培训活动，包括技术培训、管理培训等，具体安排另行通知。",
                summary="年度培训计划",
                category="activity",
                category_label="活动",
                is_top=False,
                publish_time=datetime.now()
            )
        ]

        for ann in announcements:
            db.add(ann)

        # 创建考勤配置
        attendance_configs = [
            AttendanceConfig(key="workStartTime", value="09:00"),
            AttendanceConfig(key="workEndTime", value="18:00"),
            AttendanceConfig(key="lateThresholdMinutes", value="5"),
            AttendanceConfig(key="allowMakeUp", value="true"),
        ]
        for config in attendance_configs:
            db.add(config)

        # 创建城市配置
        cities = [
            CityConfig(name="北京", province="北京", transport_fee_base=800, accom_fee_base=400),
            CityConfig(name="上海", province="上海", transport_fee_base=1000, accom_fee_base=450),
            CityConfig(name="广州", province="广东", transport_fee_base=1200, accom_fee_base=350),
            CityConfig(name="深圳", province="广东", transport_fee_base=1200, accom_fee_base=380),
            CityConfig(name="杭州", province="浙江", transport_fee_base=800, accom_fee_base=350),
            CityConfig(name="南京", province="江苏", transport_fee_base=700, accom_fee_base=300),
            CityConfig(name="成都", province="四川", transport_fee_base=1500, accom_fee_base=280),
            CityConfig(name="武汉", province="湖北", transport_fee_base=600, accom_fee_base=250),
            CityConfig(name="西安", province="陕西", transport_fee_base=1000, accom_fee_base=280),
            CityConfig(name="重庆", province="重庆", transport_fee_base=1400, accom_fee_base=300),
        ]
        for city in cities:
            db.add(city)

        # 创建节假日配置（2026年）
        holidays = [
            # 元旦
            HolidayConfig(name="元旦", date="2026-01-01", type="holiday"),
            HolidayConfig(name="元旦", date="2026-01-02", type="holiday"),
            HolidayConfig(name="元旦", date="2026-01-03", type="holiday"),
            # 春节
            HolidayConfig(name="春节", date="2026-02-07", type="holiday"),
            HolidayConfig(name="春节", date="2026-02-08", type="holiday"),
            HolidayConfig(name="春节", date="2026-02-09", type="holiday"),
            HolidayConfig(name="春节", date="2026-02-10", type="holiday"),
            HolidayConfig(name="春节", date="2026-02-11", type="holiday"),
            HolidayConfig(name="春节", date="2026-02-12", type="holiday"),
            HolidayConfig(name="春节", date="2026-02-13", type="holiday"),
            # 清明节
            HolidayConfig(name="清明节", date="2026-04-04", type="holiday"),
            HolidayConfig(name="清明节", date="2026-04-05", type="holiday"),
            HolidayConfig(name="清明节", date="2026-04-06", type="holiday"),
            # 劳动节
            HolidayConfig(name="劳动节", date="2026-05-01", type="holiday"),
            HolidayConfig(name="劳动节", date="2026-05-02", type="holiday"),
            HolidayConfig(name="劳动节", date="2026-05-03", type="holiday"),
            HolidayConfig(name="劳动节", date="2026-05-04", type="holiday"),
            HolidayConfig(name="劳动节", date="2026-05-05", type="holiday"),
            # 端午节
            HolidayConfig(name="端午节", date="2026-05-31", type="holiday"),
            HolidayConfig(name="端午节", date="2026-06-01", type="holiday"),
            HolidayConfig(name="端午节", date="2026-06-02", type="holiday"),
            # 国庆节
            HolidayConfig(name="国庆节", date="2026-10-01", type="holiday"),
            HolidayConfig(name="国庆节", date="2026-10-02", type="holiday"),
            HolidayConfig(name="国庆节", date="2026-10-03", type="holiday"),
            HolidayConfig(name="国庆节", date="2026-10-04", type="holiday"),
            HolidayConfig(name="国庆节", date="2026-10-05", type="holiday"),
            HolidayConfig(name="国庆节", date="2026-10-06", type="holiday"),
            HolidayConfig(name="国庆节", date="2026-10-07", type="holiday"),
            HolidayConfig(name="国庆节", date="2026-10-08", type="holiday"),
        ]
        for holiday in holidays:
            db.add(holiday)

        await db.commit()
        print("数据初始化完成！")
        print("测试账户：")
        print("  admin / admin123 (管理员)")
        print("  zhangsan / 123456 (普通用户)")
        print("  lisi / 123456 (普通用户)")


async def create_tables():
    """创建表"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("数据表创建完成")


async def main():
    """主函数"""
    await create_tables()
    await init_data()


if __name__ == "__main__":
    asyncio.run(main())
