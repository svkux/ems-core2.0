"""
EMS-Core v2.0 - Prioritizer
Intelligente Priorisierung von Verbrauchern
"""
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class Priority(Enum):
    """Prioritäts-Stufen"""
    CRITICAL = 0
    HIGH = 1
    MEDIUM = 2
    LOW = 3
    OPTIONAL = 4


@dataclass
class Device:
    """Geräte-Definition"""
    id: str
    name: str
    power: float
    priority: Priority
    is_on: bool = False
    can_control: bool = True
    scheduled: bool = False
    manual_override: bool = False
    min_runtime: int = 0
    current_runtime: int = 0
    
    def __lt__(self, other):
        return self.priority.value < other.priority.value


class Prioritizer:
    """Priorisierungs-Engine"""
    
    def __init__(self):
        self.devices: Dict[str, Device] = {}
        self.priority_order: List[str] = []
        self.hysteresis = 100
        
    def add_device(self, device: Device):
        """Füge Gerät hinzu"""
        self.devices[device.id] = device
        if device.id not in self.priority_order:
            self.priority_order.append(device.id)
        logger.info(f"Added device: {device.name}")
    
    def calculate_switching_plan(self, available_power: float, **kwargs) -> Dict[str, bool]:
        """Berechne optimale Schaltung"""
        plan = {}
        remaining_power = available_power
        
        sorted_devices = self._get_sorted_devices()
        
        # Phase 1: CRITICAL
        for device in sorted_devices:
            if device.priority == Priority.CRITICAL:
                plan[device.id] = True
                if not device.is_on:
                    remaining_power -= device.power
        
        # Phase 2: SCHEDULED
        for device in sorted_devices:
            if device.scheduled and device.priority != Priority.CRITICAL:
                if remaining_power >= device.power + self.hysteresis:
                    plan[device.id] = True
                    remaining_power -= device.power
                else:
                    plan[device.id] = False
        
        # Phase 3: Priorisiert
        for device in sorted_devices:
            if device.id in plan:
                continue
            
            if device.manual_override:
                plan[device.id] = device.is_on
                continue
            
            if not device.can_control:
                plan[device.id] = device.is_on
                continue
            
            if remaining_power >= device.power + self.hysteresis:
                plan[device.id] = True
                remaining_power -= device.power
            else:
                if device.is_on and device.current_runtime < device.min_runtime:
                    plan[device.id] = True
                else:
                    plan[device.id] = False
        
        return plan
    
    def _get_sorted_devices(self) -> List[Device]:
        """Hole sortierte Geräte"""
        devices_list = list(self.devices.values())
        order_map = {id: i for i, id in enumerate(self.priority_order)}
        devices_list.sort(key=lambda d: (d.priority.value, order_map.get(d.id, 999)))
        return devices_list
