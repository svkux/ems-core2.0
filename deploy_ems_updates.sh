#!/bin/bash
################################################################################
# EMS-Core v2.0 - Automatisches Deployment Script
# Erstellt alle neuen Ordner und Dateien
################################################################################

set -e  # Stop bei Fehler

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging Funktionen
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Header
echo "============================================================================"
echo "  EMS-Core v2.0 - Automatisches Deployment"
echo "============================================================================"
echo ""

# Prüfe ob im richtigen Verzeichnis
if [ ! -f "PROJECT.md" ]; then
    log_error "Bitte führe dieses Script im ems-core2.0 Hauptverzeichnis aus!"
    exit 1
fi

EMS_DIR=$(pwd)
log_info "EMS Directory: $EMS_DIR"

# Backup erstellen
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
log_info "Erstelle Backup in: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"

# Backup von existierenden Dateien
for file in core/main.py config/settings.yaml config/devices.yaml README.md; do
    if [ -f "$file" ]; then
        cp "$file" "$BACKUP_DIR/" 2>/dev/null || true
    fi
done
log_success "Backup erstellt"

################################################################################
# 1. Ordner erstellen
################################################################################
log_info "Erstelle Ordnerstruktur..."

mkdir -p core/optimizer
mkdir -p logs
mkdir -p config

log_success "Ordner erstellt"

################################################################################
# 2. core/optimizer/__init__.py
################################################################################
log_info "Erstelle core/optimizer/__init__.py..."

cat > core/optimizer/__init__.py << 'EOF'
"""EMS Optimizer Module"""
from .scheduler import Scheduler
from .prioritizer import Prioritizer, Device, Priority

__all__ = ['Scheduler', 'Prioritizer', 'Device', 'Priority']
EOF

log_success "core/optimizer/__init__.py erstellt"

################################################################################
# 3. core/optimizer/scheduler.py
################################################################################
log_info "Erstelle core/optimizer/scheduler.py..."

cat > core/optimizer/scheduler.py << 'SCHEDULER_EOF'
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
SCHEDULER_EOF

log_success "core/optimizer/scheduler.py erstellt"

################################################################################
# 4. core/optimizer/prioritizer.py
################################################################################
log_info "Erstelle core/optimizer/prioritizer.py..."

cat > core/optimizer/prioritizer.py << 'PRIORITIZER_EOF'
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
PRIORITIZER_EOF

log_success "core/optimizer/prioritizer.py erstellt"

################################################################################
# 5. core/main.py
################################################################################
log_info "Erstelle core/main.py..."

cat > core/main.py << 'MAIN_EOF'
#!/usr/bin/env python3
"""
EMS-Core v2.0 - Main Optimizer
Hauptsteuerung des Energie-Management-Systems
"""
import asyncio
import logging
import signal
from pathlib import Path
from typing import Dict, Optional

import yaml

from core.optimizer.scheduler import Scheduler
from core.optimizer.prioritizer import Prioritizer, Device, Priority

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EMSCore:
    """Haupt-Energie-Management-System"""
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        self.config_path = Path(config_path)
        self.config = self.load_config()
        self.running = False
        
        self.scheduler = Scheduler("config/schedules.json")
        self.prioritizer = Prioritizer()
        
        self.controllers = {}
        
        self.energy_data = {
            'pv_power': 0.0,
            'battery_power': 0.0,
            'battery_soc': 0.0,
            'grid_power': 0.0,
            'available_power': 0.0
        }
        
    def load_config(self) -> Dict:
        """Lade Konfiguration"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    return yaml.safe_load(f)
            else:
                logger.warning("Config not found, using defaults")
                return self.get_default_config()
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict:
        """Standard-Konfiguration"""
        return {
            'optimization_interval': 30,
            'hysteresis': 100,
            'battery': {
                'min_soc': 20,
                'max_soc': 95,
                'priority_soc': 50
            }
        }
    
    async def initialize(self):
        """Initialisiere System"""
        logger.info("Initializing EMS-Core v2.0...")
        await self.load_devices()
        logger.info("EMS-Core initialized")
    
    async def load_devices(self):
        """Lade Geräte"""
        devices_path = Path("config/devices.yaml")
        try:
            if devices_path.exists():
                with open(devices_path, 'r') as f:
                    devices_config = yaml.safe_load(f)
                
                for device_cfg in devices_config.get('devices', []):
                    device = Device(
                        id=device_cfg['id'],
                        name=device_cfg['name'],
                        power=device_cfg.get('power', 0),
                        priority=Priority[device_cfg.get('priority', 'MEDIUM')],
                        can_control=device_cfg.get('can_control', True),
                        min_runtime=device_cfg.get('min_runtime', 0)
                    )
                    self.prioritizer.add_device(device)
                
                logger.info(f"Loaded {len(devices_config.get('devices', []))} devices")
        except Exception as e:
            logger.error(f"Failed to load devices: {e}")
    
    async def optimize(self):
        """Führe Optimierung durch"""
        try:
            # Update scheduled status
            for device_id in self.prioritizer.devices:
                is_scheduled = self.scheduler.is_in_schedule(device_id)
                self.prioritizer.devices[device_id].scheduled = is_scheduled
            
            # Calculate plan
            plan = self.prioritizer.calculate_switching_plan(
                available_power=self.energy_data['available_power']
            )
            
            logger.info(f"Optimization: {sum(plan.values())}/{len(plan)} devices ON")
            
        except Exception as e:
            logger.error(f"Optimization failed: {e}")
    
    async def run(self):
        """Hauptschleife"""
        self.running = True
        interval = self.config['optimization_interval']
        
        logger.info(f"Starting optimization loop (interval: {interval}s)")
        
        while self.running:
            try:
                await self.optimize()
                await asyncio.sleep(interval)
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(interval)
    
    async def shutdown(self):
        """Beende System"""
        logger.info("Shutting down EMS-Core...")
        self.running = False


async def main():
    """Haupt-Funktion"""
    ems = EMSCore()
    
    def signal_handler(sig, frame):
        logger.info(f"Received signal {sig}")
        asyncio.create_task(ems.shutdown())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await ems.initialize()
        await ems.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        await ems.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
MAIN_EOF

chmod +x core/main.py
log_success "core/main.py erstellt"

################################################################################
# 6. config/settings.yaml
################################################################################
log_info "Erstelle config/settings.yaml..."

cat > config/settings.yaml << 'SETTINGS_EOF'
# EMS-Core v2.0 - Haupt-Konfiguration
optimization_interval: 30  # Sekunden
hysteresis: 100  # Watt

battery:
  min_soc: 20
  max_soc: 95
  priority_soc: 50

grid:
  max_import: 10000
  max_export: 0

# Solax Wechselrichter
solax:
  ip: "10.0.0.100"
  port: 502
  unit_id: 1

# SDM630 Smartmeter
sdm630:
  ip: "10.0.0.101"
  port: 502
  unit_id: 1

# SG-Ready
sg_ready:
  enabled: false
  device_id: "heatpump"
  relay1_id: "shelly_sg_relay1"
  relay2_id: "shelly_sg_relay2"

logging:
  level: INFO
  file: logs/ems.log
SETTINGS_EOF

log_success "config/settings.yaml erstellt"

################################################################################
# 7. config/devices.yaml
################################################################################
log_info "Erstelle config/devices.yaml..."

cat > config/devices.yaml << 'DEVICES_EOF'
# EMS-Core v2.0 - Geräte-Konfiguration
devices:
  - id: "fridge"
    name: "Kühlschrank"
    type: "shelly_plug"
    ip: "10.0.0.150"
    power: 150
    priority: "CRITICAL"
    can_control: false
  
  - id: "heater"
    name: "Heizstab"
    type: "shelly_1pm"
    ip: "10.0.0.151"
    power: 3000
    priority: "MEDIUM"
    can_control: true
    min_runtime: 30
  
  - id: "washer"
    name: "Waschmaschine"
    type: "shelly_plug"
    ip: "10.0.0.152"
    power: 2000
    priority: "LOW"
    can_control: true
DEVICES_EOF

log_success "config/devices.yaml erstellt"

################################################################################
# 8. config/schedules.json
################################################################################
log_info "Erstelle config/schedules.json..."

cat > config/schedules.json << 'SCHEDULES_EOF'
{
  "heater": {
    "device_id": "heater",
    "enabled": true,
    "schedule": {
      "monday": [[10, 14], [20, 22]],
      "tuesday": [[10, 14], [20, 22]],
      "wednesday": [[10, 14], [20, 22]],
      "thursday": [[10, 14], [20, 22]],
      "friday": [[10, 14], [20, 22]],
      "saturday": [[8, 22]],
      "sunday": [[8, 22]]
    }
  }
}
SCHEDULES_EOF

log_success "config/schedules.json erstellt"

################################################################################
# 9. config/priorities.json
################################################################################
log_info "Erstelle config/priorities.json..."

cat > config/priorities.json << 'PRIORITIES_EOF'
{
  "order": [
    "fridge",
    "heater",
    "washer"
  ],
  "last_updated": "2025-01-18T12:00:00"
}
PRIORITIES_EOF

log_success "config/priorities.json erstellt"

################################################################################
# 10. test_ems_system.py
################################################################################
log_info "Erstelle test_ems_system.py..."

cat > test_ems_system.py << 'TEST_EOF'
#!/usr/bin/env python3
"""
EMS-Core v2.0 - System Test
"""
import logging
from datetime import datetime

from core.optimizer.scheduler import Scheduler
from core.optimizer.prioritizer import Prioritizer, Device, Priority

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_scheduler():
    """Test Scheduler"""
    scheduler = Scheduler("config/schedules.json")
    
    schedule = {
        "monday": [[10, 14]]
    }
    scheduler.add_schedule("test_device", schedule)
    
    # Test Montag 12:00
    test_time = datetime(2025, 1, 20, 12, 0)
    result = scheduler.is_in_schedule("test_device", test_time)
    
    logger.info(f"✓ Scheduler Test: {result}")
    return result


def test_prioritizer():
    """Test Prioritizer"""
    prioritizer = Prioritizer()
    
    devices = [
        Device("critical", "Critical", 150, Priority.CRITICAL),
        Device("high", "High", 2000, Priority.HIGH),
        Device("low", "Low", 2000, Priority.LOW),
    ]
    
    for device in devices:
        prioritizer.add_device(device)
    
    plan = prioritizer.calculate_switching_plan(5000)
    
    logger.info(f"✓ Prioritizer Test: {sum(plan.values())}/{len(plan)} devices ON")
    return len(plan) == 3


if __name__ == "__main__":
    logger.info("="*70)
    logger.info("EMS-Core v2.0 - Quick Test")
    logger.info("="*70)
    
    test1 = test_scheduler()
    test2 = test_prioritizer()
    
    if test1 and test2:
        logger.info("\n✓ ALL TESTS PASSED!")
    else:
        logger.warning("\n✗ SOME TESTS FAILED!")
TEST_EOF

chmod +x test_ems_system.py
log_success "test_ems_system.py erstellt"

################################################################################
# 11. ems-core.service
################################################################################
log_info "Erstelle ems-core.service..."

cat > ems-core.service << 'SERVICE_EOF'
[Unit]
Description=EMS-Core v2.0 - Energy Management System
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/ems-core2.0
ExecStart=/opt/ems-core2.0/venv/bin/python3 /opt/ems-core2.0/core/main.py
Restart=on-failure
RestartSec=10s
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SERVICE_EOF

log_success "ems-core.service erstellt"

################################################################################
# 12. README.md
################################################################################
log_info "Erstelle README.md..."

cat > README.md << 'README_EOF'
# EMS-Core v2.0

🔋 Intelligentes Energie-Management-System

## Quick Start

```bash
# Installation
sudo ./install_ems_complete.sh

# Test
python3 test_ems_system.py

# Start
python3 core/main.py
```

## Features

- ✅ Automatische Geräte-Erkennung
- ✅ Intelligente Priorisierung
- ✅ Zeitplan-Management
- ✅ Batterie-Integration
- ✅ SG-Ready Steuerung
- ✅ Web UI (Port 8080)

## Konfiguration

Siehe `config/` Ordner:
- `settings.yaml` - System-Einstellungen
- `devices.yaml` - Geräte-Konfiguration
- `schedules.json` - Zeitpläne

## Dokumentation

Vollständige Dokumentation: https://github.com/svkux/ems-core2.0

## Support

GitHub Issues: https://github.com/svkux/ems-core2.0/issues
README_EOF

log_success "README.md erstellt"

################################################################################
# 13. .gitignore aktualisieren
################################################################################
log_info "Aktualisiere .gitignore..."

cat >> .gitignore << 'GITIGNORE_EOF'

# EMS-Core
logs/*.log
backup_*/
*.pyc
__pycache__/
GITIGNORE_EOF

log_success ".gitignore aktualisiert"

################################################################################
# Finale Schritte
################################################################################
log_info "Setze Berechtigungen..."

chmod +x core/main.py
chmod +x test_ems_system.py
chmod 644 config/*.yaml
chmod 644 config/*.json

log_success "Berechtigungen gesetzt"

################################################################################
# Zusammenfassung
################################################################################
echo ""
echo "============================================================================"
log_success "Deployment abgeschlossen!"
echo "============================================================================"
echo ""
echo "Erstellte Dateien:"
echo "  ✓ core/main.py"
echo "  ✓ core/optimizer/__init__.py"
echo "  ✓ core/optimizer/scheduler.py"
echo "  ✓ core/optimizer/prioritizer.py"
echo "  ✓ config/settings.yaml"
echo "  ✓ config/devices.yaml"
echo "  ✓ config/schedules.json"
echo "  ✓ config/priorities.json"
echo "  ✓ test_ems_system.py"
echo "  ✓ ems-core.service"
echo "  ✓ README.md"
echo ""
echo "Backup erstellt in: $BACKUP_DIR"
echo ""
echo "Nächste Schritte:"
echo "  1. Konfiguration anpassen: nano config/settings.yaml"
echo "  2. Geräte anpassen: nano config/devices.yaml"
echo "  3. Test ausführen: python3 test_ems_system.py"
echo "  4. System starten: python3 core/main.py"
echo ""
echo "Service installieren:"
echo "  sudo cp ems-core.service /etc/systemd/system/"
echo "  sudo systemctl daemon-reload"
echo "  sudo systemctl enable ems-core"
echo "  sudo systemctl start ems-core"
echo ""
log_info "Fertig!"
