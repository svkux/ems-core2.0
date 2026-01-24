# 🚀 EMS-Core v2.0 - Deployment Summary

**Stand:** 2025-01-23  
**Status:** ✅ Voll funktionsfähig - Production Ready

---

## 📦 Was ist implementiert

### ✅ **Kern-Module (100% fertig)**

#### 1. Device Manager (`core/device_manager.py`)
- ✅ CRUD für Geräte (Create, Read, Update, Delete)
- ✅ YAML-Persistierung (`config/devices.yaml`)
- ✅ IP-Mapping (`config/device_mapping.json`)
- ✅ Device Discovery Import
- ✅ Validierung
- ✅ Such- & Filter-Funktionen
- ✅ Statistiken-Generierung
- ✅ Export/Import

#### 2. Optimizer Module (`core/optimizer/`)

**Scheduler (`scheduler.py`)**
- ✅ Wochentags-basierte Zeitpläne
- ✅ Zeitfenster-Management (z.B. Mo-Fr 10-14 Uhr)
- ✅ Enable/Disable pro Gerät
- ✅ JSON-Persistierung
- ✅ Nächste Änderung berechnen

**Prioritizer (`prioritizer.py`)**
- ✅ 5 Prioritätsstufen (CRITICAL, HIGH, MEDIUM, LOW, OPTIONAL)
- ✅ User-definierte Reihenfolge (Drag & Drop im UI)
- ✅ Switching Plan Berechnung
- ✅ Mindestlaufzeit-Respektierung
- ✅ Manuelle Überschreibung
- ✅ Hysterese (100W default)

#### 3. Main Optimizer (`core/main.py`)
- ✅ Haupt-Event-Loop (30s Zyklus)
- ✅ Controller-Integration
- ✅ Energie-Daten Aggregation
- ✅ Schaltplan-Ausführung
- ✅ SG-Ready Integration
- ✅ Systemd-ready

#### 4. Energy Sources Manager (`core/energy_sources.py`) 🆕
- ✅ Multi-Provider Support:
  - Home Assistant (API)
  - Shelly (HTTP API)
  - Shelly Pro 3EM (3-Phasen)
  - Solax Modbus (PV + Battery)
  - SDM630 Modbus (Smartmeter)
- ✅ Automatische Hausverbrauch-Berechnung
- ✅ Verfügbare Leistung-Berechnung
- ✅ Async Updates aller Quellen
- ✅ Web UI Integration

---

### ✅ **Controller (100% fertig)**

| Controller | Typ | Status |
|------------|-----|--------|
| `ShellyController` | Gen1/2/Plus/Pro | ✅ |
| `SolaxModbusController` | PV + Battery | ✅ |
| `SDM630ModbusController` | Smartmeter | ✅ |
| `SGReadyController` | Wärmepumpe (4 Modi) | ✅ |
| `ShellyProEM3Controller` | 3-Phasen Messung | ✅ |

---

### ✅ **Web UI (100% fertig)**

#### Templates
- ✅ `index.html` - Dashboard/Landing
- ✅ `devices.html` - Device Management (CRUD)
- ✅ `energy_sources.html` - Energy Sources Config 🆕

#### Features
- ✅ Device Management:
  - Add/Edit/Delete Geräte
  - Suche & Filter
  - Live-Statistiken
  - Responsive Design
- ✅ Energy Sources Management: 🆕
  - PV-Quellen konfigurieren
  - Grid-Messung konfigurieren
  - Battery-Daten
  - Live-Werte anzeigen
  - Multi-Provider Support

#### REST API (`webui/api_routes.py` + `api_energy.py`)

**Device API:**
- `GET /api/devices` - Alle Geräte
- `POST /api/devices` - Neues Gerät
- `PUT /api/devices/{id}` - Update Gerät
- `DELETE /api/devices/{id}` - Lösche Gerät
- `GET /api/devices/stats` - Statistiken
- `POST /api/devices/discover` - Discovery
- `GET /api/devices/types` - Verfügbare Typen
- `GET /api/devices/priorities` - Verfügbare Prioritäten

**Energy API:** 🆕
- `GET /api/energy/sources` - Alle Energy Sources
- `POST /api/energy/sources` - Neue Source
- `DELETE /api/energy/sources/{id}` - Lösche Source
- `POST /api/energy/sources/{id}/toggle` - Enable/Disable
- `GET /api/energy/current` - Aktuelle Werte
- `POST /api/energy/refresh` - Werte aktualisieren

---

### ✅ **Systemd Services (Production-ready)**

#### 1. `ems-webui.service`
- ✅ Startet Web UI auf Port 8080
- ✅ Auto-restart bei Fehler
- ✅ Logging via journald

#### 2. `ems-optimizer.service`
- ✅ Startet Main Optimizer
- ✅ 30s Optimierungs-Intervall
- ✅ Auto-restart bei Fehler

**Befehle:**
```bash
# Status
systemctl status ems-webui
systemctl status ems-optimizer

# Logs
journalctl -u ems-webui -f
journalctl -u ems-optimizer -f

# Neustart
systemctl restart ems-webui
systemctl restart ems-optimizer
```

---

### ✅ **Konfiguration**

| Datei | Zweck | Format |
|-------|-------|--------|
| `config/settings.yaml` | System-Einstellungen | YAML |
| `config/devices.yaml` | Geräte-Definitionen | YAML |
| `config/device_mapping.json` | IP → Device ID | JSON |
| `config/schedules.json` | Zeitpläne | JSON |
| `config/priorities.json` | User-Order | JSON |
| `config/energy_sources.yaml` 🆕 | Energy Sources | YAML |

---

### ✅ **Deployment Scripts**

#### 1. `deploy_ems_updates.sh`
- Automatisches Deployment aller Dateien
- Backup vor Änderungen
- Berechtigungen setzen

#### 2. `update_github.sh`
- One-Click GitHub Sync
- Interaktive Commit-Message
- Auto-Push

#### 3. `setup_complete_system.sh`
- Komplette System-Installation
- Dependency-Check
- Service-Installation
- Tests ausführen

---

## 📁 Vollständige Datei-Struktur

```
/opt/ems-core/
├── core/
│   ├── __init__.py
│   ├── main.py                         # Main Optimizer Loop
│   ├── device_manager.py               # Device CRUD & Management
│   ├── energy_sources.py               # 🆕 Energy Sources Manager
│   │
│   ├── optimizer/
│   │   ├── __init__.py
│   │   ├── scheduler.py                # Zeitplan-Management
│   │   └── prioritizer.py              # Priorisierungs-Logik
│   │
│   ├── controllers/
│   │   ├── __init__.py
│   │   ├── shelly.py                   # Shelly Gen1/2/Plus/Pro
│   │   ├── solax.py                    # Solax Modbus
│   │   ├── sdm630.py                   # SDM630 Modbus
│   │   ├── sg_ready.py                 # SG-Ready Wärmepumpe
│   │   └── shelly_pro_em3.py           # Shelly Pro 3EM
│   │
│   └── integrations/
│       ├── __init__.py
│       └── discovery.py                # Network Discovery
│
├── webui/
│   ├── __init__.py
│   ├── app.py                          # Flask Application
│   ├── api_routes.py                   # Device API
│   ├── api_energy.py                   # 🆕 Energy Sources API
│   │
│   ├── templates/
│   │   ├── index.html                  # Landing/Dashboard
│   │   ├── devices.html                # Device Management
│   │   └── energy_sources.html         # 🆕 Energy Sources
│   │
│   └── static/
│       ├── css/
│       └── js/
│
├── config/
│   ├── settings.yaml                   # System Config
│   ├── devices.yaml                    # Device Definitions
│   ├── device_mapping.json             # IP Mapping
│   ├── schedules.json                  # Zeitpläne
│   ├── priorities.json                 # Priority Order
│   └── energy_sources.yaml             # 🆕 Energy Sources
│
├── logs/                               # Log Files
│   ├── ems.log
│   └── webui.log
│
├── tests/
│   └── test_ems_system.py             # System Tests
│
├── venv/                               # Python Virtual Env
│
├── deploy_ems_updates.sh              # Deployment Script
├── update_github.sh                   # GitHub Sync
├── setup_complete_system.sh           # Complete Setup
├── test_ems_system.py                 # Quick Tests
│
├── ems-core.service                   # Systemd Service (Optimizer)
│
├── requirements.txt                   # Python Dependencies
├── README.md                          # Projekt-Übersicht
├── DEVELOPMENT.md                     # Entwickler-Docs
├── CHANGELOG.md                       # Versionshistorie
├── DEPLOYMENT_SUMMARY.md              # Dieses Dokument
└── QUICK_REFERENCE.md                 # Schnellreferenz
```

---

## 🎯 Was funktioniert (Live-System)

### ✅ **Device Management**
1. Web UI: http://10.0.0.156:8080/devices
2. Geräte hinzufügen/bearbeiten/löschen
3. Suche & Filter funktioniert
4. Statistiken live
5. 2 Geräte konfiguriert:
   - Heizstab (MEDIUM, 3000W)
   - Zirkulationspumpe (LOW, 150W)

### ✅ **Energy Sources** 🆕
1. Web UI: http://10.0.0.156:8080/energy_sources
2. Konfigurierbar:
   - PV-Erzeugung (HA/Shelly/Solax)
   - Netz-Messung (Shelly Pro 3EM/SDM630/Solax)
   - Batterie-Daten (Solax)
3. Live-Werte alle 5s
4. Multi-Provider Support

### ✅ **Optimizer**
1. Läuft als Service (ems-optimizer.service)
2. 30s Optimierungs-Intervall
3. Priorisierung funktioniert
4. Zeitpläne werden respektiert
5. Logging: `journalctl -u ems-optimizer -f`

### ✅ **Systemd Integration**
- Beide Services starten automatisch beim Boot
- Auto-Restart bei Fehler
- Logging via journald
- Production-ready

---

## 🔌 Unterstützte Energie-Quellen

### **PV-Erzeugung:**
- ✅ Home Assistant (API)
- ✅ Shelly (HTTP API)
- ✅ Solax Wechselrichter (Modbus TCP)

### **Netz-Messung:**
- ✅ Home Assistant (API)
- ✅ Shelly Pro 3EM (HTTP API)
- ✅ SDM630 Smartmeter (Modbus TCP)
- ✅ Solax Grid-Daten (Modbus TCP)

### **Batterie:**
- ✅ Solax (Modbus TCP)
- ✅ Home Assistant (API)

### **Berechnungen:**
- ✅ Hausverbrauch = PV + Grid + Battery
- ✅ Verfügbar = |Grid| (wenn negativ)
- ✅ Hysterese: 100W

---

## 🌐 Web UI URLs

| URL | Beschreibung |
|-----|--------------|
| http://10.0.0.156:8080 | Dashboard |
| http://10.0.0.156:8080/devices | Device Management |
| http://10.0.0.156:8080/energy_sources | Energy Sources 🆕 |
| http://10.0.0.156:8080/health | Health Check |
| http://10.0.0.156:8080/api/devices | Device API |
| http://10.0.0.156:8080/api/energy/current | Live Energy Data 🆕 |

---

## 📊 Beispiel: Energie-Fluss

```
┌─────────────┐
│  Solax WR   │──> PV: 5000W
│  (Modbus)   │──> Battery: -800W (lädt)
│             │──> Battery SOC: 65%
└─────────────┘
       │
       ▼
┌─────────────┐
│Shelly Pro3EM│──> Grid: -1500W (Einspeisung!)
└─────────────┘
       │
       ▼
┌─────────────┐
│EMS-Core     │
│Berechnung:  │
│             │
│House = 5000 + (-1500) + (-800) = 2700W
│Available = |-1500| = 1500W
│             │
│Schaltet:    │
│✓ Heizstab  │ (1500W verfügbar, MEDIUM Prio)
└─────────────┘
```

---

## 🔧 Wichtige Befehle

### **Services**
```bash
# Status
systemctl status ems-webui ems-optimizer

# Neu starten
systemctl restart ems-webui ems-optimizer

# Logs
journalctl -u ems-webui -f
journalctl -u ems-optimizer -f
```

### **Testing**
```bash
# Quick Test
python3 test_ems_system.py

# API Test
curl http://localhost:8080/api/devices
curl http://localhost:8080/api/energy/current
```

### **Deployment**
```bash
# GitHub Sync
./update_github.sh

# System Update
git pull
systemctl restart ems-webui ems-optimizer
```

---

## 🆕 Neue Features seit letztem Update

### **Energy Sources Management**
- Multi-Provider Support (HA, Shelly, Modbus)
- Web UI für Konfiguration
- Live-Werte Monitoring
- Automatische Berechnungen

### **Verbesserungen**
- Bessere Error Handling
- Async Energy Updates
- Modular erweiterbar
- Production-ready Services

---

## 🎯 Für nächsten Chat - Quick Start

```bash
# 1. Repository Status
cd /opt/ems-core
git status

# 2. Services prüfen
systemctl status ems-webui ems-optimizer

# 3. Logs anschauen
journalctl -u ems-optimizer -n 50

# 4. Web UI öffnen
# http://10.0.0.156:8080/devices
# http://10.0.0.156:8080/energy_sources

# 5. Aktuelle Energie-Daten
curl http://localhost:8080/api/energy/current
```

**Relevante Dateien zum Sharen:**
- `DEPLOYMENT_SUMMARY.md` (dieses Dokument)
- `QUICK_REFERENCE.md` (Befehle)
- `config/` Ordner (Konfigurationen)
- Output von `systemctl status`

---

**Version:** 2.0.1  
**Datum:** 2025-01-23  
**Status:** ✅ Production Ready mit Energy Sources Integration  
**GitHub:** https://github.com/svkux/ems-core2.0
