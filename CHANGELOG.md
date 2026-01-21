# Changelog

All notable changes to EMS-Core will be documented in this file.

## [2.0.0] - 2025-01-19

### 🎉 Major Release - Complete Rewrite

#### Added

**Core Features**
- ✨ **DeviceManager** - Zentrale Geräte-Verwaltung mit YAML/JSON Persistierung
- ✨ **Scheduler Module** - Wochentags-basierte Zeitplan-Verwaltung
- ✨ **Prioritizer Module** - Intelligente 5-Stufen Priorisierung (CRITICAL → OPTIONAL)
- ✨ **Main Optimizer** - Haupt-Event-Loop mit 30s Optimierungs-Zyklus
- ✨ **Device Mapping** - IP-basiertes Device-Mapping System

**Web UI**
- ✨ **Device Management UI** - Vollständige CRUD-Oberfläche für Geräte
  - Add/Edit/Delete Geräte via Modal
  - Suche und Filter-Funktionen
  - Live-Statistiken Dashboard
  - Responsive Design
- ✨ **REST API** - Vollständige RESTful API (`/api/devices/*`)
  - CRUD Endpoints
  - Discovery Integration
  - Statistics Endpoints
  - Device Control

**Controllers**
- ✨ **ShellyController** - Unterstützung für Gen1, Gen2, Plus, Pro
- ✨ **SolaxModbusController** - PV + Battery Integration
- ✨ **SDM630ModbusController** - Smartmeter Integration
- ✨ **SGReadyController** - 4-Modi Wärmepumpen-Steuerung
- ✨ **ShellyProEM3Controller** - 3-Phasen Energie-Messung

**Configuration**
- ✨ Neue Config-Struktur mit YAML/JSON
  - `settings.yaml` - System-Konfiguration
  - `devices.yaml` - Geräte-Definitionen
  - `schedules.json` - Zeitpläne
  - `priorities.json` - User-definierte Reihenfolge
  - `device_mapping.json` - IP-Mapping

**Deployment**
- ✨ **Deployment Script** (`deploy_ems_updates.sh`) - Automatische Installation
- ✨ **GitHub Sync Script** (`update_github.sh`) - One-Click GitHub Update
- ✨ **Systemd Service** - Production-ready Service-Konfiguration
- ✨ **Test Suite** - Umfassende System-Tests

**Documentation**
- ✨ **README.md** - Vollständige Projekt-Dokumentation
- ✨ **DEVELOPMENT.md** - Entwickler-Dokumentation
- ✨ **CHANGELOG.md** - Versionshistorie

#### Improved

**Performance**
- ⚡ Async/Await für alle I/O-Operationen
- ⚡ Optimierte Schaltungs-Berechnung mit Hysterese
- ⚡ Caching für Device-Status

**User Experience**
- 🎨 Modernes, responsives Web UI Design
- 🎨 Live-Updates ohne Page Reload
- 🎨 Intuitive Device-Verwaltung
- 🎨 Aussagekräftige Fehlermeldungen

**Code Quality**
- 📝 Type Hints für alle Funktionen
- 📝 Umfassende Docstrings
- 📝 Logging auf allen Ebenen
- 📝 Strukturierte Error Handling

#### Technical Details

**Architecture**
```
Core Layer:
├── device_manager.py      # Device CRUD & Persistence
├── main.py               # Main Event Loop
└── optimizer/
    ├── scheduler.py      # Time-based Scheduling
    └── prioritizer.py    # Priority-based Switching

Controller Layer:
├── shelly.py            # Shelly Devices
├── solax.py             # PV/Battery
├── sdm630.py            # Smartmeter
└── sg_ready.py          # Heatpump Control

Web Layer:
├── app.py               # Flask Application
├── api_routes.py        # REST API
└── templates/
    └── devices.html     # Device Management UI
```

**Dependencies**
- Python 3.9+
- Flask 3.0+
- PyYAML
- aiohttp
- pymodbus

**Configuration**
- Alle Konfigurationen in `config/` Ordner
- YAML für strukturierte Daten
- JSON für dynamische Daten
- Automatisches Backup bei Updates

**API Endpoints**
- `GET /api/devices` - List all devices
- `POST /api/devices` - Create device
- `PUT /api/devices/{id}` - Update device
- `DELETE /api/devices/{id}` - Delete device
- `POST /api/devices/discover` - Run discovery
- `GET /api/devices/stats` - Get statistics

#### Migration Notes

**From v1.x to v2.0:**

1. **Backup alte Konfiguration:**
   ```bash
   cp -r config/ config.backup/
   ```

2. **Run Deployment Script:**
   ```bash
   ./deploy_ems_updates.sh
   ```

3. **Migrate Devices:**
   - Alte Geräte müssen neu über Web UI hinzugefügt werden
   - Oder manuell in `config/devices.yaml` eintragen

4. **Test System:**
   ```bash
   python3 test_ems_system.py
   ```

5. **Start Service:**
   ```bash
   sudo systemctl restart ems-core
   ```

#### Known Issues

- 🐛 Discovery könnte bei großen Netzwerken langsam sein
- 🐛 Web UI aktualisiert nicht automatisch (Reload erforderlich)
- ⚠️ SG-Ready Logik noch nicht vollständig getestet

#### Contributors

- Initial development and architecture
- Device Manager implementation
- Web UI design and implementation
- Documentation

---

## [1.0.0] - 2024-12-XX

### Initial Release

- Basic Shelly integration
- Simple scheduling
- Home Assistant dependency
- Manual configuration

---

## Version Schema

Format: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

---

## Legend

- ✨ New Feature
- 🐛 Bug Fix
- ⚡ Performance
- 🎨 UI/UX
- 📝 Documentation
- 🔧 Configuration
- ⚠️ Warning
- 🗑️ Deprecated
- 🔒 Security
