from schedule_manager import ScheduleManager

sm = ScheduleManager()
schedule = sm.generate_monthly_schedule()
sm.save_monthly_schedule(schedule)
print(sm.should_send_email_today('2025-04-29'))