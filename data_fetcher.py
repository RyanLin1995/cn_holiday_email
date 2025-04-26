import requests
import json
import os
import re
from datetime import datetime

class DataFetcher:
    def __init__(self, data_dir="data"):
        """初始化DataFetcher，设置存储数据文件的目录。

        参数:
            data_dir (str): 存储数据文件的目录
        """
        self.data_dir = data_dir
        # 如果目录不存在，创建目录
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        # 节气拼音到中文的映射
        self.jieqi_mapping = {
            "LI_CHUN": "立春",
            "YU_SHUI": "雨水",
            "JING_ZHE": "惊蛰",
            "CHUN_FEN": "春分",
            "QING_MING": "清明",
            "GU_YU": "谷雨",
            "LI_XIA": "立夏",
            "XIAO_MAN": "小满",
            "MANG_ZHONG": "芒种",
            "XIA_ZHI": "夏至",
            "XIAO_SHU": "小暑",
            "DA_SHU": "大暑",
            "LI_QIU": "立秋",
            "CHU_SHU": "处暑",
            "BAI_LU": "白露",
            "QIU_FEN": "秋分",
            "HAN_LU": "寒露",
            "SHUANG_JIANG": "霜降",
            "LI_DONG": "立冬",
            "XIAO_XUE": "小雪",
            "DA_XUE": "大雪",
            "DONG_ZHI": "冬至",
            "XIAO_HAN": "小寒",
            "DA_HAN": "大寒"
        }

    @staticmethod
    def _is_file_for_year(file_path, year):
        """检查文件的创建时间是否与指定年份匹配。

        参数:
            file_path (str): 文件路径
            year (int): 要检查的年份

        返回:
            bool: 如果文件创建年份与指定年份匹配返回True，否则返回False
        """
        try:
            # 获取文件的创建时间
            file_creation_time = os.path.getctime(file_path)
            # 转换为datetime对象
            creation_date = datetime.fromtimestamp(file_creation_time)
            # 提取年份并比较
            file_year = creation_date.year
            return file_year == year
        except Exception:
            return False

    def _convert_pinyin_to_chinese(self, data):
        """将拼音节气名称转换为中文。

        参数:
            data (dict): 节气数据

        返回:
            dict: 带有中文名称的节气数据
        """
        if "data" in data:
            for item in data["data"]:
                if "name" in item and item["name"] in self.jieqi_mapping:
                    item["name"] = self.jieqi_mapping[item["name"]]
        return data

    @staticmethod
    def _extract_date_from_time(data):
        """从节气数据的时间字符串中提取日期。

        参数:
            data (dict): 节气数据

        返回:
            dict: 添加了日期字段的节气数据
        """
        if "data" in data:
            for item in data["data"]:
                if "time" in item and "date" not in item:
                    # 从时间字符串中提取日期部分 (YYYY-MM-DD)
                    date_match = re.match(r'(\d{4}-\d{2}-\d{2})', item["time"])
                    if date_match:
                        item["date"] = date_match.group(1)
        return data

    def fetch_jieqi(self, year=None):
        """获取指定年份的节气数据。

        参数:
            year (int, 可选): 要获取数据的年份。默认为当前年份。

        返回:
            dict: 节气数据
        """
        if year is None:
            year = datetime.now().year

        # 检查是否已经有指定年份的数据
        jieqi_file = os.path.join(self.data_dir, f"jieqi_{year}.json")
        
        # 删除旧年份的数据文件或者年份不匹配的文件
        if os.path.exists(jieqi_file) and not self._is_file_for_year(jieqi_file, year):
            os.remove(jieqi_file)
            print(f"删除过期的节气数据文件: {jieqi_file}")
        
        # 如果文件存在且年份正确，直接读取
        if os.path.exists(jieqi_file):
            with open(jieqi_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                data = self._convert_pinyin_to_chinese(data)
                data = self._extract_date_from_time(data)
                return data

        # 从 API 获取数据
        url = f"https://api.timelessq.com/time/jieqi?year={year}"
        try:
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()

                # 将拼音名称转换为中文
                data = self._convert_pinyin_to_chinese(data)

                # 从时间中提取日期
                data = self._extract_date_from_time(data)

                # 保存数据到文件
                with open(jieqi_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

                return data
            else:
                raise Exception(f"获取节气数据失败: {response.status_code}")
        except Exception as e:
            # 如果API调用失败，尝试使用现有文件，即使年份不匹配
            if os.path.exists(jieqi_file):
                with open(jieqi_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    data = self._convert_pinyin_to_chinese(data)
                    data = self._extract_date_from_time(data)
                    return data
            raise e

    def fetch_holidays(self, year=None):
        """获取指定年份的节假日数据。

        参数:
            year (int, 可选): 要获取数据的年份。默认为当前年份。

        返回:
            dict: 节假日数据
        """
        if year is None:
            year = datetime.now().year

        # 检查是否已经有指定年份的数据
        holiday_file = os.path.join(self.data_dir, f"holiday_{year}.json")
        
        # 删除旧年份的数据文件或者年份不匹配的文件
        if os.path.exists(holiday_file) and not self._is_file_for_year(holiday_file, year):
            os.remove(holiday_file)
            print(f"删除过期的节假日数据文件: {holiday_file}")
        
        # 如果文件存在且年份正确，直接读取
        if os.path.exists(holiday_file):
            with open(holiday_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        # 从 API 获取数据
        url = f"https://api.timelessq.com/time/holiday?year={year}"
        try:
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()

                # 保存数据到文件
                with open(holiday_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

                return data
            else:
                raise Exception(f"获取节假日数据失败: {response.status_code}")
        except Exception as e:
            # 如果API调用失败，尝试使用现有文件，即使年份不匹配
            if os.path.exists(holiday_file):
                with open(holiday_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            raise e
