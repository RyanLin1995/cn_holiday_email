import os
import json
from datetime import datetime, timedelta
import calendar
from data_fetcher import DataFetcher

class ScheduleManager:
    def __init__(self, data_dir="data", data_fetcher=None):
        """初始化ScheduleManager，设置存储数据文件的目录。

        参数:
            data_dir (str): 存储数据文件的目录
            data_fetcher (DataFetcher, 可选): DataFetcher实例。如果为None，则创建一个新的实例。
        """
        self.data_dir = data_dir
        # 如果目录不存在，创建目录
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        self.schedule_file = os.path.join(self.data_dir, "monthly_schedule.json")
        
        # 初始化DataFetcher
        self.data_fetcher = data_fetcher or DataFetcher(data_dir)
        self.current_year = datetime.now().year
        
        # 获取节气和节假日数据，确保数据与当前年份匹配
        self.jieqi_data = self.data_fetcher.fetch_jieqi(self.current_year)
        self.holiday_data = self.data_fetcher.fetch_holidays(self.current_year)
    
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
        
    def generate_monthly_schedule(self):
        """生成本月的邮件发送日程表。
            
        返回:
            dict: 本月的邮件发送日程表
        """
        today = datetime.now()
        current_year = today.year
        current_month = today.month
        
        # 获取当月的第一天和最后一天
        first_day = datetime(current_year, current_month, 1).date()
        last_day = datetime(current_year, current_month, 
                           calendar.monthrange(current_year, current_month)[1]).date()
        
        # 获取下个月的前几天（用于处理跨月节日）
        next_month_days = 3  # 检查下个月的前7天
        
        # 计算需要查看的天数（包括本月和下个月的前几天）
        days_to_check = (last_day - first_day).days + 1 + next_month_days
        
        # 获取所有特殊日期
        special_dates = []
        current_date = first_day
        
        for _ in range(days_to_check):
            date_str = current_date.strftime("%Y-%m-%d")
            
            # 检查是否为节假日
            for holiday in self.holiday_data.get("data", []):
                start_date = holiday.get("start")
                end_date = holiday.get("end")
                
                if start_date and end_date:
                    start = datetime.strptime(start_date, "%Y-%m-%d").date()
                    end = datetime.strptime(end_date, "%Y-%m-%d").date()
                    
                    if start <= current_date <= end:
                        holiday_info = {
                            "name": holiday.get("name")
                        }
                        special_dates.append((date_str, "holiday", holiday_info))
                        break
            
            # 检查是否为节气
            for jieqi in self.jieqi_data.get("data", []):
                jieqi_date = jieqi.get("date")
                if not jieqi_date and "time" in jieqi:
                    time_str = jieqi.get("time")
                    if time_str:
                        jieqi_date = time_str.split(" ")[0]
                
                if jieqi_date == date_str:
                    jieqi_info = {
                        "name": jieqi.get("name")
                    }
                    special_dates.append((date_str, "jieqi", jieqi_info))
                    break
            
            current_date += timedelta(days=1)
        
        # 计算每个特殊日期的邮件发送日期
        email_schedule = {}
        
        # 对特殊日期进行去重处理
        for date_str, type_str, info in special_dates:
            special_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            
            # 判断是否为下个月的日期
            is_next_month = special_date.month != current_month
            
            # 如果是下个月的日期，将发送日期设置为本月最后一个工作日
            if is_next_month:
                send_date = last_day
                while not self.is_workday(send_date):
                    send_date = send_date - timedelta(days=1)
            # 如果是本月的日期且是非工作日，找到前一个工作日
            elif not self.is_workday(special_date):
                send_date = special_date - timedelta(days=1)  # 先往前看一天
                # 往前找直到找到工作日
                max_days_to_check = 10  # 防止无限循环
                days_checked = 0
                
                while not self.is_workday(send_date) and days_checked < max_days_to_check:
                    send_date = send_date - timedelta(days=1)
                    days_checked += 1
                
                # 如果找不到工作日，则使用原始日期
                if days_checked >= max_days_to_check:
                    send_date = special_date
            else:
                send_date = special_date
            
            send_date_str = send_date.strftime("%Y-%m-%d")
            
            # 将发送日期添加到日程表中，进行去重处理
            if send_date_str not in email_schedule:
                email_schedule[send_date_str] = []
            
            # 检查是否已经存在相似的节日名称
            current_name = info["name"]
            is_duplicate = False
            
            for existing_entry in email_schedule[send_date_str]:
                existing_name = existing_entry["info"]["name"]
                if current_name in existing_name or existing_name in current_name:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                email_schedule[send_date_str].append({
                    "type": type_str,
                    "info": info,
                    "original_date": date_str
                })
        
        return email_schedule
    
    def save_monthly_schedule(self, schedule):
        """保存月度邮件发送日程表到文件。
        
        参数:
            schedule (dict): 月度邮件发送日程表
            
        返回:
            bool: 保存成功返回True，否则返回False
        """
        try:
            with open(self.schedule_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "month": datetime.now().strftime("%Y-%m"),
                    "schedule": schedule
                }, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存月度日程表失败: {str(e)}")
            return False
    
    def load_monthly_schedule(self):
        """从文件加载月度邮件发送日程表。如果文件不存在或月份不匹配，则生成新的日程表。
        
        返回:
            dict: 月度邮件发送日程表
        """
        current_month = datetime.now().strftime("%Y-%m")
        
        # 尝试从文件加载日程表
        if os.path.exists(self.schedule_file):
            try:
                with open(self.schedule_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # 检查月份是否匹配
                    if data.get("month") == current_month:
                        return data.get("schedule")
                    else:
                        print(f"月度日程表月份不匹配，当前月份: {current_month}，文件月份: {data.get('month')}，将重新生成")
            except Exception as e:
                print(f"加载月度日程表失败: {str(e)}")
        else:
            print(f"月度日程表文件不存在，将创建新文件: {self.schedule_file}")
        
        # 如果无法从文件加载或月份不匹配，生成新的日程表
        schedule = self.generate_monthly_schedule()
        self.save_monthly_schedule(schedule)
        return schedule
    
    def should_send_email_today(self, date=None):
        """检查今天是否应该发送邮件。
        参数:
            date (str): 可选参数，指定要检查的日期，格式为%Y-%m-%d。如果未提供，则使用当前日期。
        
        返回:
            tuple: (should_send, special_date_type, special_date_info)
                  should_send: 布尔值，表示今天是否应该发送邮件
                  special_date_type: 特殊日期类型（"holiday", "jieqi", 或 None）
                  special_date_info: 特殊日期信息
        """
        today = date if date else datetime.now().strftime("%Y-%m-%d")

        # 获取日程表
        schedule = self.load_monthly_schedule()
        
        if today in schedule and schedule[today]:
            # 如果今天有特殊日期，选择第一个
            special_date_entry = schedule[today][0]
            return True, special_date_entry["type"], special_date_entry["info"]
        
        return False, None, None