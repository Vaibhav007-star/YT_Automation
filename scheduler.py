import schedule
import time
import subprocess

def upload_video():
    print("Starting upload...")
    subprocess.run(["python", "uploader.py"])

# Upload times
schedule.every().day.at("11:30").do(upload_video)
schedule.every().day.at("18:00").do(upload_video)
schedule.every().day.at("23:00").do(upload_video)

print("Scheduler running...")

while True:
    schedule.run_pending()
    time.sleep(30)