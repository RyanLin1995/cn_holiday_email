from datetime import datetime


def should_send_email_today(date_info):
    if date_info["nearest_workday"] and date_info["nearest_workday"] == datetime.now().strftime("%Y-%m-%d"):
        return True
    else:
        return False


