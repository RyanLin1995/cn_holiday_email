import os
import argparse
import logging
import json
from content_generator import ContentGenerator
from data_fetcher import date_fetch_main
from email_sender import EmailSender
from schedule_manager import should_send_email_today


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
            "use_ssl": True
        },
        "recipients": [
            "all-employees@company.com",
            "staff@company.com"
        ],
        "openai": {
            "api_key": "",  # 可选，或从环境变量中读取
            "base_url": "",  # 可选，从环境变量中读取
            "email_model": "gpt-3.5-turbo",  # 可选，从环境变量中读取
            "date_model": "Qwen/Qwen3-Coder-30B-A3B-Instruct"  # 可选，从环境变量中读取
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
        api_key = os.environ.get("OPENAI_API_KEY") or config["openai"].get("api_key", "")
        base_url = os.environ.get("OPENAI_API_BASE") or config["openai"].get("base_url", "")
        email_model = os.environ.get("OPENAI_API_MODEL") or config["openai"].get("email_model", "")
        date_model = os.environ.get("OPENAI_API_MODEL") or config["openai"].get("date_model", "")

        if not all([api_key, base_url, email_model, date_model]):
            logger.error("缺少必要设置，请检查配置文件或环境变量。")
            return

        # 请求节假日数据
        date_fetch_main(base_url=base_url, api_key=api_key,
                        model=date_model)

        # 初始化组件
        content_generator = ContentGenerator(api_key=api_key, base_url=base_url, model=email_model)
        
        # 检查今天是否应该发送邮件
        if os.path.exists('date.json'):
            with open('date.json') as f:
                email_schedule = json.load(f)
                if email_schedule[0]:
                    date_info = email_schedule[0]
                else:
                    logger.info("7天内没有找到节日，无需发送...")
                    return
        else:
            logger.info("没有找到邮件发送日程表，无需发送...")
            return

        should_send = should_send_email_today(date_info)

        if should_send or args.force:
            # 如果强制发送但今天不是特殊日期，则查找最近的特殊日期
            if args.force:
                logger.info("强制发送模式：查找最近的特殊日期")

            logger.info(f"今天将提前发送{date_info['holiday_name']}的邮件")

            # 生成邮件内容
            email_content = content_generator.generate_email_content(date_info['holiday_name'])
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
