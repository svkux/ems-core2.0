#!/usr/bin/env python3
"""
EMS-Core v2.0 - Device Manager
Zentrale Verwaltung für Geräte-Mapping und Konfiguration
"""
import json
import logging
import yaml
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class DeviceConfig:
    """Geräte-Konfiguration"""
    id: str
    name: str
    type: str  # shelly_plug, shelly_1pm, solax, sdm630, etc.
    ip: str
    port: int = 80
    power: float = 0  # Nennleistung in Watt
    priority: str = "MEDIUM"  # CRITICAL, HIGH, MEDIUM, LOW, OPTIONAL
    can_control: bool = True
    min_runtime: int = 0  # Minuten
    enabled: bool = True
    # Zusätzliche Metadaten
    room: str = ""
    category: str = ""  # appliance, heating, ev_charging, etc.
    notes: str = ""
    discovered_at: Optional[str] = None
    last_seen: Optional[str] = None


class DeviceManager:
    """Zentrale Geräte-Verwaltung"""
    
    def __init__(self, 
                 devices_file: str = "config/devices.yaml",
                 mapping_file: str = "config/device_mapping.json"):
        self.devices_file = Path(devices_file)
        self.mapping_file = Path(mapping_file)
        
        self.devices: Dict[str, DeviceConfig] = {}
        self.device_mapping: Dict[str, str] = {}  # IP -> Device ID
        
        self.load_devices()
        self.load_mapping()
    
    def load_devices(self):
        """Lade Geräte aus YAML"""
        try:
            if self.devices_file.exists():
                with open(self.devices_file, 'r') as f:
                    data = yaml.safe_load(f)
                
                for device_data in data.get('devices', []):
                    device = DeviceConfig(**device_data)
                    self.devices[device.id] = device
                    
                logger.info(f"Loaded {len(self.devices)} devices from {self.devices_file}")
            else:
                logger.warning(f"No devices file found at {self.devices_file}")
                self.devices = {}
        except Exception as e:
            logger.error(f"Failed to load devices: {e}")
            self.devices = {}
    
    def save_devices(self):
        """Speichere Geräte als YAML"""
        try:
            self.devices_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert to dict format
            devices_list = []
            for device in self.devices.values():
                device_dict = asdict(device)
                # Remove None values
                device_dict = {k: v for k, v in device_dict.items() if v is not None}
                devices_list.append(device_dict)
            
            data = {'devices': devices_list}
            
            with open(self.devices_file, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(f"Saved {len(self.devices)} devices to {self.devices_file}")
        except Exception as e:
            logger.error(f"Failed to save devices: {e}")
    
    def load_mapping(self):
        """Lade IP -> Device ID Mapping"""
        try:
            if self.mapping_file.exists():
                with open(self.mapping_file, 'r') as f:
                    self.device_mapping = json.load(f)
                logger.info(f"Loaded {len(self.device_mapping)} device mappings")
            else:
                self.device_mapping = {}
        except Exception as e:
            logger.error(f"Failed to load mapping: {e}")
            self.device_mapping = {}
    
    def save_mapping(self):
        """Speichere IP -> Device ID Mapping"""
        try:
            self.mapping_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.mapping_file, 'w') as f:
                json.dump(self.device_mapping, f, indent=2)
            logger.info(f"Saved {len(self.device_mapping)} device mappings")
        except Exception as e:
            logger.error(f"Failed to save mapping: {e}")
    
    def add_device(self, device: DeviceConfig) -> bool:
        """Füge neues Gerät hinzu"""
        try:
            # Prüfe ob ID bereits existiert
            if device.id in self.devices:
                logger.warning(f"Device {device.id} already exists")
                return False
            
            # Setze discovered_at
            if device.discovered_at is None:
                device.discovered_at = datetime.now().isoformat()
            
            device.last_seen = datetime.now().isoformat()
            
            # Speichere Gerät
            self.devices[device.id] = device
            
            # Update Mapping
            if device.ip:
                self.device_mapping[device.ip] = device.id
            
            # Persistiere
            self.save_devices()
            self.save_mapping()
            
            logger.info(f"Added device: {device.name} ({device.id})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add device: {e}")
            return False
    
    def update_device(self, device_id: str, updates: Dict) -> bool:
        """Update Gerät"""
        try:
            if device_id not in self.devices:
                logger.warning(f"Device {device_id} not found")
                return False
            
            device = self.devices[device_id]
            old_ip = device.ip
            
            # Update fields
            for key, value in updates.items():
                if hasattr(device, key):
                    setattr(device, key, value)
            
            device.last_seen = datetime.now().isoformat()
            
            # Update mapping if IP changed
            if 'ip' in updates and updates['ip'] != old_ip:
                if old_ip in self.device_mapping:
                    del self.device_mapping[old_ip]
                self.device_mapping[device.ip] = device_id
            
            self.save_devices()
            self.save_mapping()
            
            logger.info(f"Updated device: {device_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update device: {e}")
            return False
    
    def remove_device(self, device_id: str) -> bool:
        """Entferne Gerät"""
        try:
            if device_id not in self.devices:
                logger.warning(f"Device {device_id} not found")
                return False
            
            device = self.devices[device_id]
            
            # Remove from mapping
            if device.ip in self.device_mapping:
                del self.device_mapping[device.ip]
            
            # Remove device
            del self.devices[device_id]
            
            self.save_devices()
            self.save_mapping()
            
            logger.info(f"Removed device: {device_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove device: {e}")
            return False
    
    def get_device(self, device_id: str) -> Optional[DeviceConfig]:
        """Hole Gerät nach ID"""
        return self.devices.get(device_id)
    
    def get_device_by_ip(self, ip: str) -> Optional[DeviceConfig]:
        """Hole Gerät nach IP"""
        device_id = self.device_mapping.get(ip)
        if device_id:
            return self.devices.get(device_id)
        return None
    
    def get_all_devices(self) -> List[DeviceConfig]:
        """Hole alle Geräte"""
        return list(self.devices.values())
    
    def get_devices_by_type(self, device_type: str) -> List[DeviceConfig]:
        """Hole Geräte nach Typ"""
        return [d for d in self.devices.values() if d.type == device_type]
    
    def get_devices_by_category(self, category: str) -> List[DeviceConfig]:
        """Hole Geräte nach Kategorie"""
        return [d for d in self.devices.values() if d.category == category]
    
    def search_devices(self, query: str) -> List[DeviceConfig]:
        """Suche Geräte (Name, IP, Typ)"""
        query = query.lower()
        results = []
        
        for device in self.devices.values():
            if (query in device.name.lower() or 
                query in device.ip.lower() or 
                query in device.type.lower() or
                query in device.id.lower()):
                results.append(device)
        
        return results
    
    def validate_device(self, device: DeviceConfig) -> tuple[bool, str]:
        """Validiere Geräte-Konfiguration"""
        # ID Check
        if not device.id or len(device.id) < 2:
            return False, "Invalid device ID"
        
        # Name Check
        if not device.name or len(device.name) < 2:
            return False, "Invalid device name"
        
        # IP Check
        if not device.ip:
            return False, "IP address required"
        
        # Type Check
        valid_types = [
            'shelly_plug', 'shelly_1pm', 'shelly_plus_1pm', 'shelly_pro_1pm',
            'shelly_pro_3em', 'solax', 'sdm630', 'sg_ready', 'generic'
        ]
        if device.type not in valid_types:
            return False, f"Invalid device type. Must be one of: {', '.join(valid_types)}"
        
        # Priority Check
        valid_priorities = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'OPTIONAL']
        if device.priority not in valid_priorities:
            return False, f"Invalid priority. Must be one of: {', '.join(valid_priorities)}"
        
        # Power Check
        if device.power < 0:
            return False, "Power must be positive"
        
        return True, "Valid"
    
    def import_discovered_devices(self, discovered: List[Dict]) -> int:
        """
        Importiere entdeckte Geräte
        
        Args:
            discovered: Liste von entdeckten Geräten aus Discovery
            
        Returns:
            Anzahl erfolgreich importierter Geräte
        """
        imported = 0
        
        for disc_device in discovered:
            try:
                # Generiere ID aus IP
                device_id = f"{disc_device['type']}_{disc_device['ip'].replace('.', '_')}"
                
                # Prüfe ob bereits existiert
                if device_id in self.devices:
                    # Update last_seen
                    self.devices[device_id].last_seen = datetime.now().isoformat()
                    continue
                
                # Erstelle neues Gerät
                device = DeviceConfig(
                    id=device_id,
                    name=disc_device.get('name', f"{disc_device['type']} {disc_device['ip']}"),
                    type=disc_device['type'],
                    ip=disc_device['ip'],
                    port=disc_device.get('port', 80),
                    power=0,  # Muss manuell gesetzt werden
                    priority='MEDIUM',
                    discovered_at=datetime.now().isoformat()
                )
                
                if self.add_device(device):
                    imported += 1
                    
            except Exception as e:
                logger.error(f"Failed to import device {disc_device}: {e}")
        
        return imported
    
    def export_to_dict(self) -> Dict:
        """Exportiere alle Geräte als Dict"""
        return {
            'devices': [asdict(d) for d in self.devices.values()],
            'mapping': self.device_mapping,
            'count': len(self.devices),
            'exported_at': datetime.now().isoformat()
        }
    
    def get_statistics(self) -> Dict:
        """Hole Statistiken"""
        stats = {
            'total_devices': len(self.devices),
            'enabled_devices': sum(1 for d in self.devices.values() if d.enabled),
            'controllable_devices': sum(1 for d in self.devices.values() if d.can_control),
            'by_type': {},
            'by_priority': {},
            'by_category': {},
            'total_power': sum(d.power for d in self.devices.values()),
        }
        
        # Count by type
        for device in self.devices.values():
            stats['by_type'][device.type] = stats['by_type'].get(device.type, 0) + 1
            stats['by_priority'][device.priority] = stats['by_priority'].get(device.priority, 0) + 1
            if device.category:
                stats['by_category'][device.category] = stats['by_category'].get(device.category, 0) + 1
        
        return stats


if __name__ == "__main__":
    # Test
    logging.basicConfig(level=logging.INFO)
    
    manager = DeviceManager()
    
    # Test Gerät hinzufügen
    test_device = DeviceConfig(
        id="test_shelly_1",
        name="Test Shelly Plug",
        type="shelly_plug",
        ip="10.0.0.150",
        power=2000,
        priority="MEDIUM",
        room="Kitchen",
        category="appliance"
    )
    
    manager.add_device(test_device)
    
    # Statistiken
    stats = manager.get_statistics()
    print(f"Statistics: {stats}")
    
    # Suche
    results = manager.search_devices("test")
    print(f"Search results: {len(results)}")
