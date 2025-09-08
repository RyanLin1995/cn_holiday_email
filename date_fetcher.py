from datetime import datetime, timedelta

import httpx
from agno.agent import Agent
from agno.models.openai import OpenAILike
from dotenv import load_dotenv

load_dotenv()


def is_working_date_tool(date: str) -> dict:
    """将判断日期是否为工作日"""
    target_date = datetime.strptime(date, "%Y-%m-%d").date()
    api_link = rf"https://holiday.dreace.top/?date={target_date}"
    # 处理周末
    response = httpx.get(api_link)
    if response.status_code == 200:
        data = response.json()
        if data["isHoliday"]:
            if data["note"] == "周末":
                return {
                    "isHoliday": False,
                    "note": "周末",
                    "holiday_name": data["note"],
                    "date": data["date"],
                }
            else:
                return {
                    "isHoliday": True,
                    "note": "节日",
                    "holiday_name": data["note"],
                    "date": data["date"],
                }
        else:
            return {
                "isHoliday": False,
                "note": "工作日",
                "holiday_name": data["note"],
                "date": data["date"],
            }

    return {}


def create_return_json(response_data):
    """
    根据 Agent 返回的信息创建 json 文件
    """
    with open("date.json", "w", encoding="utf-8") as f:
        f.write(response_data)


def is_run(date_fetch_weekday):
    """
    返回今天是否为周日
    """
    return datetime.now().weekday() == date_fetch_weekday


def date_fetch_main(base_url, api_key, model, apart_day, date_fetch_weekday):
    """获取未来日期中是否存在节日

    参数:
        base_url (str, 可选): OpenAI API基础URL。默认从环境变量获取。
        api_key (str, 可选): OpenAI API密钥。默认从环境变量获取。
        model (str, 可选): 要使用的OpenAI模型。默认从环境变量获取或使用'gpt-3.5-turbo'。
        apart_day (int, 可选): 两个日期之间的间隔
        date_fetch_weekday (int, 可选): 每周星期几获取日期
    """
    agent_model = OpenAILike(base_url=base_url, api_key=api_key, id=model)
    prompt = f"""
    # 你是一个中国节假日数据处理大师，请帮完成以下需求：
    ### 需求：
    - 请找到{datetime.now().strftime('%Y-%m-%d')}至{(datetime.now() + timedelta(days=apart_day)).strftime('%Y-%m-%d')}之间的所有节假日，以及节假日的前一个工作日，以 json 格式返回一个文件。格式为：
    ```json
    {{
        "isHoliday": true,
        "holiday_name": "节日名称",
        "nearest_workday": "距离节日最近的工作日"
    }}
    ```

    ### 提示：
    - 不要输出其他内容
    - 如果遇到错误，请返回空的 json
    - 如果是连续的节日，只需返回第一个节日的日期即可
    - 如果返回的节假日中存在相同工作日，请把他们合并为一个
    """
    if is_run(date_fetch_weekday):
        agent = Agent(
            tools=[is_working_date_tool, create_return_json],
            name="Date Assist",
            model=agent_model,
        )
        agent.run(prompt)
