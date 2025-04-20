from datetime import datetime, timedelta
from data_fetcher import DataFetcher

class DateChecker:
    def __init__(self, data_fetcher=None):
        """使用DataFetcher初始化DateChecker。

        参数:
            data_fetcher (DataFetcher, 可选): DataFetcher实例。如果为None，则创建一个新的实例。
        """
        self.data_fetcher = data_fetcher or DataFetcher()
        self.current_year = datetime.now().year
        self.jieqi_data = self.data_fetcher.fetch_jieqi(self.current_year)
        self.holiday_data = self.data_fetcher.fetch_holidays(self.current_year)

    def is_today_jieqi(self):
        """检查今天是否为节气。

        返回:
            dict 或 None: 如果今天是节气，返回节气信息，否则返回None
        """
        today = datetime.now().strftime("%Y-%m-%d")

        for jieqi in self.jieqi_data.get("data", []):
            # 检查节气是否有date字段，如果没有，从时间中提取
            jieqi_date = jieqi.get("date")
            if not jieqi_date and "time" in jieqi:
                # 从时间字符串中提取日期部分 (YYYY-MM-DD)
                time_str = jieqi.get("time")
                if time_str:
                    jieqi_date = time_str.split(" ")[0]

            if jieqi_date == today:
                return jieqi

        return None

    def is_today_holiday(self):
        """检查今天是否为节假日。

        返回:
            dict 或 None: 如果今天是节假日，返回节假日信息，否则返回None
        """
        today = datetime.now().strftime("%Y-%m-%d")
        today_date = datetime.now().date()

        for holiday in self.holiday_data.get("data", []):
            # 检查今天是否在节假日期间内
            start_date = holiday.get("start")
            end_date = holiday.get("end")

            if start_date and end_date:
                start = datetime.strptime(start_date, "%Y-%m-%d").date()
                end = datetime.strptime(end_date, "%Y-%m-%d").date()

                if start <= today_date <= end:
                    # 创建节假日信息字典
                    holiday_info = {
                        "name": holiday.get("name"),
                        "date": today,
                        "start": start_date,
                        "end": end_date
                    }
                    return holiday_info

        return None

    def get_today_special_date(self):
        """检查今天是否为特殊日期（节假日或节气）。

        返回:
            tuple: (type, data) 其中type是 "holiday", "jieqi", 或 None,
                  data是相应的信息
        """
        holiday = self.is_today_holiday()
        if holiday:
            return "holiday", holiday

        jieqi = self.is_today_jieqi()
        if jieqi:
            return "jieqi", jieqi

        return None, None

    def get_upcoming_special_dates(self, days=7):
        """获取指定天数内的即将到来的特殊日期。

        参数:
            days (int): 往后看的天数

        返回:
            list: 即将到来的特殊日期的(date, type, data)元组列表
        """
        today = datetime.now().date()
        end_date = today + timedelta(days=days)
        upcoming = []

        # 检查即将到来的节假日
        for holiday in self.holiday_data.get("data", []):
            start_date = holiday.get("start")
            if start_date:
                start = datetime.strptime(start_date, "%Y-%m-%d").date()

                # 如果节假日在我们的范围内开始
                if today < start <= end_date:
                    holiday_info = {
                        "name": holiday.get("name"),
                        "date": start_date,
                        "start": start_date,
                        "end": holiday.get("end")
                    }
                    upcoming.append((start_date, "holiday", holiday_info))

        # 检查即将到来的节气
        for jieqi in self.jieqi_data.get("data", []):
            # 从 date 字段或 time 字段获取日期
            jieqi_date = jieqi.get("date")
            if not jieqi_date and "time" in jieqi:
                time_str = jieqi.get("time")
                if time_str:
                    jieqi_date = time_str.split(" ")[0]

            if jieqi_date:
                date = datetime.strptime(jieqi_date, "%Y-%m-%d").date()

                # 如果节气在我们的范围内
                if today < date <= end_date:
                    # Create a copy of the jieqi info to avoid modifying the original
                    jieqi_info = jieqi.copy()
                    if "date" not in jieqi_info and jieqi_date:
                        jieqi_info["date"] = jieqi_date
                    upcoming.append((jieqi_date, "jieqi", jieqi_info))

        # Sort by date
        upcoming.sort(key=lambda x: x[0])

        return upcoming

    def is_workday(self, date):
        """检查给定日期是否为工作日（周一至周五且不在法定节假日范围内）。

        参数:
            date: datetime.date 对象或可转换为日期的字符串

        返回:
            bool: 如果是工作日返回True，否则返回False
        """
        if isinstance(date, str):
            date = datetime.strptime(date, "%Y-%m-%d").date()

        # 首先检查是否是周一至周五（0-6对应周一至周日）
        if date.weekday() >= 5:
            return False

        # 然后检查是否在法定节假日范围内
        date_str = date.strftime("%Y-%m-%d")

        for holiday in self.holiday_data.get("data", []):
            start_date = holiday.get("start")
            end_date = holiday.get("end")

            if start_date and end_date:
                start = datetime.strptime(start_date, "%Y-%m-%d").date()
                end = datetime.strptime(end_date, "%Y-%m-%d").date()

                if start <= date <= end:
                    # 检查是否有补班安排（在节假日期间需要上班的日期）
                    work_days = holiday.get("work", [])
                    if date_str in work_days:
                        return True  # 这是补班日，是工作日
                    return False  # 在节假日范围内且不是补班日，不是工作日

        return True  # 不在任何节假日范围内的工作日

    def get_next_workday_for_special_date(self, days_ahead=7):
        """获取即将到来的特殊日期，如果特殊日期是非工作日，则返回其前一个工作日。

        参数:
            days_ahead (int): 往后看的天数

        返回:
            tuple: (today_should_send, special_date_type, special_date_info)
                  today_should_send: 布尔值，表示今天是否应该发送邮件
                  special_date_type: 特殊日期类型（"holiday", "jieqi", 或 None）
                  special_date_info: 特殊日期信息
        """
        today = datetime.now().date()

        # 首先检查今天是否为特殊日期
        special_date_type, special_date_info = self.get_today_special_date()
        if special_date_type:
            return True, special_date_type, special_date_info

        # 获取即将到来的特殊日期
        upcoming = self.get_upcoming_special_dates(days=days_ahead)

        for date_str, type_str, info in upcoming:
            special_date = datetime.strptime(date_str, "%Y-%m-%d").date()

            # 如果特殊日期是非工作日（周末或法定节假日）
            if not self.is_workday(special_date):
                # 找到特殊日期前的最后一个工作日
                last_workday = special_date - timedelta(days=1)  # 先往前看一天
                # 往前找直到找到工作日
                max_days_to_check = 10  # 防止无限循环
                days_checked = 0

                while not self.is_workday(last_workday) and days_checked < max_days_to_check:
                    last_workday = last_workday - timedelta(days=1)
                    days_checked += 1

                # 如果找不到工作日，则返回原始日期
                if days_checked >= max_days_to_check:
                    return False, None, None

                # 如果今天是该特殊日期前的最后一个工作日
                if today == last_workday:
                    return True, type_str, info

            # 如果特殊日期是工作日且就是今天
            elif special_date == today:
                return True, type_str, info

        return False, None, None
