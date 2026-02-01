from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import json
import os
from services.update_data_api import fetch_data_from_api

# Global scheduler instance
scheduler = BackgroundScheduler()
scheduler.start()

# File untuk menyimpan konfigurasi jadwal
SCHEDULE_CONFIG_FILE = "data/schedule_config.json"


def load_schedule_config():
    """Load konfigurasi jadwal dari file"""
    try:
        if os.path.exists(SCHEDULE_CONFIG_FILE):
            with open(SCHEDULE_CONFIG_FILE, 'r') as f:
                return json.load(f)
        return None
    except Exception as e:
        print(f"Error loading schedule config: {e}")
        return None


def save_schedule_config(config):
    """Save konfigurasi jadwal ke file"""
    try:
        os.makedirs(os.path.dirname(SCHEDULE_CONFIG_FILE), exist_ok=True)
        with open(SCHEDULE_CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving schedule config: {e}")
        return False


def scheduled_fetch_job():
    """Job yang akan dijalankan sesuai jadwal"""
    try:
        print(f"[{datetime.now()}] Running scheduled data fetch...")
        result = fetch_data_from_api('all', 1990, 2023)
        
        if result.get('success'):
            print(f"[{datetime.now()}] Scheduled fetch completed successfully!")
            print(f"  - Energy records: {result.get('energyCount', 0)}")
            print(f"  - GDP records: {result.get('gdpCount', 0)}")
        else:
            print(f"[{datetime.now()}] Scheduled fetch failed: {result.get('message')}")
            
    except Exception as e:
        print(f"[{datetime.now()}] Error in scheduled job: {str(e)}")


def setup_schedule(frequency, time_str, timezone='Asia/Jakarta', enabled=True):
    """
    Setup jadwal scraping otomatis
    
    Args:
        frequency: 'daily', 'weekly', 'monthly'
        time_str: waktu dalam format 'HH:MM' (misal: '02:00')
        timezone: timezone string (default: 'Asia/Jakarta')
        enabled: aktif atau tidak
    """
    try:
        # Remove existing job if any
        if scheduler.get_job('data_fetch_job'):
            scheduler.remove_job('data_fetch_job')
        
        if not enabled:
            print("Schedule disabled by user")
            return True
        
        # Parse time
        hour, minute = map(int, time_str.split(':'))
        
        # Create cron trigger based on frequency
        if frequency == 'daily':
            # Setiap hari pada waktu tertentu
            trigger = CronTrigger(
                hour=hour,
                minute=minute,
                timezone=timezone
            )
        elif frequency == 'weekly':
            # Setiap minggu (hari Senin) pada waktu tertentu
            trigger = CronTrigger(
                day_of_week='mon',
                hour=hour,
                minute=minute,
                timezone=timezone
            )
        elif frequency == 'monthly':
            # Setiap bulan (tanggal 1) pada waktu tertentu
            trigger = CronTrigger(
                day=1,
                hour=hour,
                minute=minute,
                timezone=timezone
            )
        elif frequency == 'yearly':
            # Setiap tahun (bulan Juni tanggal 1) pada waktu tertentu
            trigger = CronTrigger(
                month=6,
                day=1,
                hour=hour,
                minute=minute,
                timezone=timezone
            )
        else:
            raise ValueError(f"Invalid frequency: {frequency}")
        
        # Add job to scheduler
        scheduler.add_job(
            scheduled_fetch_job,
            trigger=trigger,
            id='data_fetch_job',
            name='Scheduled Data Fetch',
            replace_existing=True
        )
        
        print(f"Schedule setup successful: {frequency} at {time_str} ({timezone})")
        return True
        
    except Exception as e:
        print(f"Error setting up schedule: {str(e)}")
        return False


def get_next_run_time():
    """Get waktu eksekusi berikutnya"""
    try:
        job = scheduler.get_job('data_fetch_job')
        if job and job.next_run_time:
            return job.next_run_time.strftime("%d %b %Y %H:%M:%S")
        return None
    except Exception as e:
        print(f"Error getting next run time: {e}")
        return None


def get_schedule_status():
    """Get status jadwal saat ini"""
    try:
        config = load_schedule_config()
        job = scheduler.get_job('data_fetch_job')
        
        return {
            "enabled": config.get('enabled', False) if config else False,
            "frequency": config.get('frequency') if config else None,
            "time": config.get('time') if config else None,
            "timezone": config.get('timezone') if config else None,
            "next_run": get_next_run_time(),
            "is_running": job is not None
        }
    except Exception as e:
        print(f"Error getting schedule status: {e}")
        return {
            "enabled": False,
            "is_running": False
        }


def initialize_scheduler():
    """Initialize scheduler dari saved config saat aplikasi start"""
    try:
        config = load_schedule_config()
        if config and config.get('enabled'):
            setup_schedule(
                frequency=config.get('frequency', 'monthly'),
                time_str=config.get('time', '02:00'),
                timezone=config.get('timezone', 'Asia/Jakarta'),
                enabled=True
            )
            print("Scheduler initialized from saved config")
    except Exception as e:
        print(f"Error initializing scheduler: {e}")
