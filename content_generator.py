from openai import OpenAI

class ContentGenerator:
    def __init__(self, api_key=None, base_url=None, model=None):
        """初始化ContentGenerator，设置OpenAI参数。

        参数:
            api_key (str, 可选): OpenAI API密钥。默认从环境变量获取。
            base_url (str, 可选): OpenAI API基础URL。默认从环境变量获取。
            model (str, 可选): 要使用的OpenAI模型。默认从环境变量获取或使用'gpt-3.5-turbo'。
        """
        # 优先使用环境变量中的设置
        self.api_key = api_key
        self.base_url = base_url
        self.model = model

        # 创建OpenAI客户端
        client_args = {"api_key": self.api_key, "base_url": self.base_url}
        self.client = OpenAI(**client_args)

    def generate_email_content(self, special_date_type, special_date_info):
        """根据特殊日期生成邮件内容。

        参数:
            special_date_type (str): 特殊日期类型 ("节日" 或 "节气")
            special_date_info (dict): 关于特殊日期的信息

        返回:
            dict: 生成的邮件内容，包含主题和正文
        """
        if not self.client:
            raise ValueError("生成内容需要OpenAI API密钥")

        if special_date_type == "holiday":
            prompt = f"""
            请为中国传统节日"{special_date_info.get('name')}"生成一封祝福邮件。
            邮件应包含以下内容：
            1. 节日的简短介绍和历史背景
            2. 节日的传统习俗和庆祝方式
            3. 温馨的祝福语
            4. 适合这个节日的一句诗词或名言

            请提供邮件主题和正文。
            """
        elif special_date_type == "jieqi":
            prompt = f"""
            请为中国传统节气"{special_date_info.get('name')}"生成一封邮件。
            邮件应包含以下内容：
            1. 节气的简短介绍和意义
            2. 这个节气的气候特点和自然现象
            3. 与这个节气相关的传统习俗或饮食
            4. 适合这个节气的一句诗词或名言
            5. 温馨的祝福语

            请提供邮件主题和正文。
            """
        else:
            raise ValueError(f"不支持的特殊日期类型: {special_date_type}")

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是一位中国传统文化专家，擅长撰写有关中国传统节日和节气的内容。"},
                {"role": "user", "content": prompt}
            ]
        )

        content = response.choices[0].message.content

        # 解析响应以提取主题和正文
        lines = content.strip().split('\n')
        subject = ""
        body = ""

        for i, line in enumerate(lines):
            if "主题" in line or "标题" in line:
                subject = line.split("：", 1)[1].strip() if "：" in line else line.strip()
                body = "\n".join(lines[i+1:]).strip()
                break

        if not subject:
            # 如果无法解析主题，则使用第一行作为主题
            subject = lines[0].strip()
            body = "\n".join(lines[1:]).strip()

        return {
            "subject": subject,
            "body": body
        }


