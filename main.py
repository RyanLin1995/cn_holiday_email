import os
import argparse
import logging
import json
import shutil
from datetime import datetime
from data_fetcher import DataFetcher
from date_checker import DateChecker
from content_generator import ContentGenerator
from email_sender import EmailSender

def setup_logging():
    """Setup logging configuration."""
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
    """Load configuration from a JSON file.

    Args:
        config_path (str): Path to the configuration file

    Returns:
        dict: Configuration data
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_default_config(config_path="config.json"):
    """Create a default configuration file.

    Args:
        config_path (str): Path to save the configuration file
    """
    default_config = {
        "email": {
            "smtp_server": "smtp.example.com",
            "smtp_port": 587,
            "username": "your_email@example.com",
            "password": "your_password",
            "sender_name": "公司文化部"
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
        "check_days_ahead": 1
    }

    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(default_config, f, ensure_ascii=False, indent=2)

    print(f"Default configuration created at {config_path}")
    print("Please edit the configuration file with your actual settings.")
    print("\nNote: OpenAI API key should be set in environment variable 'OPENAI_API_KEY'")

def main():
    """Main function to run the holiday email sender."""
    parser = argparse.ArgumentParser(description="AI节日邮件发送程序")
    parser.add_argument("--config", default="config.json", help="配置文件路径")
    parser.add_argument("--create-config", action="store_true", help="创建默认配置文件")
    parser.add_argument("--force", action="store_true", help="强制发送邮件，即使今天不是特殊日期")
    parser.add_argument("--test", action="store_true", help="测试模式，不实际发送邮件")
    parser.add_argument("--use-sample", action="store_true", help="使用示例数据文件")
    args = parser.parse_args()

    # Create default configuration if requested
    if args.create_config:
        create_default_config(args.config)
        return

    # Setup logging
    logger = setup_logging()
    logger.info("Starting AI节日邮件发送程序")

    try:
        # Load configuration
        config = load_config(args.config)
        logger.info("Configuration loaded successfully")

        # Get OpenAI settings from config and environment variables
        # openai_api_key = os.environ.get("OPENAI_API_KEY") or config["openai"].get("api_key", "")
        # openai_base_url = os.environ.get("OPENAI_API_BASE") or config["openai"].get("base_url", "")
        # openai_model = os.environ.get("OPENAI_API_MODEL") or config["openai"].get("model", "")

        openai_api_key = config["openai"].get("api_key", "")
        openai_base_url = config["openai"].get("base_url", "")
        openai_model = config["openai"].get("model", "")

        # Initialize data directory
        data_dir = "data"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        # Use sample data if requested
        current_year = datetime.now().year
        if args.use_sample:
            # Check if sample files exist
            sample_jieqi = "jieqi_2025.json"
            sample_holiday = "holiday_2025.json"

            if os.path.exists(sample_jieqi) and os.path.exists(sample_holiday):
                # Copy sample files to data directory with current year
                target_jieqi = os.path.join(data_dir, f"jieqi_{current_year}.json")
                target_holiday = os.path.join(data_dir, f"holiday_{current_year}.json")

                shutil.copy2(sample_jieqi, target_jieqi)
                shutil.copy2(sample_holiday, target_holiday)

                logger.info("Using sample data files")
            else:
                logger.warning("Sample files not found, using API data instead")

        # Initialize components
        data_fetcher = DataFetcher(data_dir)
        date_checker = DateChecker(data_fetcher)
        content_generator = ContentGenerator(api_key=openai_api_key, base_url=openai_base_url, model=openai_model)

        # 检查今天是否应该发送邮件（今天是特殊日期或是非工作日特殊日期前的最后一个工作日）
        should_send, special_date_type, special_date_info = date_checker.get_next_workday_for_special_date(
            days_ahead=config.get("check_days_ahead", 7)
        )

        if should_send or args.force:
            if not special_date_type and args.force:
                # 如果强制发送且今天不是特殊日期，使用下一个即将到来的特殊日期
                upcoming = date_checker.get_upcoming_special_dates(days=config.get("check_days_ahead", 7))
                if upcoming:
                    _, special_date_type, special_date_info = upcoming[0]
                    logger.info(f"Forced mode: Using upcoming {special_date_type}: {special_date_info.get('name')}")
                else:
                    logger.error("没有找到即将到来的特殊日期")
                    return
            else:
                if special_date_type == "holiday" or special_date_type == "jieqi":
                    date_str = special_date_info.get('date')
                    special_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else datetime.now().date()
                    today = datetime.now().date()

                    if special_date == today:
                        logger.info(f"今天是 {special_date_type}: {special_date_info.get('name')}")
                    else:
                        logger.info(f"今天是 {special_date_info.get('date')} {special_date_type}: {special_date_info.get('name')} 前的最后一个工作日")

            # Generate email content
            email_content = content_generator.generate_email_content(special_date_type, special_date_info)
            logger.info(f"Email content generated: {email_content['subject']}")

            if not args.test:
                # Initialize email sender
                email_sender = EmailSender(
                    smtp_server=config["email"]["smtp_server"],
                    smtp_port=config["email"]["smtp_port"],
                    username=config["email"]["username"],
                    password=config["email"]["password"],
                    sender_name=config["email"]["sender_name"]
                )

                # Send email
                success = email_sender.send_email(
                    recipients=config["recipients"],
                    subject=email_content["subject"],
                    body=email_content["body"],
                    poster_path=None  # 不再使用海报
                )

                if success:
                    logger.info("Email sent successfully")
                else:
                    logger.error("Failed to send email")
            else:
                logger.info("Test mode: Email not sent")
                logger.info(f"Subject: {email_content['subject']}")
                logger.info(f"Body: {email_content['body']}")
        else:
            logger.info("Today is not a special date. No email sent.")

            # Check upcoming special dates
            upcoming = date_checker.get_upcoming_special_dates(days=config.get("check_days_ahead", 7))
            if upcoming:
                logger.info("Upcoming special dates:")
                for date_str, type_str, info in upcoming:
                    logger.info(f"  {date_str}: {type_str} - {info.get('name')}")

    except Exception as e:
        logger.exception(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
