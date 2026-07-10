from apscheduler.schedulers.blocking import BlockingScheduler
from analyze import analyze_and_store

def job():
    print("\n--- Running scheduled fetch + analysis ---")
    analyze_and_store()

if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(job, 'interval', minutes=20)
    print("Scheduler started. Fetching every 20 minutes. Press Ctrl+C to stop.")
    job()  # run once immediately on startup
    scheduler.start()
