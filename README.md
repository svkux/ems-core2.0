# EMS-Core v2.0

**Energy Management System** - Intelligente Steuerung von Haushaltsgeräten basierend auf PV-Erzeugung, Batterie und Netz.

## 🚀 Features

### ✅ Implementiert (Stand: 27.01.2026)

- **Energy Sources Management**
  - PV-Erzeugung (Home Assistant, Solax Modbus)
  - Netz-Messung (Shelly 3EM, SDM630)
  - Batterie (Home Assistant, Solax Modbus) mit SOC Anzeige
  - Auto-Refresh alle 5-60 Sekunden (konfigurierbar)

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
  - Hysterese gegen Flackern
  - 30 Sekunden Cycle Intervall

- **Web UI**
  - Device Management (CRUD)
  - Energy Sources Configuration
  - Live Dashboard mit aktuellen Werten
  - Responsive Design

- **Systemd Services**
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

Siehe [INSTALLATION.md](INSTALLATION.md) für detaillierte Anleitung.

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
│   ├── main.py                    # Optimizer Loop
│   ├── device_manager.py          # Device CRUD
│   ├── energy_sources.py          # Energy Data Management
│   ├── controllers/
│   │   ├── shelly.py              # Shelly Controller
│   │   └── sg_ready.py            # SG-Ready Controller
│   └── optimizer/
│       └── scheduler.py           # TODO: Zeitplan-Management
├── webui/
│   ├── app.py                     # Flask App
│   ├── api_routes.py              # Device API
│   ├── api_energy.py              # Energy API
│   └── templates/
│       ├── index.html             # Landing
│       ├── devices.html           # Device Management
│       └── energy_sources.html    # Energy Dashboard + Flow
├── config/
│   ├── devices.yaml               # Device Definitions
│   └── energy_sources.json        # Energy Sources Config
└── logs/
    └── ems.log                    # Application Logs
```

## 🌐 Web UI

**URL:** `http://YOUR-IP:8080`

### Seiten:

1. **Dashboard** (`/`) - Übersicht (TODO)
2. **Devices** (`/devices`) - Geräte-Verwaltung
3. **Energy Sources** (`/energy_sources`) - Energie-Dashboard
   - Tab 1: Übersicht (Value Cards)
   - Tab 2: Energie-Fluss (Sankey Visualisierung)
   - Tab 3: Quellen (Configuration)

## 🔌 API Endpoints

Siehe [API_DOCUMENTATION.md](API_DOCUMENTATION.md) für Details.

**Energy API:**
- `GET /api/energy/sources` - Liste aller Quellen
- `POST /api/energy/sources` - Quelle hinzufügen
- `GET /api/energy/current` - Aktuelle Werte
- `POST /api/energy/refresh` - Manuelle Aktualisierung

**Device API:**
- `GET /api/devices` - Liste aller Geräte
- `POST /api/devices/<id>/control` - Gerät steuern (on/off)
- `GET /api/devices/<id>/status` - Live Status
- `GET /api/devices/<id>/power` - Aktueller Verbrauch

## 🎯 Optimizer Strategie

Der Optimizer entscheidet basierend auf:

1. **Verfügbare Power** = PV-Überschuss - Hysterese
2. **Battery SOC** (Bonus bei >90%, Penalty bei <20%)
3. **Device Priorität:**
   - **CRITICAL**: Immer AN
   - **HIGH**: AN bei ausreichend PV/Battery
   - **MEDIUM**: AN bei gutem Überschuss
   - **LOW/OPTIONAL**: Nur bei deutlichem Überschuss

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
```

## 🛠️ Troubleshooting

Siehe [TROUBLESHOOTING.md](TROUBLESHOOTING.md) für häufige Probleme.

**Häufige Probleme:**

1. **Battery SOC zeigt 0%**
   - Prüfe `entity_id_soc` in Config
   - Siehe Troubleshooting Guide

2. **Devices werden nicht gesteuert**
   - Prüfe IP-Adressen
   - Teste Netzwerk-Erreichbarkeit

3. **WebUI startet nicht**
   - Check Logs: `sudo journalctl -u ems-webui -n 50`
   - Port 8080 bereits belegt?

## 🚧 Roadmap

### Nächste Features (Priorität)

1. **Dashboard** - Zentrale Übersichtsseite
2. **Historische Daten** - Charts für PV/Grid/Battery
3. **Zeitpläne** - "Gerät nur 10-14 Uhr"
4. **Benachrichtigungen** - Email/Push bei Events
5. **Wetter-Integration** - PV-Prognose
6. **Statistiken** - Eigenverbrauch, Autarkie pro Tag/Woche

### Langfristig

- Machine Learning für Verbrauchsprognose
- Strompreis-Integration (dynamische Tarife)
- Mobile App (PWA)
- MQTT Support
- Multi-User System

## 📝 Changelog

Siehe [CHANGELOG.md](CHANGELOG.md) für vollständige Version History.

**v2.0.0 (27.01.2026)**
- Initial Release
- Energy Sources Management
- Device Control (Shelly + SG-Ready)
- Optimizer Loop
- Energy Flow Visualisierung

## 🤝 Contributing

1. Fork das Repository
2. Erstelle einen Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit deine Changes (`git commit -m 'Add AmazingFeature'`)
4. Push zum Branch (`git push origin feature/AmazingFeature`)
5. Öffne einen Pull Request

## 📄 License

MIT License - siehe LICENSE Datei

## 👤 Author

**svkux**
- GitHub: [@svkux](https://github.com/svkux)

## 🙏 Acknowledgments

- Built with [Flask](https://flask.palletsprojects.com/)
- UI inspired by modern energy management systems
- Shelly API integration
- Home Assistant integration
