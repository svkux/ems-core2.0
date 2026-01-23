# EMS-Core v2.0 - Energie-Management-System

🔋 **Intelligentes, eigenständiges Energie-Management ohne Home Assistant**

Optimiert PV-Eigenverbrauch durch priorisierte Verbraucher-Steuerung mit Zeitplänen, Batterie-Integration und SG-Ready Wärmepumpen-Steuerung.

---

## 📋 Inhaltsverzeichnis

- [Features](#-features)
- [Architektur](#-architektur)
- [Installation](#-installation)
- [Konfiguration](#-konfiguration)
- [Web UI](#-web-ui)
- [API](#-api)
- [Beispiele](#-beispiele)
- [Troubleshooting](#-troubleshooting)

---

## ✨ Features

### Kern-Funktionen
- ✅ **Automatische Geräte-Erkennung** (Shelly, Solax, SDM630)
- ✅ **Intelligente Priorisierung** mit 5 Prioritätsstufen
- ✅ **Zeitplan-Management** für automatische Steuerung
- ✅ **Batterie-Integration** mit SOC-basierter Logik
- ✅ **SG-Ready Steuerung** für Wärmepumpen (4 Modi)
- ✅ **Web UI** mit Drag & Drop Priorisierung
- ✅ **Echtzeit-Optimierung** alle 30 Sekunden
- ✅ **Manuelle Überschreibung** pro Gerät

### Unterstützte Geräte
- **Shelly**: Plug, 1PM, Plus 1PM, Pro 1PM, Pro 3EM
- **Solax**: X1/X3 Wechselrichter (Modbus TCP)
- **SDM630**: Smartmeter (Modbus TCP)
- **Allgemein**: Jedes Gerät mit HTTP/Modbus API

---

## 🏗️ Architektur

```
┌─────────────────────────────────────────────────────────────┐
│                        EMS-Core v2.0                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Discovery  │  │  Controller  │  │   Optimizer  │     │
│  │  (Netzwerk)  │  │   (Geräte)   │  │  (Logik)     │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                  │                  │             │
│         └──────────────────┴──────────────────┘             │
│                            │                                │
│                    ┌───────▼────────┐                       │
│                    │   Main Loop    │                       │
│                    │  (30s Cycle)   │                       │
│                    └───────┬────────┘                       │
│                            │                                │
│         ┌──────────────────┼──────────────────┐             │
│         │                  │                  │             │
│    ┌────▼─────┐     ┌──────▼──────┐    ┌─────▼────┐        │
│    │Scheduler │     │ Prioritizer │    │SG-Ready  │        │
│    │(Zeit)    │     │(Prio-Logik) │    │(WP)      │        │
│    └──────────┘     └─────────────┘    └──────────┘        │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                        Web UI (8080)                        │
│  Discovery | Config | Priorities | Schedules | Manual      │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Installation

### Voraussetzungen
- Python 3.9+
- LXC Container oder Linux Server
- Netzwerk-Zugriff zu Geräten

### Automatische Installation

```bash
# Repository klonen
git clone https://github.com/svkux/ems-core2.0.git
cd ems-core2.0

# Installation ausführen
chmod +x install_ems_complete.sh
sudo ./install_ems_complete.sh
```

### Manuelle Installation

```bash
# Virtuelle Umgebung erstellen
python3 -m venv venv
source venv/bin/activate

# Dependencies installieren
pip install -r requirements.txt

# Konfiguration erstellen
mkdir -p config logs
cp config/settings.yaml.example config/settings.yaml
cp config/devices.yaml.example config/devices.yaml

# Systemd Service einrichten
sudo cp ems-core.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ems-core
sudo systemctl start ems-core
```

---

## ⚙️ Konfiguration

### 1. System-Einstellungen (`config/settings.yaml`)

```yaml
optimization_interval: 30  # Sekunden
hysteresis: 100  # Watt Hysterese

battery:
  min_soc: 20
  max_soc: 95
  priority_soc: 50  # Ab diesem SOC Verbraucher priorisieren

solax:
  ip: "10.0.0.100"
  port: 502

sg_ready:
  enabled: true
  relay1_id: "shelly_sg_relay1"
  relay2_id: "shelly_sg_relay2"
```

### 2. Geräte-Konfiguration (`config/devices.yaml`)

```yaml
devices:
  - id: "heater"
    name: "Heizstab"
    type: "shelly_1pm"
    ip: "10.0.0.151"
    power: 3000
    priority: "MEDIUM"
    can_control: true
    min_runtime: 30  # Minuten
```

### 3. Prioritäts-Stufen

| Priorität | Beschreibung | Beispiel |
|-----------|--------------|----------|
| `CRITICAL` | Immer an | Kühlschrank, Server |
| `HIGH` | Hohe Priorität | Wärmepumpe |
| `MEDIUM` | Mittlere Priorität | Heizstab |
| `LOW` | Niedrige Priorität | Waschmaschine |
| `OPTIONAL` | Nur bei Überschuss | E-Auto Wallbox |

### 4. Zeitpläne (`config/schedules.json`)

```json
{
  "heater": {
    "device_id": "heater",
    "enabled": true,
    "schedule": {
      "monday": [[10, 14], [20, 22]],
      "tuesday": [[10, 14]]
    }
  }
}
```

**Format:** `[[start_hour, end_hour], ...]`

---

## 🌐 Web UI

URL: **http://YOUR_IP:8080**

### Tabs

#### 1. **Discovery**
- Automatisches Scannen nach Geräten
- Anzeige gefundener Shelly, Solax, SDM630
- Hinzufügen zur Konfiguration

#### 2. **Config**
- System-Einstellungen bearbeiten
- Batterie-Parameter anpassen
- SG-Ready konfigurieren

#### 3. **Priorities**
- **Drag & Drop** Priorisierung
- Reihenfolge definiert Schaltung bei gleicher Priorität
- Live-Vorschau der Leistungsverteilung

#### 4. **Schedules**
- Zeitpläne erstellen/bearbeiten
- Wochentags-basierte Steuerung
- Aktivierung/Deaktivierung pro Gerät

#### 5. **Manual**
- Manuelle Geräte-Steuerung
- Überschreibt automatische Optimierung
- Status-Anzeige aller Geräte

---

## 📊 Optimierungs-Logik

### Energie-Berechnung

```python
# Verfügbare Leistung berechnen
available_power = PV - Hausverbrauch - Batterieladung

# Wenn Batterie > priority_soc (50%):
if battery_soc >= 50:
    available_power = |Netz-Einspeisung| - Hysterese

# Wenn Batterie fast voll (>90%):
if battery_soc >= 90:
    available_power = max(available_power, |Netz-Einspeisung|)
```

### Schaltungs-Algorithmus

1. **Phase 1: CRITICAL Geräte** (immer an)
2. **Phase 2: SCHEDULED Geräte** (wenn im Zeitplan)
3. **Phase 3: Priorisierte Geräte** (nach Reihenfolge)
   - Sortierung: Priority → User-Order
   - Respektiert Mindestlaufzeit
   - Berücksichtigt Hysterese

### SG-Ready Modi

| Modus | Bedingung | Beschreibung |
|-------|-----------|--------------|
| `LOCKED` | SOC < 20% | Sperre (Batterie leer) |
| `NORMAL` | Default | Normalbetrieb |
| `COMFORT` | Überschuss > 2kW | Erhöhter Komfort |
| `FORCED` | Überschuss > 5kW & SOC > 80% | Zwangsbetrieb |

---

## 🔧 API

### REST Endpoints

```bash
# System Status
GET /api/status

# Geräte-Liste
GET /api/devices

# Gerät schalten
POST /api/device/{device_id}/switch
{
  "state": true,  # true=ON, false=OFF
  "manual": true  # Optional: Manuelle Überschreibung
}

# Zeitplan setzen
POST /api/schedule/{device_id}
{
  "schedule": {
    "monday": [[10, 14]]
  },
  "enabled": true
}

# Priorität ändern
POST /api/priority
{
  "order": ["device1", "device2", "device3"]
}
```

---

## 📝 Beispiele

### Beispiel 1: Sonniger Tag (8kW PV)

```
Zeit: 12:00 Uhr, Montag
PV: 8000W
Batterie: 85% (lädt leicht)
Netz: -2000W (Einspeisung)

→ Verfügbar: ~2000W

Schaltung:
✓ Kühlschrank (150W) - CRITICAL
✓ Wärmepumpe (2000W) - HIGH, im Zeitplan
✗ Heizstab (3000W) - MEDIUM (nicht genug Leistung)
✗ Waschmaschine (2000W) - LOW
```

### Beispiel 2: Bewölkt (2kW PV)

```
Zeit: 14:00 Uhr
PV: 2000W
Batterie: 45% (entlädt)
Netz: 500W (Bezug)

→ Verfügbar: 0W (Batterie hat Priorität)

Schaltung:
✓ Kühlschrank (150W) - CRITICAL
✗ Alle anderen Geräte
```

### Beispiel 3: Hoher Überschuss (12kW PV)

```
Zeit: 13:00 Uhr
PV: 12000W
Batterie: 95% (voll)
Netz: -5000W (Einspeisung)

→ Verfügbar: ~5000W

Schaltung:
✓ Kühlschrank (150W)
✓ Wärmepumpe (2000W) - SG-Ready: FORCED
✓ Heizstab (3000W)
✓ Waschmaschine (2000W)
→ Gesamt: 7150W (System schaltet intelligent)
```

---

## 🐛 Troubleshooting

### Gerät wird nicht erkannt

```bash
# Prüfe Netzwerk-Erreichbarkeit
ping 10.0.0.150

# Prüfe Shelly API
curl http://10.0.0.150/status

# Logs prüfen
sudo journalctl -u ems-core -f
```

### Optimierung läuft nicht

```bash
# Service Status
sudo systemctl status ems-core

# Neustart
sudo systemctl restart ems-core

# Config validieren
python3 -c "import yaml; yaml.safe_load(open('config/settings.yaml'))"
```

### Batterie-Priorität funktioniert nicht

- Prüfe `battery.priority_soc` in `settings.yaml`
- Stelle sicher dass Solax-Daten korrekt gelesen werden
- Logs prüfen: `grep "Battery" /var/log/ems-core.log`

### SG-Ready schaltet nicht

```bash
# Prüfe Relais-Status
curl http://RELAY1_IP/status
curl http://RELAY2_IP/status

# Prüfe Konfiguration
grep -A5 "sg_ready" config/settings.yaml
```

---

## 🧪 Tests

### System-Test ausführen

```bash
source venv/bin/activate
python3 test_ems_system.py
```

**Erwartete Ausgabe:**
```
✓ PASS - Scheduler Basic
✓ PASS - Scheduler Time Windows
✓ PASS - Prioritizer Basic
...
✓ ALL TESTS PASSED!
```

---

## 📈 Monitoring

### Logs

```bash
# Live Logs
sudo journalctl -u ems-core -f

# Fehler-Logs
sudo journalctl -u ems-core -p err

# Letzte 100 Zeilen
sudo journalctl -u ems-core -n 100
```

### Statistiken

Die Web UI zeigt:
- Gesamt-Optimierungen
- Geschaltete Geräte
- Aktuelle Energie-Daten
- Letzte Optimierung

---

## 🔄 Updates

```bash
cd /opt/ems-core
git pull
sudo systemctl restart ems-core
```

---

## 📞 Support

- **GitHub Issues**: https://github.com/svkux/ems-core2.0/issues
- **Dokumentation**: Siehe `docs/` Ordner

---

## 📄 Lizenz

MIT License - Siehe LICENSE Datei

---

## 🙏 Credits

Entwickelt für maximale PV-Eigenverbrauch-Optimierung mit Shelly-Geräten, Solax-Wechselrichtern und SG-Ready Wärmepumpen.

**Version:** 2.0  
**Autor:** EMS-Core Team  
**Datum:** Januar 2025
