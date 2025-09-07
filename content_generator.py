from agno.agent import Agent
from agno.models.openai import OpenAILike

class ContentGenerator:
    def __init__(self, api_key=None, base_url=None, model=None):
        """初始化ContentGenerator，设置OpenAI参数。

        参数:
            api_key (str, 可选): OpenAI API密钥。默认从环境变量获取。
            base_url (str, 可选): OpenAI API基础URL。默认从环境变量获取。
            model (str, 可选): 要使用的OpenAI模型。默认从环境变量获取或使用'gpt-3.5-turbo'。
        """
        # 优先使用环境变量中的设置
        model = OpenAILike(base_url=base_url, api_key=api_key, id=model)
        self.client = Agent(name="Master Email Writer", model=model)

    def generate_email_content(self, holiday_name):
        """根据特殊日期生成邮件内容。

        参数:
            holiday_name (str): 节气名称

        返回:
            dict: 生成的邮件内容，包含主题和正文
        """
        if not self.client:
            raise ValueError("生成内容需要OpenAI API密钥")

        prompt = f"""
        **User Prompt：** 

        请为节日 **{holiday_name}** 生成一封温暖得体的双语祝福邮件，受众为中外混合团队的同事。邮件需包含以下要素：  

        1. **节日背景与意义**  
        - 用1-2句话说明节日的起源或核心意义（如春节象征辞旧迎新），语言生动且有文化共鸣（避免学术化描述）。  
        - 描述典型节日氛围（如“张灯结彩”“家人团聚的温馨”），帮助国际同事理解情感基调。  

        2. **传统习俗与庆祝方式**  
        - 列举1-2个代表性习俗（如中秋赏月、端午赛龙舟），简短解释其寓意（如“月饼象征团圆”）。  
        - 若节日含饮食文化（如冬至饺子），可自然提及，增加生活化亲切感。  

        3. **祝福语与团队关联**  
        - 表达对收件人及家人的祝愿（如健康、事业），并适当关联团队合作（如“感谢大家一年的支持”）。  
        - 中文祝福需简洁押韵（如“新春快乐，万事如意”），英文祝福避免直译（用“Wishing you joy and prosperity”代替“Hope you happy”）。  

        4. **文化金句**  
        - 引用一句与节日相关的经典诗词或谚语（如苏轼中秋词“但愿人长久”），附简短白话解释其情感（如“表达对长久团圆的美好期盼”）。  
        - 中英文版本均需保留金句，英文可意译（如“千里共婵娟”译为“Though miles apart, we share the same moon”）。  

        **语言与格式要求：**  
        - 结构：中文内容在前，英文在后，中间用分隔线（如“------”）区分。  
        - 语气：亲切如同事交谈，避免刻板（如用“我们”而非“本人”）。  
        - 敏感提示：若节日含宗教背景（如圣诞节），祝福需包容多元文化（如用“节日快乐”而非“圣诞快乐”）。  
        - 输出：标题跟内容都以字符串形式输出，中文内容跟英文内容都不要有任何的注解，也不要带有任何的格式符号。英文输出不要只是中文输出的翻译。

        **输出示例：**  
        标题：新春祝福 | Warm Wishes for the Lunar New Year

        亲爱的同事们，  
        春节是家人团聚、辞旧迎新的时刻……（中文内容）  
        ------
        Dear team,  
        The Lunar New Year marks a time for reunion and new beginnings…（英文内容） 
        """

        response = self.client.run(prompt)

        content = response.content

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


