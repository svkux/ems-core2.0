"""
EMS-Core v2.0 - Scheduler
Verwaltet Zeitpläne für Verbraucher
"""
import json
import logging
from datetime import datetime, time, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class Scheduler:
    """Zeitplan-Management für Verbraucher"""
    
    def __init__(self, config_path: str = "config/schedules.json"):
        self.config_path = Path(config_path)
        self.schedules: Dict[str, Dict] = {}
        self.load_schedules()
        
    def load_schedules(self):
        """Lade Zeitpläne aus JSON"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    self.schedules = json.load(f)
                logger.info(f"Loaded {len(self.schedules)} schedules")
            else:
                logger.warning(f"No schedules file found at {self.config_path}")
                self.schedules = {}
        except Exception as e:
            logger.error(f"Failed to load schedules: {e}")
            self.schedules = {}
    
    def save_schedules(self):
        """Speichere Zeitpläne in JSON"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.schedules, f, indent=2)
            logger.info(f"Saved {len(self.schedules)} schedules")
        except Exception as e:
            logger.error(f"Failed to save schedules: {e}")
    
    def add_schedule(self, device_id: str, schedule: Dict):
        """Füge Zeitplan für Gerät hinzu"""
        self.schedules[device_id] = {
            "device_id": device_id,
            "schedule": schedule,
            "enabled": True
        }
        self.save_schedules()
        logger.info(f"Added schedule for {device_id}")
    
    def remove_schedule(self, device_id: str):
        """Entferne Zeitplan für Gerät"""
        if device_id in self.schedules:
            del self.schedules[device_id]
            self.save_schedules()
            logger.info(f"Removed schedule for {device_id}")
    
    def is_in_schedule(self, device_id: str, check_time: Optional[datetime] = None) -> bool:
        """Prüfe ob Gerät aktuell im Zeitplan ist"""
        if device_id not in self.schedules:
            return False
        
        schedule_data = self.schedules[device_id]
        if not schedule_data.get("enabled", True):
            return False
        
        schedule = schedule_data.get("schedule", {})
        if not schedule:
            return False
        
        if check_time is None:
            check_time = datetime.now()
        
        weekday = check_time.strftime("%A").lower()
        if weekday not in schedule:
            return False
        
        current_hour = check_time.hour
        current_minute = check_time.minute
        current_time_minutes = current_hour * 60 + current_minute
        
        for time_window in schedule[weekday]:
            if len(time_window) != 2:
                continue
                
            start_hour, end_hour = time_window
            start_minutes = start_hour * 60
            end_minutes = end_hour * 60
            
            if start_minutes <= current_time_minutes < end_minutes:
                return True
        
        return False
    
    def validate_schedule(self, schedule: Dict) -> bool:
        """Validiere Zeitplan-Format"""
        valid_days = ["monday", "tuesday", "wednesday", "thursday", 
                      "friday", "saturday", "sunday"]
        
        for day, windows in schedule.items():
            if day not in valid_days:
                logger.error(f"Invalid day: {day}")
                return False
            
            if not isinstance(windows, list):
                logger.error(f"Windows must be list for {day}")
                return False
            
            for window in windows:
                if not isinstance(window, list) or len(window) != 2:
                    logger.error(f"Invalid window format: {window}")
                    return False
                
                start, end = window
                if not (0 <= start < 24 and 0 <= end <= 24 and start < end):
                    logger.error(f"Invalid time range: {start}-{end}")
                    return False
        
        return True
