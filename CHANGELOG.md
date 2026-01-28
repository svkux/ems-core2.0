# Changelog

Alle nennenswerten Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/),
und dieses Projekt folgt [Semantic Versioning](https://semver.org/lang/de/).

## [2.0.1] - 2026-01-28

### ✨ Added
- **Manual Override System** - Manuelle Gerätesteuerung überschreibt alle Automatismen
  - 3 Modi: AUTO, MANUAL_ON, MANUAL_OFF
  - Zeitbasierte Overrides mit auto-expire
  - REST API für Override-Steuerung
  - Persistenz über Neustarts
  - Integration in Optimizer mit höchster Priorität
  
- **Scheduler System** - Zeitbasierte Gerätesteuerung
  - TIME_WINDOW: Zeitfenster-basierte Steuerung
  - TIME_BLOCK: Blockierung zu bestimmten Zeiten
  - CONDITIONAL: Zeit + Energie-Bedingungen (z.B. PV > 2000W)
  - Wochentags-Support
  - Priority Override Support
  - JSON-basierte Persistenz
  
- **Web UI Redesign** - Komplett überarbeitete Benutzeroberfläche
  - Einheitliche Sidebar Navigation auf allen Seiten
  - Breadcrumbs für bessere Orientierung
  - Device List mit Manual Override Buttons (EIN/AUS/AUTO)
  - Override Status Anzeige mit 👤 Symbol
  - Filter & Suchfunktion für Geräte
  - Toast Notifications für User Feedback
  - Mobile-responsive Design
  - Live System Status in Sidebar
  
- **Dashboard API** - Neuer `/api/dashboard/summary` Endpoint
  - Liefert alle Dashboard-Daten in einem Call
  - Energy Data, Device Stats, Active Devices
  
- **Dokumentation**
  - SCHEDULER_README.md - Vollständige Scheduler Dokumentation
  - OVERRIDE_README.md - Manual Override System Guide
  - WEBUI_README.md - Web UI Redesign Guide
  - BUGFIXES.md - Migration Guide von v2.0.0

### 🐛 Fixed
- Fixed DeviceConfig Inkonsistenzen in main.py
  - `device.connection_params.get('ip')` → `device.ip`
  - `device.power_rating` → `device.power`
- Fixed Async Support in Flask app.py
  - Added `run_async()` helper function
- Improved error handling in device_manager.py
  - Better validation with IP format checks
  - Port range validation (1-65535)
  - Improved error messages

### 🔄 Changed
- **Optimizer Hierarchie** - Neue Entscheidungslogik:
  1. Manual Override (höchste Priorität)
  2. Schedule (force_off/force_on)
  3. PV-Optimierung (normale Logik)
- Updated main.py zu main_final.py mit vollständiger Integration
- Updated app.py mit Override API Integration
- Improved logging mit Emoji-Markern:
  - 👤 für Manual Override
  - 🕐 für Schedule
  - ⚡ für PV-Optimierung

### 📚 Documentation
- Updated README.md mit allen neuen Features
- Added API Examples für alle Endpoints
- Added Troubleshooting Section
- Added Development Setup Guide

### 🧪 Testing
- Added test functions in all new modules
  - device_override.py mit Beispiel-Tests
  - scheduler.py mit Time Window Tests
  - schedule_manager.py mit CRUD Tests

## [2.0.0] - 2026-01-27

### ✨ Added
- Initial Release von EMS-Core v2.0
- **Energy Sources Management**
  - PV-Erzeugung (Home Assistant, Solax Modbus)
  - Netz-Messung (Shelly 3EM, SDM630)
  - Batterie (Home Assistant, Solax Modbus) mit SOC
  - Auto-Refresh konfigurierbar (5-60s)
  
- **Energy Flow Visualisierung**
  - Live Sankey-Diagramm mit animierten Partikeln
  - Eigenverbrauch, Autarkie-Grad, PV-Überschuss
  - Battery SOC mit Progress Bar
  
- **Device Control**
  - Shelly Plug/1PM/Plus/Pro (Gen1 + Gen2)
  - SG-Ready Wärmepumpen Steuerung (4 Modi)
  - Ein/Aus/Toggle Steuerung
  - Live Power Monitoring
  
- **Optimizer Loop**
  - Prioritäts-basierte Steuerung (CRITICAL → OPTIONAL)
  - PV-Überschuss Erkennung
  - Battery SOC basierte Entscheidungen
  - Hysterese gegen Flackern (100W)
  - 30 Sekunden Cycle Intervall
  
- **Web UI**
  - Device Management (CRUD)
  - Energy Sources Configuration
  - Live Dashboard mit aktuellen Werten
  - Responsive Design
  - Landing Page mit System-Übersicht
  
- **Systemd Services**
  - ems-optimizer.service für Optimizer Loop
  - ems-webui.service für Flask Web UI
  - Auto-Start beim Boot
  - Auto-Restart bei Fehler
  - Logging via journald
  
- **REST API**
  - Device API (`/api/devices`)
  - Energy API (`/api/energy`)
  - Health Check (`/health`)
  
- **Dokumentation**
  - README.md mit Feature-Übersicht
  - INSTALLATION.md mit Schritt-für-Schritt Anleitung
  - API_DOCUMENTATION.md mit allen Endpoints
  - TROUBLESHOOTING.md für häufige Probleme

### 🏗️ Architecture
- Modulare Code-Struktur
  - core/ für Backend-Logik
  - webui/ für Frontend
  - config/ für Konfigurationen
  - controllers/ für Device-Controller
- YAML-basierte Device-Konfiguration
- JSON-basierte Energy Sources Konfiguration
- Async/Await für I/O-Operationen

### 📦 Dependencies
- Flask für Web UI
- aiohttp für async HTTP requests
- PyYAML für YAML parsing
- pymodbus für Modbus communication (optional)

---

## Unreleased

### Geplant für v2.1
- [ ] Historische Daten & Charts
- [ ] Schedule Management UI
- [ ] Settings Page
- [ ] Export/Import Configs
- [ ] Wetter-Integration

### Geplant für v2.2
- [ ] Benachrichtigungen (Email/Push)
- [ ] Statistiken Dashboard
- [ ] Dark Mode
- [ ] PWA Support

### Langfristige Roadmap
- [ ] Machine Learning für Verbrauchsprognose
- [ ] Strompreis-Integration
- [ ] MQTT Support
- [ ] Multi-User System
- [ ] Mobile App

---

## Version History

| Version | Datum | Beschreibung |
|---------|-------|--------------|
| 2.0.1 | 2026-01-28 | Manual Override + Scheduler + UI Redesign |
| 2.0.0 | 2026-01-27 | Initial Release |

---

## Migration Guides

### Von 2.0.0 zu 2.0.1

1. **Backup erstellen:**
```bash
cd /opt/ems-core
sudo systemctl stop ems-optimizer ems-webui
cp -r /opt/ems-core /opt/ems-core.backup
```

2. **Code aktualisieren:**
```bash
git pull origin main
```

3. **Neue Dateien deployen:**
```bash
# Override System
cp core/device_override.py /opt/ems-core/core/
cp webui/api_override.py /opt/ems-core/webui/

# Scheduler
mkdir -p /opt/ems-core/core/optimizer
cp core/optimizer/scheduler.py /opt/ems-core/core/optimizer/
cp core/optimizer/schedule_manager.py /opt/ems-core/core/optimizer/

# Updated Files
cp core/main.py /opt/ems-core/core/
cp core/device_manager.py /opt/ems-core/core/
cp webui/app.py /opt/ems-core/webui/

# New Templates
cp webui/templates/base.html /opt/ems-core/webui/templates/
cp webui/templates/index.html /opt/ems-core/webui/templates/
cp webui/templates/devices.html /opt/ems-core/webui/templates/
```

4. **Config-Dateien erstellen:**
```bash
# Werden automatisch beim ersten Start erstellt
touch /opt/ems-core/config/schedules.json
touch /opt/ems-core/config/device_overrides.json
```

5. **Services neu starten:**
```bash
sudo systemctl start ems-optimizer ems-webui
sudo systemctl status ems-optimizer ems-webui
```

6. **Logs prüfen:**
```bash
sudo journalctl -u ems-optimizer -f
# Erwartete Ausgabe:
# ✅ Manual Override enabled
# ✅ Scheduler enabled
```

7. **Web UI testen:**
- Öffne http://YOUR-IP:8080
- Prüfe neue Sidebar Navigation
- Teste Override Buttons in Device List

### Breaking Changes in 2.0.1

**Keine Breaking Changes!**  
v2.0.1 ist vollständig rückwärtskompatibel mit v2.0.0.

Alle neuen Features sind optional:
- Ohne Schedules: System läuft wie v2.0.0
- Ohne Overrides: System läuft wie v2.0.0
- Alte Templates funktionieren weiter (aber neues Design empfohlen)

---

## Contributors

- **svkux** - Initial work and maintainer

## Links

- [Repository](https://github.com/svkux/ems-core2.0)
- [Issues](https://github.com/svkux/ems-core2.0/issues)
- [Discussions](https://github.com/svkux/ems-core2.0/discussions)
