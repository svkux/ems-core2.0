#!/usr/bin/env python3
"""
EMS-Core v2.0 - Schedule Manager
CRUD Operations für Zeitpläne
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, time

from core.optimizer.scheduler import Schedule, ScheduleType, TimeWindow, Condition

logger = logging.getLogger(__name__)


class ScheduleManager:
    """Manager für Zeitplan-Verwaltung"""
    
    def __init__(self, schedules_file: str = "config/schedules.json"):
        self.schedules_file = Path(schedules_file)
        self.schedules: Dict[str, Schedule] = {}
        
        self.load_schedules()
    
    def load_schedules(self):
        """Lade Schedules aus JSON"""
        try:
            if self.schedules_file.exists():
                with open(self.schedules_file, 'r') as f:
                    data = json.load(f)
                
                for schedule_data in data.get('schedules', []):
                    schedule = self._deserialize_schedule(schedule_data)
                    if schedule:
                        self.schedules[schedule.id] = schedule
                
                logger.info(f"✅ Loaded {len(self.schedules)} schedules")
            else:
                logger.info("ℹ️ No schedules file found, starting fresh")
                self.schedules = {}
        except Exception as e:
            logger.error(f"❌ Failed to load schedules: {e}", exc_info=True)
            self.schedules = {}
    
    def save_schedules(self):
        """Speichere Schedules als JSON"""
        try:
            self.schedules_file.parent.mkdir(parents=True, exist_ok=True)
            
            schedules_list = []
            for schedule in self.schedules.values():
                schedule_dict = self._serialize_schedule(schedule)
                schedules_list.append(schedule_dict)
            
            data = {'schedules': schedules_list}
            
            with open(self.schedules_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"💾 Saved {len(self.schedules)} schedules")
        except Exception as e:
            logger.error(f"❌ Failed to save schedules: {e}", exc_info=True)
    
    def _serialize_schedule(self, schedule: Schedule) -> Dict:
        """Konvertiere Schedule zu JSON-serialisierbarem Dict"""
        result = {
            'id': schedule.id,
            'name': schedule.name,
            'device_id': schedule.device_id,
            'schedule_type': schedule.schedule_type.value,
            'enabled': schedule.enabled,
            'action_in_window': schedule.action_in_window,
            'action_outside_window': schedule.action_outside_window,
            'override_priority': schedule.override_priority,
            'priority_in_window': schedule.priority_in_window,
            'description': schedule.description,
            'created_at': schedule.created_at,
            'last_modified': schedule.last_modified
        }
        
        # Time Window
        if schedule.time_window:
            result['time_window'] = {
                'start_time': schedule.time_window.start_time.strftime('%H:%M'),
                'end_time': schedule.time_window.end_time.strftime('%H:%M'),
                'days': schedule.time_window.days
            }
        
        # Conditions
        if schedule.conditions:
            result['conditions'] = [
                {
                    'parameter': c.parameter,
                    'operator': c.operator,
                    'value': c.value
                }
                for c in schedule.conditions
            ]
        
        return result
    
    def _deserialize_schedule(self, data: Dict) -> Optional[Schedule]:
        """Konvertiere Dict zu Schedule Object"""
        try:
            # Time Window
            time_window = None
            if 'time_window' in data:
                tw = data['time_window']
                time_window = TimeWindow(
                    start_time=datetime.strptime(tw['start_time'], '%H:%M').time(),
                    end_time=datetime.strptime(tw['end_time'], '%H:%M').time(),
                    days=tw['days']
                )
            
            # Conditions
            conditions = None
            if 'conditions' in data:
                conditions = [
                    Condition(
                        parameter=c['parameter'],
                        operator=c['operator'],
                        value=c['value']
                    )
                    for c in data['conditions']
                ]
            
            schedule = Schedule(
                id=data['id'],
                name=data['name'],
                device_id=data['device_id'],
                schedule_type=ScheduleType(data['schedule_type']),
                enabled=data.get('enabled', True),
                time_window=time_window,
                conditions=conditions,
                action_in_window=data.get('action_in_window', 'allow'),
                action_outside_window=data.get('action_outside_window', 'allow'),
                override_priority=data.get('override_priority', False),
                priority_in_window=data.get('priority_in_window'),
                description=data.get('description', ''),
                created_at=data.get('created_at'),
                last_modified=data.get('last_modified')
            )
            
            return schedule
            
        except Exception as e:
            logger.error(f"Failed to deserialize schedule: {e}")
            return None
    
    def add_schedule(self, schedule: Schedule) -> bool:
        """Füge Schedule hinzu"""
        try:
            if schedule.id in self.schedules:
                logger.warning(f"⚠️ Schedule {schedule.id} already exists")
                return False
            
            # Validierung
            is_valid, error_msg = self.validate_schedule(schedule)
            if not is_valid:
                logger.error(f"Invalid schedule: {error_msg}")
                return False
            
            # Timestamps
            if schedule.created_at is None:
                schedule.created_at = datetime.now().isoformat()
            schedule.last_modified = datetime.now().isoformat()
            
            self.schedules[schedule.id] = schedule
            self.save_schedules()
            
            logger.info(f"✅ Added schedule: {schedule.name} ({schedule.id})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to add schedule: {e}", exc_info=True)
            return False
    
    def update_schedule(self, schedule_id: str, updates: Dict) -> bool:
        """Update Schedule"""
        try:
            if schedule_id not in self.schedules:
                logger.warning(f"⚠️ Schedule {schedule_id} not found")
                return False
            
            schedule = self.schedules[schedule_id]
            
            # Update simple fields
            for key in ['name', 'enabled', 'action_in_window', 'action_outside_window',
                       'override_priority', 'priority_in_window', 'description']:
                if key in updates:
                    setattr(schedule, key, updates[key])
            
            # Update time_window
            if 'time_window' in updates:
                tw = updates['time_window']
                schedule.time_window = TimeWindow(
                    start_time=datetime.strptime(tw['start_time'], '%H:%M').time(),
                    end_time=datetime.strptime(tw['end_time'], '%H:%M').time(),
                    days=tw['days']
                )
            
            # Update conditions
            if 'conditions' in updates:
                schedule.conditions = [
                    Condition(
                        parameter=c['parameter'],
                        operator=c['operator'],
                        value=c['value']
                    )
                    for c in updates['conditions']
                ]
            
            # Validierung
            is_valid, error_msg = self.validate_schedule(schedule)
            if not is_valid:
                logger.error(f"Update would make schedule invalid: {error_msg}")
                return False
            
            schedule.last_modified = datetime.now().isoformat()
            
            self.save_schedules()
            logger.info(f"✅ Updated schedule: {schedule_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update schedule: {e}", exc_info=True)
            return False
    
    def remove_schedule(self, schedule_id: str) -> bool:
        """Entferne Schedule"""
        try:
            if schedule_id not in self.schedules:
                logger.warning(f"⚠️ Schedule {schedule_id} not found")
                return False
            
            del self.schedules[schedule_id]
            self.save_schedules()
            
            logger.info(f"🗑️ Removed schedule: {schedule_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to remove schedule: {e}", exc_info=True)
            return False
    
    def get_schedule(self, schedule_id: str) -> Optional[Schedule]:
        """Hole Schedule nach ID"""
        return self.schedules.get(schedule_id)
    
    def get_all_schedules(self) -> List[Schedule]:
        """Hole alle Schedules"""
        return list(self.schedules.values())
    
    def get_schedules_by_device(self, device_id: str) -> List[Schedule]:
        """Hole alle Schedules für ein Device"""
        return [s for s in self.schedules.values() if s.device_id == device_id]
    
    def get_enabled_schedules(self) -> List[Schedule]:
        """Hole alle aktivierten Schedules"""
        return [s for s in self.schedules.values() if s.enabled]
    
    def validate_schedule(self, schedule: Schedule) -> tuple[bool, str]:
        """Validiere Schedule"""
        # ID Check
        if not schedule.id or len(schedule.id) < 2:
            return False, "Invalid schedule ID"
        
        # Name Check
        if not schedule.name or len(schedule.name) < 2:
            return False, "Invalid schedule name"
        
        # Device ID Check
        if not schedule.device_id:
            return False, "Device ID required"
        
        # Schedule Type Check
        if not isinstance(schedule.schedule_type, ScheduleType):
            return False, "Invalid schedule type"
        
        # Time Window Check
        if schedule.schedule_type in [ScheduleType.TIME_WINDOW, ScheduleType.TIME_BLOCK, ScheduleType.CONDITIONAL]:
            if not schedule.time_window:
                return False, "Time window required for this schedule type"
            
            if not schedule.time_window.days:
                return False, "At least one day must be selected"
            
            for day in schedule.time_window.days:
                if day < 0 or day > 6:
                    return False, "Invalid day (must be 0-6)"
        
        # Conditions Check (for CONDITIONAL)
        if schedule.schedule_type == ScheduleType.CONDITIONAL:
            if not schedule.conditions:
                return False, "Conditions required for conditional schedule"
            
            valid_operators = ['>', '<', '>=', '<=', '==', '!=']
            for condition in schedule.conditions:
                if condition.operator not in valid_operators:
                    return False, f"Invalid operator: {condition.operator}"
        
        # Action Check
        valid_actions = ['allow', 'force_on', 'force_off']
        if schedule.action_in_window not in valid_actions:
            return False, f"Invalid action_in_window: {schedule.action_in_window}"
        if schedule.action_outside_window not in valid_actions:
            return False, f"Invalid action_outside_window: {schedule.action_outside_window}"
        
        # Priority Check
        if schedule.priority_in_window:
            valid_priorities = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'OPTIONAL']
            if schedule.priority_in_window not in valid_priorities:
                return False, f"Invalid priority: {schedule.priority_in_window}"
        
        return True, "Valid"
    
    def get_statistics(self) -> Dict:
        """Hole Statistiken"""
        stats = {
            'total_schedules': len(self.schedules),
            'enabled_schedules': sum(1 for s in self.schedules.values() if s.enabled),
            'by_type': {},
            'by_device': {},
            'devices_with_schedules': len(set(s.device_id for s in self.schedules.values()))
        }
        
        for schedule in self.schedules.values():
            # By Type
            schedule_type = schedule.schedule_type.value
            stats['by_type'][schedule_type] = stats['by_type'].get(schedule_type, 0) + 1
            
            # By Device
            stats['by_device'][schedule.device_id] = stats['by_device'].get(schedule.device_id, 0) + 1
        
        return stats
    
    def export_to_dict(self) -> Dict:
        """Exportiere alle Schedules als Dict"""
        return {
            'schedules': [self._serialize_schedule(s) for s in self.schedules.values()],
            'count': len(self.schedules),
            'exported_at': datetime.now().isoformat()
        }


if __name__ == "__main__":
    # Test
    logging.basicConfig(level=logging.INFO)
    
    print("\n" + "="*60)
    print("EMS Schedule Manager - Test")
    print("="*60)
    
    manager = ScheduleManager()
    
    # Test Schedule erstellen
    test_schedule = Schedule(
        id="test_1",
        name="Waschmaschine 10-14 Uhr",
        device_id="washer_1",
        schedule_type=ScheduleType.TIME_WINDOW,
        time_window=TimeWindow(
            start_time=time(10, 0),
            end_time=time(14, 0),
            days=[0, 1, 2, 3, 4]
        ),
        action_in_window="allow",
        action_outside_window="force_off",
        description="Waschmaschine nur werktags 10-14 Uhr erlauben"
    )
    
    # Validierung
    is_valid, msg = manager.validate_schedule(test_schedule)
    print(f"\nValidation: {is_valid} - {msg}")
    
    # Hinzufügen
    if manager.add_schedule(test_schedule):
        print("✅ Schedule added")
    
    # Statistiken
    stats = manager.get_statistics()
    print(f"\n📊 Statistics:")
    print(f"  Total Schedules: {stats['total_schedules']}")
    print(f"  Enabled: {stats['enabled_schedules']}")
    print(f"  Devices with Schedules: {stats['devices_with_schedules']}")
    
    print("\n" + "="*60)
