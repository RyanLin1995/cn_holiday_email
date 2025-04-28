import os
import argparse
import logging
import json
import shutil
from datetime import datetime
from data_fetcher import DataFetcher
from content_generator import ContentGenerator
from email_sender import EmailSender
from schedule_manager import ScheduleManager

def setup_logging():
    """设置日志配置。"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("cn_holiday_email.log"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("cn_holiday_email")

def load_config(config_path="config.json"):
    """从JSON文件加载配置。

    参数:
        config_path (str): 配置文件路径

    返回:
        dict: 配置数据
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"找不到配置文件：{config_path}")

    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_default_config(config_path="config.json"):
    """创建默认配置文件。

    参数:
        config_path (str): 保存配置文件的路径
    """
    default_config = {
        "email": {
            "smtp_server": "smtp.example.com",
            "smtp_port": 587,
            "username": "your_email@example.com",
            "password": "your_password",
            "sender_name": "公司文化部",
            "use_ssl": true
        },
        "recipients": [
            "all-employees@company.com",
            "staff@company.com"
        ],
        "openai": {
            "api_key": "",  # 从环境变量中读取
            "base_url": "",  # 可选，从环境变量中读取
            "model": "gpt-3.5-turbo"  # 可选，从环境变量中读取
        },
    }

    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(default_config, f, ensure_ascii=False, indent=2)

    print(f"默认配置文件已创建：{config_path}")
    print("请使用实际设置编辑配置文件。")
    print("\n注意：OpenAI API密钥应设置在环境变量'OPENAI_API_KEY'中")

def main():
    """运行节日邮件发送程序的主函数。"""
    parser = argparse.ArgumentParser(description="AI节日邮件发送程序")
    parser.add_argument("--config", default="config.json", help="配置文件路径")
    parser.add_argument("--create-config", action="store_true", help="创建默认配置文件")
    parser.add_argument("--force", action="store_true", help="强制发送邮件，即使今天不是特殊日期")
    parser.add_argument("--test", action="store_true", help="测试模式，不实际发送邮件")
    parser.add_argument("--use-sample", action="store_true", help="使用示例数据文件")
    parser.add_argument("--regenerate-schedule", action="store_true", help="强制重新生成月度邮件发送日程表")
    args = parser.parse_args()

    # 如果请求创建默认配置
    if args.create_config:
        create_default_config(args.config)
        return

    # 设置日志
    logger = setup_logging()
    logger.info("启动AI节日邮件发送程序")

    try:
        # 加载配置
        config = load_config(args.config)
        logger.info("配置加载成功")

        # 从配置和环境变量获取OpenAI设置
        # openai_api_key = os.environ.get("OPENAI_API_KEY") or config["openai"].get("api_key", "")
        # openai_base_url = os.environ.get("OPENAI_API_BASE") or config["openai"].get("base_url", "")
        # openai_model = os.environ.get("OPENAI_API_MODEL") or config["openai"].get("model", "")
        openai_api_key = config["openai"].get("api_key", "")
        openai_base_url = config["openai"].get("base_url", "")
        openai_model = config["openai"].get("model", "")

        # 初始化数据目录
        data_dir = "data"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        # 如果请求使用示例数据
        current_year = datetime.now().year
        if args.use_sample:
            # 检查示例文件是否存在
            sample_jieqi = f"jieqi_{current_year}.json"
            sample_holiday = f"holiday_{current_year}.json"

            if os.path.exists(sample_jieqi) and os.path.exists(sample_holiday):
                # 将示例文件复制到数据目录
                target_jieqi = os.path.join(data_dir, f"jieqi_{current_year}.json")
                target_holiday = os.path.join(data_dir, f"holiday_{current_year}.json")

                shutil.copy2(sample_jieqi, target_jieqi)
                shutil.copy2(sample_holiday, target_holiday)

                logger.info("使用示例数据文件")
            else:
                logger.warning("未找到示例文件，将使用API数据")

        # 初始化组件
        data_fetcher = DataFetcher(data_dir)
        content_generator = ContentGenerator(api_key=openai_api_key, base_url=openai_base_url, model=openai_model)
        schedule_manager = ScheduleManager(data_dir, data_fetcher)
        
        # 检查是否需要生成或更新月度日程表
        current_month = datetime.now().strftime("%Y-%m")
        monthly_schedule = None if args.regenerate_schedule else schedule_manager.load_monthly_schedule()
        
        if monthly_schedule is None:
            logger.info(f"生成{current_month}月度邮件发送日程表")
            monthly_schedule = schedule_manager.generate_monthly_schedule()
            schedule_manager.save_monthly_schedule(monthly_schedule)
            logger.info(f"月度日程表已保存，共{len(monthly_schedule)}个发送日期")
            
            # 输出本月的发送日程
            for send_date, events in monthly_schedule.items():
                for event in events:
                    original_date = event.get("original_date")
                    event_type = event.get("type")
                    event_name = event.get("info", {}).get("name")
                    logger.info(f"计划在 {send_date} 发送 {original_date} 的{event_type}: {event_name}")
        
        # 检查今天是否应该发送邮件
        should_send, special_date_type, special_date_info = schedule_manager.should_send_email_today()

        if should_send or args.force:
            # 如果强制发送但今天不是特殊日期，则查找最近的特殊日期
            if not special_date_type and args.force:
                logger.info("强制发送模式：查找最近的特殊日期")
                # 获取最近的特殊日期
                special_date_type, special_date_info = schedule_manager.get_nearest_special_date()
                if not special_date_type:
                    logger.error("无法找到最近的特殊日期，无法发送邮件")
                    return
                logger.info(f"找到最近的{special_date_type}：{special_date_info.get('name')}")

            
            # 获取原始日期和节日名称
            today = datetime.now().strftime("%Y-%m-%d")
            special_date_entry = monthly_schedule[today][0] if today in monthly_schedule else None
            original_date = special_date_entry.get("original_date") if special_date_entry else today
            event_name = special_date_info.get("name", "")
            
            if original_date == today:
                logger.info(f"今天是{special_date_type}：{event_name}")
            else:
                logger.info(f"今天将提前发送{original_date}的{special_date_type}：{event_name}的邮件")

            # 生成邮件内容
            email_content = content_generator.generate_email_content(special_date_type, special_date_info)
            logger.info(f"邮件内容已生成：{email_content['subject']}")

            if not args.test:
                # 初始化邮件发送器
                email_sender = EmailSender(
                    smtp_server=config["email"]["smtp_server"],
                    smtp_port=config["email"]["smtp_port"],
                    username=config["email"]["username"],
                    password=config["email"]["password"],
                    sender_name=config["email"]["sender_name"],
                    ssl=config["email"].get("use_ssl", True)
                )

                # 发送邮件
                success = email_sender.send_email(
                    recipients=config["recipients"],
                    subject=email_content["subject"],
                    body=email_content["body"]
                )

                if success:
                    logger.info("邮件发送成功")
                else:
                    logger.error("邮件发送失败")
            else:
                logger.info("测试模式：邮件未发送")
                logger.info(f"邮件主题：{email_content['subject']}")
                logger.info(f"邮件内容：{email_content['body']}")
        else:
            logger.info("今天不是特殊日期，不发送邮件。")

    except Exception as e:
        logger.exception(f"发生错误：{str(e)}")

if __name__ == "__main__":
    main()
