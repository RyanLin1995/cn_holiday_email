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
            **User Prompt：** 

            请为节日 **{special_date_info.get('name')}** 生成一封温暖得体的双语祝福邮件，受众为中外混合团队的同事。邮件需包含以下要素：  

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
        elif special_date_type == "jieqi":
            prompt = f"""
            **User Prompt：**  

            请为中国传统节气 **{special_date_info.get('name')}** 生成一封温暖得体的双语问候邮件，受众为中外混合团队的同事。邮件需包含以下要素：  

            1. **节气背景与意义**  
            - 用1-2句话说明节气的天文或农业意义（如“芒种”象征播种希望），语言优美且易于理解。  
            - 描述节气的典型自然景象（如“白露凝霜，秋意渐浓”），帮助国际同事感受季节变化。  

            2. **气候特点与自然现象**  
            - 简要提及该节气的温度、降水或物候特征（如“冬至昼短夜长”），并融入对自然规律的感悟（如“万物休养，静待春归”）。  

            3. **传统习俗与饮食文化**  
            - 列举1-2个代表性习俗（如清明踏青、大暑饮伏茶），解释其健康或文化寓意（如“菊花酒驱寒避邪”）。  
            - 若有节气特色饮食（如立春咬春饼），可自然提及，增强生活气息。  

            4. **文化金句**  
            - 引用一句与节气相关的诗词或谚语（如杜甫“露从今夜白，月是故乡明”），附白话解释其意境（如“表达对故乡与亲人的思念”）。  
            - 中英文版本均需保留金句，英文可意译（如“月是故乡明”译为“The moon shines brightest at home”）。  

            5. **祝福语与团队关联**  
            - 结合节气特点表达祝愿（如“愿秋分为您带来平衡与丰收”），可适当关联工作（如“期待我们共同收获项目成果”）。  
            - 中文祝福需凝练（如“暑去凉来，珍重加衣”），英文避免直译（用“May the cool breeze bring you freshness”代替“Hope you not hot”）。  

            **语言与格式要求：**  
            - 结构：中文内容在前，英文在后，中间用分隔线（如“------”）区分。  
            - 语气：亲切如朋友交谈，避免说教（如用“我们常说”而非“古人云”）。  
            - 文化提示：对国际同事可简短解释节气在农历中的重要性（如“二十四节气是中国古代农耕文明的智慧”）。  
            - 输出：标题跟内容都以字符串形式输出，中文内容跟英文内容都不要有任何的注解，也不要带有任何的格式符号。英文输出不要只是中文输出的翻译。

            **输出示例：**  
            标题：秋分问候 | Autumn Equinox Wishes

            亲爱的朋友们，  
            秋分是昼夜平分的日子，象征着平衡与收获……（中文内容）  
            ------
            Dear all,  
            The Autumn Equinox balances day and night, marking a time of harmony…（英文内容）  
            """
        else:
            raise ValueError(f"不支持的特殊日期类型: {special_date_type}")

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": open('system_prompt.md', 'r', encoding='utf-8').read()},
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


