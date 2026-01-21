# EMS-Core v2.0 - Development Documentation

## 🏗️ Projekt-Status (Stand: 2025-01-19)

### ✅ Implementiert

#### Core Module
- ✅ **DeviceManager** (`core/device_manager.py`)
  - Zentrale Geräte-Verwaltung
  - YAML/JSON Persistierung
  - IP-Mapping
  - Validierung
  - Import/Export

- ✅ **Scheduler** (`core/optimizer/scheduler.py`)
  - Wochentags-basierte Zeitpläne
  - Zeitfenster-Management
  - Enable/Disable pro Gerät
  - JSON-Persistierung

- ✅ **Prioritizer** (`core/optimizer/prioritizer.py`)
  - 5 Prioritätsstufen (CRITICAL, HIGH, MEDIUM, LOW, OPTIONAL)
  - User-definierte Reihenfolge
  - Switching Plan Berechnung
  - Mindestlaufzeit-Respektierung
  - Manuelle Überschreibung

- ✅ **Main Optimizer** (`core/main.py`)
  - Haupt-Event-Loop
  - Controller-Integration
  - Energie-Daten Aggregation
  - SG-Ready Steuerung
  - Systemd-ready

#### Controller
- ✅ **ShellyController** (Gen1/2/Plus/Pro)
- ✅ **SolaxModbusController** (PV + Battery)
- ✅ **SDM630ModbusController** (Smartmeter)
- ✅ **SGReadyController** (Wärmepumpen)
- ✅ **ShellyProEM3Controller** (3-Phasen Messung)

#### Web UI
- ✅ **Device Management** (`webui/templates/devices.html`)
  - Add/Edit/Delete Geräte
  - Suche & Filter
  - Statistiken
  - Responsive Design

- ✅ **API Endpoints** (`webui/api_routes.py`)
  - REST API für alle Operationen
  - Device CRUD
  - Discovery Integration
  - Statistics

- ✅ **Flask App** (`webui/app.py`)
  - Blueprint-System
  - Error Handling
  - Health Check

---

## 📁 Projekt-Struktur

```
ems-core2.0/
├── core/
│   ├── __init__.py
│   ├── main.py                    # Haupt-Optimizer
│   ├── device_manager.py          # Device Management
│   │
│   ├── optimizer/
│   │   ├── __init__.py
│   │   ├── scheduler.py           # Zeitpläne
│   │   └── prioritizer.py         # Priorisierung
│   │
│   ├── controllers/
│   │   ├── __init__.py
│   │   ├── shelly.py              # Shelly Devices
│   │   ├── solax.py               # Solax Inverter
│   │   ├── sdm630.py              # SDM630 Meter
│   │   └── sg_ready.py            # SG-Ready
│   │
│   └── integrations/
│       ├── __init__.py
│       └── discovery.py           # Network Discovery
│
├── webui/
│   ├── app.py                     # Flask App
│   ├── api_routes.py              # REST API
│   │
│   ├── templates/
│   │   ├── index.html             # Dashboard
│   │   ├── devices.html           # Device Management
│   │   ├── discovery.html         # Discovery
│   │   ├── priorities.html        # Priorities
│   │   └── schedules.html         # Schedules
│   │
│   └── static/
│       ├── css/
│       └── js/
│
├── config/
│   ├── settings.yaml              # System Config
│   ├── devices.yaml               # Device Config
│   ├── schedules.json             # Zeitpläne
│   ├── priorities.json            # Priority Order
│   └── device_mapping.json        # IP Mapping
│
├── logs/                          # Log Files
│
├── tests/
│   └── test_ems_system.py         # System Tests
│
├── deploy_ems_updates.sh          # Deployment Script
├── update_github.sh               # GitHub Sync
├── ems-core.service               # Systemd Service
├── requirements.txt
├── README.md
├── DEVELOPMENT.md                 # This file
└── CHANGELOG.md
```

---

## 🔧 Development Workflow

### Setup Development Environment

```bash
# Clone Repository
git clone https://github.com/svkux/ems-core2.0.git
cd ems-core2.0

# Virtual Environment
python3 -m venv venv
source venv/bin/activate

# Install Dependencies
pip install -r requirements.txt

# Install Dev Dependencies
pip install pytest pytest-asyncio black flake8
```

### Run Tests

```bash
# Quick Test
python3 test_ems_system.py

# Full Test Suite (wenn pytest installiert)
pytest tests/ -v

# Test einzelnes Modul
python3 -m pytest tests/test_scheduler.py
```

### Run Development Server

```bash
# Main Optimizer (Vordergrund)
python3 core/main.py

# Web UI (Vordergrund)
python3 webui/app.py

# Mit Debug Logging
LOG_LEVEL=DEBUG python3 core/main.py
```

---

## 🎯 Coding Standards

### Python Style Guide

- **PEP 8** für Code-Formatierung
- **Type Hints** wo möglich
- **Docstrings** für alle Module/Klassen/Funktionen
- **Async/Await** für I/O Operationen

### Beispiel:

```python
async def control_device(device_id: str, state: bool) -> bool:
    """
    Steuere Gerät
    
    Args:
        device_id: Eindeutige Geräte-ID
        state: True = ON, False = OFF
        
    Returns:
        True wenn erfolgreich
        
    Raises:
        DeviceNotFoundError: Wenn Gerät nicht existiert
    """
    device = self.get_device(device_id)
    if not device:
        raise DeviceNotFoundError(f"Device {device_id} not found")
    
    # Implementation...
    return True
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

# Levels verwenden:
logger.debug("Detailed debug info")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred")
logger.critical("Critical error")
```

---

## 🔌 API Dokumentation

### Device Management API

#### `GET /api/devices`
Hole alle Geräte

**Response:**
```json
{
  "success": true,
  "devices": [...],
  "count": 5
}
```

#### `POST /api/devices`
Erstelle neues Gerät

**Request:**
```json
{
  "id": "heater_1",
  "name": "Heizstab",
  "type": "shelly_1pm",
  "ip": "10.0.0.150",
  "power": 3000,
  "priority": "MEDIUM"
}
```

#### `PUT /api/devices/{id}`
Update Gerät

#### `DELETE /api/devices/{id}`
Lösche Gerät

#### `POST /api/devices/discover`
Starte Discovery

#### `GET /api/devices/stats`
Hole Statistiken

Vollständige API-Docs: siehe `webui/api_routes.py`

---

## 🧪 Testing

### Unit Tests

```python
import pytest
from core.optimizer.scheduler import Scheduler

def test_scheduler_add():
    scheduler = Scheduler("test_schedules.json")
    schedule = {"monday": [[10, 14]]}
    
    scheduler.add_schedule("test", schedule)
    
    assert "test" in scheduler.schedules
```

### Integration Tests

```python
import pytest
from core.device_manager import DeviceManager, DeviceConfig

@pytest.mark.asyncio
async def test_device_lifecycle():
    manager = DeviceManager()
    
    device = DeviceConfig(
        id="test_1",
        name="Test Device",
        type="shelly_plug",
        ip="10.0.0.150",
        power=1000
    )
    
    # Add
    assert manager.add_device(device) == True
    
    # Get
    retrieved = manager.get_device("test_1")
    assert retrieved.name == "Test Device"
    
    # Update
    manager.update_device("test_1", {"power": 2000})
    assert manager.get_device("test_1").power == 2000
    
    # Delete
    assert manager.remove_device("test_1") == True
```

---

## 🚀 Deployment

### Lokaler Test-Deploy

```bash
./deploy_ems_updates.sh
```

### Production Deploy

```bash
# 1. Update Code
git pull

# 2. Update Dependencies
pip install -r requirements.txt

# 3. Restart Service
sudo systemctl restart ems-core
sudo systemctl restart ems-webui

# 4. Check Status
sudo systemctl status ems-core
sudo journalctl -u ems-core -f
```

---

## 📝 Git Workflow

### Branch Strategy

- `main` - Production-ready code
- `develop` - Development branch
- `feature/*` - Feature branches
- `bugfix/*` - Bugfix branches

### Commit Messages

Format: `type(scope): message`

Types:
- `feat`: Neues Feature
- `fix`: Bugfix
- `docs`: Dokumentation
- `refactor`: Code Refactoring
- `test`: Tests
- `chore`: Maintenance

Beispiele:
```bash
git commit -m "feat(device): Add device mapping functionality"
git commit -m "fix(scheduler): Fix timezone handling"
git commit -m "docs(api): Update API documentation"
```

### GitHub Sync

```bash
# Automatisch
./update_github.sh

# Manuell
git add .
git commit -m "Your message"
git push origin main
```

---

## 🐛 Debugging

### Enable Debug Logging

```python
# In core/main.py
logging.basicConfig(level=logging.DEBUG)
```

### Common Issues

**Problem: Geräte werden nicht erkannt**
```bash
# Check Discovery
python3 -c "from core.integrations.discovery import DeviceDiscovery; d = DeviceDiscovery(); print(d.scan_network('10.0.0.0/24'))"
```

**Problem: Controller-Fehler**
```bash
# Test Controller direkt
python3 << EOF
import asyncio
from core.controllers.shelly import ShellyController

async def test():
    shelly = ShellyController("10.0.0.150")
    print(await shelly.get_status())

asyncio.run(test())
EOF
```

---

## 🔮 Roadmap

### Phase 1 (Current)
- ✅ Device Manager
- ✅ Basic Web UI
- ✅ Core Optimizer
- ⏳ Testing & Bugfixes

### Phase 2 (Next)
- [ ] Advanced Scheduling (Wettervorhersage)
- [ ] Machine Learning Optimization
- [ ] Grafana Integration
- [ ] MQTT Support
- [ ] Multi-User Support

### Phase 3 (Future)
- [ ] Mobile App
- [ ] Cloud Backup
- [ ] Energy Trading Integration
- [ ] AI-based Prediction

---

## 📞 Support

- **Issues**: https://github.com/svkux/ems-core2.0/issues
- **Discussions**: https://github.com/svkux/ems-core2.0/discussions

---

## 📄 License

MIT License - See LICENSE file
