# EMS-Core v2.0

**Energy Management System** - Intelligente Steuerung von Haushaltsgeräten basierend auf PV-Erzeugung, Batterie und Netz.

## 🚀 Features

### ✅ Implementiert (Stand: 28.01.2026)

#### Kern-Funktionen
- **PV-Optimierung** - Automatische Gerätesteuerung basierend auf PV-Überschuss
- **Manual Override** 👤 - Manuelle Gerätesteuerung überschreibt alle Automatismen
- **Zeitpläne (Scheduler)** 🕐 - Zeitbasierte Regeln (Zeit-Fenster, Blockierung, Konditional)
- **Multi-Source Energy** - PV, Batterie, Netz mit verschiedenen Datenquellen

#### Energy Sources Management
- PV-Erzeugung (Home Assistant, Solax Modbus)
- Netz-Messung (Shelly 3EM, SDM630)
- Batterie (Home Assistant, Solax Modbus) mit SOC
- Auto-Refresh alle 5-60 Sekunden (konfigurierbar)

#### Energy Flow Visualisierung
- Live Sankey-Diagramm mit animierten Partikeln
- Eigenverbrauch, Autarkie-Grad, PV-Überschuss
- Battery SOC mit Progress Bar

#### Device Control
- Shelly Plug/1PM/Plus/Pro (Gen1 + Gen2)
- SG-Ready Wärmepumpen Steuerung (4 Modi)
- Ein/Aus/Toggle Steuerung
- Live Power Monitoring
- **Manual Override** (ON/OFF/AUTO) mit optionalem Auto-Expire

#### Optimizer Loop
- **Hierarchische Entscheidung:**
  1. Manual Override (höchste Priorität)
  2. Schedule (force_off/force_on)
  3. PV-Optimierung (normale Logik)
- Prioritäts-basierte Steuerung (CRITICAL → OPTIONAL)
- Battery SOC basierte Entscheidungen
- Hysterese gegen Flackern
- 30 Sekunden Cycle Intervall

#### Scheduler System
- **TIME_WINDOW** - "Gerät nur 10-14 Uhr"
- **TIME_BLOCK** - "Gerät nachts sperren"
- **CONDITIONAL** - "Nur bei PV > 2000W UND 11-16 Uhr"
- Wochentags-Support
- Priority Override
- Persistent über Neustarts

#### Web UI
- **Modern Redesigned** - Einheitliche Sidebar Navigation
- **Device Management** - CRUD mit Manual Override Buttons
- **Live Dashboard** - Energie-Fluss, Metriken, Status
- **Energy Sources** - Configuration & Monitoring
- **Responsive** - Mobile-optimiert
- **Breadcrumbs** - Verbesserte Navigation
- **Toast Notifications** - User Feedback

#### Systemd Services
- Auto-Start beim Boot
- Auto-Restart bei Fehler
- Logging via journald

## 📋 System Requirements

- Ubuntu 20.04+ oder Debian 11+
- Python 3.8+
- 512 MB RAM minimum
- Netzwerk-Zugriff zu:
  - Home Assistant (optional)
  - Shelly Devices
  - Solax Inverter (optional)

## 🔧 Installation

Siehe [INSTALLATION.md](docs/INSTALLATION.md) für detaillierte Anleitung.

**Quick Start:**

```bash
# 1. Clone Repository
git clone https://github.com/svkux/ems-core2.0.git
cd ems-core2.0

# 2. Setup Virtual Environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Deploy Services
sudo ./deploy_services.sh

# 4. Open Web UI
# http://YOUR-IP:8080
```

## 📁 Projekt-Struktur

```
/opt/ems-core/
├── core/
│   ├── main.py                    # Optimizer Loop (mit Override + Scheduler)
│   ├── device_manager.py          # Device CRUD
│   ├── device_override.py         # Manual Override Manager
│   ├── energy_sources.py          # Energy Data Management
│   ├── controllers/
│   │   ├── shelly.py              # Shelly Controller
│   │   └── sg_ready.py            # SG-Ready Controller
│   └── optimizer/
│       ├── scheduler.py           # Scheduler Engine
│       └── schedule_manager.py    # Schedule CRUD
├── webui/
│   ├── app.py                     # Flask App
│   ├── api_routes.py              # Device API
│   ├── api_energy.py              # Energy API
│   ├── api_override.py            # Override API
│   └── templates/
│       ├── base.html              # Base Template (Sidebar)
│       ├── index.html             # Homepage
│       ├── dashboard.html         # Live Dashboard
│       ├── devices.html           # Device Management + Override
│       └── energy_sources.html    # Energy Configuration
├── config/
│   ├── devices.yaml               # Device Definitions
│   ├── energy_sources.json        # Energy Sources Config
│   ├── schedules.json             # Zeitpläne
│   └── device_overrides.json      # Manual Overrides
└── logs/
    └── ems.log                    # Application Logs
```

## 🌐 Web UI

**URL:** `http://YOUR-IP:8080`

### Seiten:

1. **Home** (`/`) - System-Übersicht und Quick Links
2. **Dashboard** (`/dashboard`) - Live Energie-Flüsse und Metriken
3. **Devices** (`/devices`) - Geräte-Verwaltung mit Manual Override
4. **Energy Sources** (`/energy_sources`) - Energie-Quellen Konfiguration

### Manual Override

Jedes Gerät hat drei Buttons:
- **▶️ EIN** - Manuell einschalten (überschreibt alles)
- **⏸️ AUS** - Manuell ausschalten (überschreibt alles)
- **🤖 AUTO** - Zurück zur automatischen Steuerung

## 🔌 API Endpoints

### Device API
```bash
GET    /api/devices                    # Liste aller Geräte
POST   /api/devices/<id>/control       # Gerät steuern
GET    /api/devices/<id>/status        # Live Status
GET    /api/devices/<id>/power         # Aktueller Verbrauch
```

### Energy API
```bash
GET    /api/energy/sources             # Liste aller Quellen
POST   /api/energy/sources             # Quelle hinzufügen
GET    /api/energy/current             # Aktuelle Werte
POST   /api/energy/refresh             # Manuelle Aktualisierung
```

### Override API
```bash
GET    /api/override/status            # Alle Overrides
GET    /api/override/<device_id>       # Override Status
POST   /api/override/<device_id>       # Override setzen
DELETE /api/override/<device_id>       # Override entfernen
POST   /api/override/<device_id>/manual_on   # Quick: EIN
POST   /api/override/<device_id>/manual_off  # Quick: AUS
POST   /api/override/<device_id>/auto        # Quick: AUTO
```

### Dashboard API
```bash
GET    /api/dashboard/summary          # Dashboard Daten
```

Siehe [API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md) für Details.

## 🎯 Optimizer Hierarchie

```
1. MANUAL OVERRIDE 👤  (höchste Priorität)
       ↓
2. SCHEDULE 🕐         (force_off/force_on)
       ↓
3. PV-OPTIMIERUNG ⚡   (normale Logik basierend auf Priority)
```

### Beispiel-Szenario

**Setup:**
- Device: Waschmaschine (Priority: MEDIUM)
- PV: 1000W (zu wenig für MEDIUM)
- Schedule: force_off außerhalb 10-14 Uhr
- Zeit: 09:30 Uhr

**Ohne Override:**
```
Schedule prüfen → force_off (außerhalb Fenster)
→ Gerät AUS ❌
```

**Mit Manual Override (EIN):**
```
Override prüfen → manual_on
→ Gerät EIN ✅ (trotz wenig PV und Schedule!)
```

## 📊 Logging & Monitoring

```bash
# Optimizer Logs (Live)
sudo journalctl -u ems-optimizer -f

# WebUI Logs (Live)
sudo journalctl -u ems-webui -f

# Beide zusammen
sudo journalctl -u ems-optimizer -u ems-webui -f

# Logs der letzten Stunde
sudo journalctl -u ems-optimizer --since "1 hour ago"

# Override-Entscheidungen
sudo journalctl -u ems-optimizer -f | grep "👤"

# Schedule-Entscheidungen
sudo journalctl -u ems-optimizer -f | grep "🕐"
```

## 🛠️ Troubleshooting

Siehe [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) für häufige Probleme.

**Quick Checks:**

```bash
# System Status
curl http://localhost:8080/health

# Devices
curl http://localhost:8080/api/devices

# Overrides
curl http://localhost:8080/api/override/status

# Energy
curl http://localhost:8080/api/energy/current
```

## 📚 Dokumentation

- [INSTALLATION.md](docs/INSTALLATION.md) - Vollständige Installations-Anleitung
- [BUGFIXES.md](docs/BUGFIXES.md) - Bug Fixes und Migration von v2.0.0
- [DASHBOARD_README.md](docs/DASHBOARD_README.md) - Dashboard Dokumentation
- [SCHEDULER_README.md](docs/SCHEDULER_README.md) - Scheduler System
- [OVERRIDE_README.md](docs/OVERRIDE_README.md) - Manual Override System
- [WEBUI_README.md](docs/WEBUI_README.md) - Web UI Redesign
- [API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md) - REST API Referenz
- [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) - Problemlösungen

## 🚧 Roadmap

### v2.1 (Q1 2026)
- [ ] Historische Daten & Charts (24h, 7d, 30d)
- [ ] Schedule Management UI
- [ ] Settings Page
- [ ] Export/Import Configs

### v2.2 (Q2 2026)
- [ ] Wetter-Integration (PV-Prognose)
- [ ] Benachrichtigungen (Email/Push)
- [ ] Statistiken (Eigenverbrauch pro Tag/Woche)
- [ ] Dark Mode

### Langfristig
- Machine Learning für Verbrauchsprognose
- Strompreis-Integration (dynamische Tarife)
- Mobile App (PWA)
- MQTT Support
- Multi-User System

## 📝 Changelog

Siehe [CHANGELOG.md](CHANGELOG.md) für vollständige Version History.

### v2.0.1 (28.01.2026)
- ✨ Manual Override System
- ✨ Scheduler System (TIME_WINDOW, TIME_BLOCK, CONDITIONAL)
- ✨ Web UI Redesign mit Sidebar Navigation
- ✨ Device List mit Override Buttons
- 🐛 Fixed DeviceConfig Inkonsistenzen
- 🐛 Fixed Async Support in Flask
- 📚 Umfangreiche Dokumentation

### v2.0.0 (27.01.2026)
- 🎉 Initial Release
- ⚡ Energy Sources Management
- 🔌 Device Control (Shelly + SG-Ready)
- 🤖 Optimizer Loop
- 📊 Energy Flow Visualisierung
- 🌐 Web UI

## 🤝 Contributing

Contributions sind willkommen! Bitte:

1. Fork das Repository
2. Erstelle einen Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit deine Changes (`git commit -m 'Add AmazingFeature'`)
4. Push zum Branch (`git push origin feature/AmazingFeature`)
5. Öffne einen Pull Request

### Development Setup

```bash
# Clone & Setup
git clone https://github.com/svkux/ems-core2.0.git
cd ems-core2.0
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run Optimizer (Development)
python3 core/main.py

# Run WebUI (Development)
python3 webui/app.py

# Run Tests
python3 -m pytest tests/
```

## 📄 License

MIT License - siehe [LICENSE](LICENSE) Datei

## 👤 Author

**svkux**
- GitHub: [@svkux](https://github.com/svkux)
- Project: [ems-core2.0](https://github.com/svkux/ems-core2.0)

## 🙏 Acknowledgments

- Built with [Flask](https://flask.palletsprojects.com/)
- UI inspired by modern energy management systems
- Shelly API integration
- Home Assistant integration
- Community feedback and contributions

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/svkux/ems-core2.0/issues)
- **Discussions**: [GitHub Discussions](https://github.com/svkux/ems-core2.0/discussions)
- **Dokumentation**: [docs/](docs/)

## ⭐ Star History

Wenn dir dieses Projekt gefällt, gib ihm einen Star! ⭐

---

**Made with ❤️ by svkux**  
**Version 2.0.1 | Januar 2026**
