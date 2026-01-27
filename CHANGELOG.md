# Changelog

Alle wichtigen Änderungen an EMS-Core werden hier dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/).

## [2.0.0] - 2026-01-27

### 🎉 Initial Release - Vollständiges EMS-Core v2.0

### Added

#### Energy Management
- **Energy Sources Manager** (`core/energy_sources.py`)
  - Support für PV, Grid, Battery Sources
  - Provider: Home Assistant, Shelly 3EM, Solax Modbus, SDM630
  - Battery SOC Monitoring und Anzeige
  - Auto-Update Mechanismus
  - Hausverbrauch-Berechnung: `House = PV - Battery + Grid`
  
- **Energy Flow Visualisierung**
  - Live Sankey-Diagramm mit animierten Partikeln
  - Dynamische Farbcodierung (PV=Grün, Battery=Blau, Grid=Rot/Grün)
  - Summary Cards: Eigenverbrauch, Autarkie-Grad, PV-Überschuss
  - Battery SOC Progress Bar
  - Integriert als Tab in Energy Sources Page

#### Device Control
- **Shelly Controller** (`core/controllers/shelly.py`)
  - Vollständiger Support für Gen1 (Plug, 1PM, 2.5, 3EM)
  - Vollständiger Support für Gen2 (Plus, Pro)
  - Funktionen: turn_on, turn_off, toggle, get_status, get_power
  - Async + Sync Wrapper für Flask Integration
  
- **SG-Ready Controller** (`core/controllers/sg_ready.py`)
  - 4 Betriebsmodi: OFF, NORMAL, RECOMMENDED, FORCED
  - 2-Relais Steuerung für SG-Ready Eingänge
  - PV-Überschuss Mode für Wärmepumpen

#### Optimizer
- **Main Optimizer Loop** (`core/main.py`)
  - Prioritäts-basierte Device Steuerung
  - 5 Prioritäts-Level: CRITICAL, HIGH, MEDIUM, LOW, OPTIONAL
  - PV-Überschuss Erkennung mit konfigurierbarer Hysterese
  - Battery SOC basierte Entscheidungen (Bonus/Penalty System)
  - 30 Sekunden Cycle Intervall
  - Umfassendes Logging

#### Web UI
- **Energy Sources Page** (`webui/templates/energy_sources.html`)
  - Tab 1: Übersicht mit Value Cards
  - Tab 2: Energie-Fluss Visualisierung
  - Tab 3: Quellen-Konfiguration
  - Auto-Refresh alle 5-60 Sekunden (konfigurierbar)
  - Live Timestamp "Zuletzt aktualisiert"
  
- **Device Management** (`webui/templates/devices.html`)
  - CRUD Operationen für Devices
  - Device Discovery (Vorbereitung)
  - Kategorien und Prioritäten
  
- **API Endpoints**
  - Energy API: `/api/energy/sources`, `/api/energy/current`, `/api/energy/refresh`
  - Device API: `/api/devices`, `/api/devices/<id>/control`, `/api/devices/<id>/status`
  - Control: ON/OFF/Toggle für Shelly Devices
  - Batch Control für mehrere Devices

#### System Integration
- **Systemd Services**
  - `ems-optimizer.service` - Optimizer Loop
  - `ems-webui.service` - Flask Web UI
  - Auto-Start beim Boot
  - Auto-Restart bei Fehler
  - Logging via journald
  
- **Deployment Script** (`deploy_services.sh`)
  - Automatische Service Installation
  - Service Aktivierung
  - Status-Anzeige
  - Hilfreiche Kommando-Übersicht

### Fixed

#### Battery SOC Anzeige
- **Problem:** Battery SOC wurde nicht angezeigt (zeigte immer 0%)
- **Root Cause:** 
  1. Doppeltes "sensor." in entity_id_soc: `sensor.sensor.batterie_soc_2`
  2. WebUI und Optimizer nutzten unterschiedliche Config-Dateien
  3. Python Cache verhinderte Code-Updates
- **Lösung:**
  1. Config korrigiert zu: `sensor.batterie_soc_2`
  2. WebUI Config-Pfad geändert zu zentraler Config: `/opt/ems-core/config/energy_sources.json`
  3. Debug-Logging hinzugefügt zur besseren Fehlersuche

#### Hausverbrauch-Berechnung
- **Problem:** Falsche Berechnung bei Battery Entladung
- **Alte Formel:** `House = PV + Grid + Battery` (falsch bei Entladung)
- **Neue Formel:** `House = PV - Battery + Grid` (korrekt)
- **Validierung:**
  - Beispiel 1: PV=3000W, Battery=+500W (lädt), Grid=-1000W → House=1500W ✓
  - Beispiel 2: PV=1000W, Battery=-500W (entlädt), Grid=+1000W → House=2500W ✓

#### Auto-Refresh Mechanismus
- **Problem:** Timestamp aktualisierte sich, aber Werte blieben gleich
- **Root Cause:** Frontend rief `/api/energy/current` auf, aber Backend holte keine neuen Daten
- **Lösung:** `updateValues()` ruft jetzt zuerst `/api/energy/refresh` auf, um Backend zu triggern

### Changed

- **Config-Struktur:** Zentralisierte Config in `/opt/ems-core/config/`
- **Logging:** Ausführlicheres Logging mit Debug-Messages
- **Error Handling:** Verbesserte Exception Handling in allen Controllern

### Technical Details

#### Dependencies
```
Flask>=2.3.0
aiohttp>=3.9.0
pymodbus>=3.5.0
pyyaml>=6.0
```

#### Python Version
- Minimum: Python 3.8
- Tested: Python 3.10, 3.11

#### Architecture
- **Backend:** Flask + asyncio
- **Frontend:** Vanilla JavaScript (keine Frameworks)
- **Data Flow:** Energy Sources → Manager → API → Frontend
- **Persistence:** JSON Files (Config), journald (Logs)

### Known Issues

1. **Device Discovery** - Noch nicht implementiert (Placeholder vorhanden)
2. **Schedules** - Zeitbasierte Regeln noch nicht verfügbar
3. **Historische Daten** - Keine Speicherung historischer Werte
4. **Authentication** - Kein Login-System (alle APIs öffentlich)

### Security Notes

- ⚠️ Web UI läuft ohne Authentication (Port 8080)
- ⚠️ Services laufen als root (für Hardware-Zugriff)
- ✅ Keine sensiblen Daten im Code (Tokens in Config)
- ✅ Config-Dateien sind nicht web-accessible

### Migration Notes

Für Upgrade von älteren Versionen:
- Keine Migration nötig (v2.0.0 ist erste Release)
- Config-Format ist stabil

### Credits

Entwickelt mit Unterstützung von Claude (Anthropic AI).

---

## [Unreleased]

### Planned Features

#### High Priority
- Dashboard mit Gesamtübersicht
- Historische Daten (Tages-/Wochen-Charts)
- Device Status Live-Anzeige in WebUI
- Zeitpläne/Schedules für Devices

#### Medium Priority
- Benachrichtigungen (Email, Push)
- Wetter-API Integration für PV-Prognose
- Statistiken (Eigenverbrauch, Autarkie)
- Export (CSV, JSON)

#### Low Priority
- User Authentication
- Multi-User Support
- Mobile App (PWA)
- MQTT Integration
- Machine Learning Prognosen

---

## Version History

- **v2.0.0** (2026-01-27) - Initial Release
- **v1.x** - Experimentelle Versionen (nicht veröffentlicht)

---

## Changelog Konventionen

- **Added** - Neue Features
- **Changed** - Änderungen an existierenden Features
- **Deprecated** - Features die bald entfernt werden
- **Removed** - Entfernte Features
- **Fixed** - Bug Fixes
- **Security** - Sicherheits-Fixes
