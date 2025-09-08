# AI节日邮件发送
一个用于在节假日的时候发送邮件的AI程序。使用到AI生成邮件内容

## 数据来源
- [节假日API](https://holiday.dreace.top/)
  - 传递日期到API，获取日期是否为节假日信息
- 使用Agent方式调用大模型判断发送时间

## 功能特点
- 自动检测今天是否为中国传统节日或节气
- 智能判断工作日：
  - 如果节日/节气是非工作日（周六、周日或法定节假日），会在前一个工作日发送邮件
  - 自动识别法定节假日和补班安排，确保在正确的工作日发送邮件
- 使用Agent方式调用大模型生成节日/节气相关的邮件内容
- 自动发送邮件给配置的收件人列表
- 支持强制发送模式和测试模式
- 支持自定义OpenAI API基础URL
- 支持自定义OpenAI模型

## 安装

1. 克隆仓库
```bash
git clone https://github.com/yourusername/cn_holiday_email.git
cd cn_holiday_email
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 创建配置文件
```bash
python main.py --create-config
```

4. 编辑配置文件 `config.json`，填入您的邮箱信息

5. 设置环境变量以提供OpenAI API密钥
```bash
# Windows
set OPENAI_API_KEY=your_api_key

# Linux/Mac
export OPENAI_API_KEY=your_api_key
```

6. （可选）设置环境变量以提供OpenAI API基础URL
```bash
# Windows
set OPENAI_API_BASE=your_api_base_url

# Linux/Mac
export OPENAI_API_BASE=your_api_base_url
```

7. （可选）设置环境变量以指定OpenAI模型（注意：当设置了`OPENAI_API_MODEL`模型时，配置文件的`email_model`和`date_model`都将使用此模型）
```bash
# Windows
set OPENAI_API_MODEL=your_model_name

# Linux/Mac
export OPENAI_API_MODEL=your_model_name
```

## 使用方法

### 基本用法
```bash
python main.py
```

### 使用自定义配置文件
```bash
python main.py --config your_config.json
```

### 创建自定义配置文件
```bash
python main.py --create-config
```

### 测试模式（不实际发送邮件）
```bash
python main.py --test
```

### 强制发送模式（即使今天不是特殊日期）
```bash
python main.py --force
```

## 项目结构
- `main.py`: 主程序入口
- `date_fetcher.py`: 日期获取模块
- `content_generator.py`: 内容生成模块
- `email_sender.py`: 邮件发送模块
- `config.json`: 配置文件
- `date.json`: 由 `date_fetcher.py` 获取的日期数据

## 配置文件说明
```json
{
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
    "api_key": "",  // 从环境变量中读取
    "base_url": "",  // 从环境变量中读取（可选）
    "email_model": "gpt-3.5-turbo",  // 从环境变量中读取（可选）
    "date_model": "Qwen/Qwen3-Coder-30B-A3B-Instruct"  // 从环境变量中读取（可选）
  },
  "holiday": {
    "date_fetch_weekday": 6,  // date_fetcher.py 运行时的星期数。6表示周日才运行
    "apart_day": 7  // 获取日期相隔天数，默认为7天。如：2025-01-01和2025-01-08之间的日期，则 apart_day 为7天。
  }
}
```

## 环境变量

- `OPENAI_API_KEY`: OpenAI API密钥（必需）
- `OPENAI_API_BASE`: OpenAI API基础URL（可选）
- `OPENAI_API_MODEL`: OpenAI模型名称（可选，默认为"gpt-3.5-turbo"）