#!/usr/bin/env python3
"""
EMS-Core v2.0 - Scheduler
Zeitbasierte Steuerung von Geräten mit flexiblen Regeln
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime, time
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ScheduleType(Enum):
    """Typen von Zeitplänen"""
    TIME_WINDOW = "time_window"       # Nur zu bestimmten Zeiten
    TIME_BLOCK = "time_block"         # Blockiere zu bestimmten Zeiten
    CONDITIONAL = "conditional"       # Zeit + Bedingung (z.B. PV > 2000W)


class DayOfWeek(Enum):
    """Wochentage"""
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


@dataclass
class TimeWindow:
    """Zeit-Fenster Definition"""
    start_time: time
    end_time: time
    days: List[int]  # Liste von Wochentagen (0=Montag, 6=Sonntag)


@dataclass
class Condition:
    """Bedingung für conditional Schedules"""
    parameter: str      # z.B. "pv_power", "battery_soc", "grid_power"
    operator: str       # ">", "<", ">=", "<=", "==", "!="
    value: float        # Schwellwert


@dataclass
class Schedule:
    """Zeitplan für ein Gerät"""
    id: str
    name: str
    device_id: str
    schedule_type: ScheduleType
    enabled: bool = True
    
    # Time Window/Block
    time_window: Optional[TimeWindow] = None
    
    # Conditional
    conditions: Optional[List[Condition]] = None
    
    # Actions
    action_in_window: str = "allow"     # "allow", "force_on", "force_off"
    action_outside_window: str = "allow"  # "allow", "force_off"
    
    # Priority Override
    override_priority: bool = False     # Überschreibe Device-Priorität?
    priority_in_window: Optional[str] = None
    
    # Metadata
    description: str = ""
    created_at: Optional[str] = None
    last_modified: Optional[str] = None


class Scheduler:
    """
    Scheduler Engine
    
    Hauptaufgaben:
    1. Prüfe ob Device zu aktueller Zeit gesteuert werden darf
    2. Evaluiere Zeit-Fenster
    3. Evaluiere Bedingungen (PV-Power, Battery SOC, etc.)
    4. Gebe Empfehlung zurück (allow, force_on, force_off)
    """
    
    def __init__(self, schedule_manager):
        """
        Args:
            schedule_manager: ScheduleManager Instanz
        """
        self.schedule_manager = schedule_manager
        self.current_energy_data = {}
        
        logger.info("Scheduler initialized")
    
    def update_energy_data(self, energy_data: Dict):
        """
        Update aktuelle Energie-Daten für Conditional Schedules
        
        Args:
            energy_data: Dict mit pv_power, battery_soc, grid_power, etc.
        """
        self.current_energy_data = energy_data
    
    def check_device_schedule(self, 
                             device_id: str, 
                             current_time: Optional[datetime] = None) -> Dict:
        """
        Prüfe alle Schedules für ein Device
        
        Args:
            device_id: Device ID
            current_time: Aktuelle Zeit (default: now)
            
        Returns:
            Dict mit Scheduler-Entscheidung:
            {
                'allowed': bool,
                'action': 'allow' | 'force_on' | 'force_off',
                'reason': str,
                'schedule_id': str or None,
                'override_priority': bool,
                'priority': str or None
            }
        """
        if current_time is None:
            current_time = datetime.now()
        
        # Hole alle aktiven Schedules für dieses Device
        schedules = self.schedule_manager.get_schedules_by_device(device_id)
        active_schedules = [s for s in schedules if s.enabled]
        
        if not active_schedules:
            # Keine Schedules -> erlaubt
            return {
                'allowed': True,
                'action': 'allow',
                'reason': 'No schedules defined',
                'schedule_id': None,
                'override_priority': False,
                'priority': None
            }
        
        # Evaluiere alle Schedules (höchste Priorität gewinnt)
        # Reihenfolge: BLOCK > FORCE_OFF > FORCE_ON > ALLOW
        
        decisions = []
        
        for schedule in active_schedules:
            decision = self._evaluate_schedule(schedule, current_time)
            if decision:
                decisions.append(decision)
        
        # Wenn keine Entscheidung getroffen wurde
        if not decisions:
            return {
                'allowed': True,
                'action': 'allow',
                'reason': 'No matching schedules',
                'schedule_id': None,
                'override_priority': False,
                'priority': None
            }
        
        # Sortiere nach Priorität (force_off > force_on > allow)
        priority_order = {'force_off': 0, 'force_on': 1, 'allow': 2}
        decisions.sort(key=lambda d: priority_order.get(d['action'], 99))
        
        # Höchste Priorität gewinnt
        return decisions[0]
    
    def _evaluate_schedule(self, 
                          schedule: Schedule, 
                          current_time: datetime) -> Optional[Dict]:
        """
        Evaluiere einen einzelnen Schedule
        
        Returns:
            Decision dict oder None wenn Schedule nicht zutrifft
        """
        if schedule.schedule_type == ScheduleType.TIME_WINDOW:
            return self._evaluate_time_window(schedule, current_time)
        
        elif schedule.schedule_type == ScheduleType.TIME_BLOCK:
            return self._evaluate_time_block(schedule, current_time)
        
        elif schedule.schedule_type == ScheduleType.CONDITIONAL:
            return self._evaluate_conditional(schedule, current_time)
        
        return None
    
    def _evaluate_time_window(self, 
                             schedule: Schedule, 
                             current_time: datetime) -> Optional[Dict]:
        """
        Evaluiere TIME_WINDOW Schedule
        
        Erlaubt Steuerung nur innerhalb des Zeit-Fensters
        """
        if not schedule.time_window:
            logger.warning(f"Schedule {schedule.id} has no time_window defined")
            return None
        
        in_window = self._is_in_time_window(schedule.time_window, current_time)
        
        if in_window:
            # Innerhalb des Fensters
            return {
                'allowed': schedule.action_in_window != 'force_off',
                'action': schedule.action_in_window,
                'reason': f"Schedule '{schedule.name}' - inside time window",
                'schedule_id': schedule.id,
                'override_priority': schedule.override_priority,
                'priority': schedule.priority_in_window
            }
        else:
            # Außerhalb des Fensters
            return {
                'allowed': schedule.action_outside_window != 'force_off',
                'action': schedule.action_outside_window,
                'reason': f"Schedule '{schedule.name}' - outside time window",
                'schedule_id': schedule.id,
                'override_priority': False,
                'priority': None
            }
    
    def _evaluate_time_block(self, 
                            schedule: Schedule, 
                            current_time: datetime) -> Optional[Dict]:
        """
        Evaluiere TIME_BLOCK Schedule
        
        Blockiert Steuerung innerhalb des Zeit-Fensters
        """
        if not schedule.time_window:
            logger.warning(f"Schedule {schedule.id} has no time_window defined")
            return None
        
        in_window = self._is_in_time_window(schedule.time_window, current_time)
        
        if in_window:
            # Innerhalb des Block-Fensters -> force_off
            return {
                'allowed': False,
                'action': 'force_off',
                'reason': f"Schedule '{schedule.name}' - blocked by time block",
                'schedule_id': schedule.id,
                'override_priority': True,
                'priority': None
            }
        
        # Außerhalb des Blocks -> normal
        return None
    
    def _evaluate_conditional(self, 
                             schedule: Schedule, 
                             current_time: datetime) -> Optional[Dict]:
        """
        Evaluiere CONDITIONAL Schedule
        
        Zeit-Fenster UND Bedingungen müssen erfüllt sein
        """
        if not schedule.time_window:
            logger.warning(f"Schedule {schedule.id} has no time_window defined")
            return None
        
        # Prüfe Zeit-Fenster
        in_window = self._is_in_time_window(schedule.time_window, current_time)
        
        if not in_window:
            # Außerhalb des Fensters
            return {
                'allowed': schedule.action_outside_window != 'force_off',
                'action': schedule.action_outside_window,
                'reason': f"Schedule '{schedule.name}' - outside time window",
                'schedule_id': schedule.id,
                'override_priority': False,
                'priority': None
            }
        
        # Innerhalb des Fensters -> prüfe Bedingungen
        if schedule.conditions:
            conditions_met = self._check_conditions(schedule.conditions)
            
            if conditions_met:
                return {
                    'allowed': schedule.action_in_window != 'force_off',
                    'action': schedule.action_in_window,
                    'reason': f"Schedule '{schedule.name}' - time + conditions met",
                    'schedule_id': schedule.id,
                    'override_priority': schedule.override_priority,
                    'priority': schedule.priority_in_window
                }
            else:
                return {
                    'allowed': False,
                    'action': 'force_off',
                    'reason': f"Schedule '{schedule.name}' - conditions not met",
                    'schedule_id': schedule.id,
                    'override_priority': False,
                    'priority': None
                }
        
        # Keine Bedingungen -> nur Zeit-Fenster zählt
        return {
            'allowed': schedule.action_in_window != 'force_off',
            'action': schedule.action_in_window,
            'reason': f"Schedule '{schedule.name}' - inside time window",
            'schedule_id': schedule.id,
            'override_priority': schedule.override_priority,
            'priority': schedule.priority_in_window
        }
    
    def _is_in_time_window(self, 
                          time_window: TimeWindow, 
                          current_time: datetime) -> bool:
        """
        Prüfe ob current_time innerhalb des TimeWindow liegt
        """
        # Prüfe Wochentag
        weekday = current_time.weekday()
        if weekday not in time_window.days:
            return False
        
        # Prüfe Zeit
        current_time_only = current_time.time()
        
        # Handle Overnight Windows (z.B. 22:00 - 06:00)
        if time_window.start_time > time_window.end_time:
            # Overnight: Entweder nach start ODER vor end
            return (current_time_only >= time_window.start_time or 
                   current_time_only <= time_window.end_time)
        else:
            # Normal: Zwischen start und end
            return (time_window.start_time <= current_time_only <= time_window.end_time)
    
    def _check_conditions(self, conditions: List[Condition]) -> bool:
        """
        Prüfe ob alle Bedingungen erfüllt sind
        
        Returns:
            True wenn ALLE Bedingungen erfüllt (AND-Verknüpfung)
        """
        if not self.current_energy_data:
            logger.warning("No energy data available for condition check")
            return False
        
        for condition in conditions:
            if not self._check_single_condition(condition):
                return False
        
        return True
    
    def _check_single_condition(self, condition: Condition) -> bool:
        """Prüfe eine einzelne Bedingung"""
        # Hole Wert aus Energy Data
        current_value = self.current_energy_data.get(condition.parameter)
        
        if current_value is None:
            logger.warning(f"Parameter {condition.parameter} not found in energy data")
            return False
        
        # Evaluiere Operator
        try:
            if condition.operator == '>':
                return current_value > condition.value
            elif condition.operator == '<':
                return current_value < condition.value
            elif condition.operator == '>=':
                return current_value >= condition.value
            elif condition.operator == '<=':
                return current_value <= condition.value
            elif condition.operator == '==':
                return abs(current_value - condition.value) < 0.01  # Float comparison
            elif condition.operator == '!=':
                return abs(current_value - condition.value) >= 0.01
            else:
                logger.error(f"Unknown operator: {condition.operator}")
                return False
        except Exception as e:
            logger.error(f"Error evaluating condition: {e}")
            return False
    
    def get_all_active_schedules(self, current_time: Optional[datetime] = None) -> List[Dict]:
        """
        Hole alle aktiven Schedules mit ihrem aktuellen Status
        
        Returns:
            Liste von dicts mit schedule info und status
        """
        if current_time is None:
            current_time = datetime.now()
        
        result = []
        
        for schedule in self.schedule_manager.get_all_schedules():
            if not schedule.enabled:
                continue
            
            decision = self._evaluate_schedule(schedule, current_time)
            
            status = {
                'schedule': schedule,
                'decision': decision,
                'in_window': self._is_in_time_window(schedule.time_window, current_time) if schedule.time_window else False
            }
            
            result.append(status)
        
        return result


if __name__ == "__main__":
    # Test
    logging.basicConfig(level=logging.INFO)
    
    print("\n" + "="*60)
    print("EMS Scheduler - Test")
    print("="*60)
    
    # Test Time Window
    from datetime import time
    
    window = TimeWindow(
        start_time=time(10, 0),
        end_time=time(14, 0),
        days=[0, 1, 2, 3, 4]  # Mo-Fr
    )
    
    schedule = Schedule(
        id="test_1",
        name="Waschmaschine 10-14 Uhr",
        device_id="washer_1",
        schedule_type=ScheduleType.TIME_WINDOW,
        time_window=window,
        action_in_window="allow",
        action_outside_window="force_off"
    )
    
    # Mock Schedule Manager
    class MockScheduleManager:
        def __init__(self):
            self.schedules = [schedule]
        
        def get_schedules_by_device(self, device_id):
            return [s for s in self.schedules if s.device_id == device_id]
        
        def get_all_schedules(self):
            return self.schedules
    
    manager = MockScheduleManager()
    scheduler = Scheduler(manager)
    
    # Test verschiedene Zeiten
    test_times = [
        datetime(2026, 1, 27, 9, 0),   # 09:00 - Vor Fenster
        datetime(2026, 1, 27, 12, 0),  # 12:00 - In Fenster
        datetime(2026, 1, 27, 15, 0),  # 15:00 - Nach Fenster
    ]
    
    for test_time in test_times:
        decision = scheduler.check_device_schedule("washer_1", test_time)
        print(f"\n{test_time.strftime('%H:%M')}:")
        print(f"  Allowed: {decision['allowed']}")
        print(f"  Action: {decision['action']}")
        print(f"  Reason: {decision['reason']}")
    
    print("\n" + "="*60)
