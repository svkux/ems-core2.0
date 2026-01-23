# 🚀 EMS-Core v2.0 - Quick Reference

## 📦 Installation (One-Liner)

```bash
cd /opt/ems-core2.0 && ./setup_complete_system.sh
```

---

## 🔧 Wichtigste Befehle

### System
```bash
# Starten
sudo systemctl start ems-core

# Stoppen
sudo systemctl stop ems-core

# Status
sudo systemctl status ems-core

# Logs (Live)
sudo journalctl -u ems-core -f

# Neustart
sudo systemctl restart ems-core
```

### Development
```bash
# Virtual Environment aktivieren
source venv/bin/activate

# Web UI starten
python3 webui/app.py

# Main Optimizer starten
python3 core/main.py

# Tests
python3 test_ems_system.py
```

### Git
```bash
# Status
git status

# Commit & Push (automatisch)
./update_github.sh

# Manuell
git add .
git commit -m "Your message"
git push origin main
```

---

## 📁 Wichtigste Dateien

| Datei | Beschreibung |
|-------|--------------|
| `core/device_manager.py` | Device CRUD & Management |
| `core/main.py` | Haupt-Optimizer Loop |
| `core/optimizer/scheduler.py` | Zeitplan-Management |
| `core/optimizer/prioritizer.py` | Priorisierungs-Logik |
| `webui/app.py` | Flask Web Server |
| `webui/api_routes.py` | REST API Endpoints |
| `webui/templates/devices.html` | Device Management UI |
| `config/settings.yaml` | System-Konfiguration |
| `config/devices.yaml` | Geräte-Definitionen |
| `config/schedules.json` | Zeitpläne |

---

## 🌐 URLs

| Service | URL |
|---------|-----|
| Web UI | http://10.0.0.252:8080 |
| Device Management | http://10.0.0.252:8080/devices |
| Discovery | http://10.0.0.252:8080/discovery |
| API Docs | http://10.0.0.252:8080/api/devices |
| Health Check | http://10.0.0.252:8080/health |

---

## 🔌 API Schnellreferenz

```bash
# Alle Geräte
curl http://localhost:8080/api/devices

# Ein Gerät
curl http://localhost:8080/api/devices/heater_1

# Neues Gerät
curl -X POST http://localhost:8080/api/devices \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test_1",
    "name": "Test Device",
    "type": "shelly_plug",
    "ip": "10.0.0.150",
    "power": 2000,
    "priority": "MEDIUM"
  }'

# Gerät löschen
curl -X DELETE http://localhost:8080/api/devices/test_1

# Discovery
curl -X POST http://localhost:8080/api/devices/discover \
  -H "Content-Type: application/json" \
  -d '{"network": "10.0.0.0/24"}'

# Statistiken
curl http://localhost:8080/api/devices/stats
```

---

## ⚙️ Konfiguration

### `config/settings.yaml`
```yaml
optimization_interval: 30
hysteresis: 100

battery:
  min_soc: 20
  max_soc: 95
  priority_soc: 50

solax:
  ip: "10.0.0.100"
  port: 502

sdm630:
  ip: "10.0.0.101"
  port: 502
```

### `config/devices.yaml`
```yaml
devices:
  - id: "heater_1"
    name: "Heizstab"
    type: "shelly_1pm"
    ip: "10.0.0.150"
    power: 3000
    priority: "MEDIUM"
```

---

## 🐛 Troubleshooting

### Import Error
```bash
export PYTHONPATH=/opt/ems-core2.0:$PYTHONPATH
source venv/bin/activate
```

### Port bereits belegt
```bash
# Prüfe welcher Prozess Port 8080 nutzt
sudo lsof -i :8080

# Oder ändere Port in webui/app.py
```

### Service startet nicht
```bash
# Detaillierte Logs
sudo journalctl -u ems-core -xe

# Manuell starten (Debug)
cd /opt/ems-core2.0
source venv/bin/activate
python3 core/main.py
```

### Config Fehler
```bash
# Validiere YAML
python3 -c "import yaml; yaml.safe_load(open('config/settings.yaml'))"

# Validiere JSON
python3 -c "import json; json.load(open('config/schedules.json'))"
```

---

## 📊 Device Typen

| Type | Beschreibung |
|------|--------------|
| `shelly_plug` | Shelly Plug/Plug S |
| `shelly_1pm` | Shelly 1PM |
| `shelly_plus_1pm` | Shelly Plus 1PM |
| `shelly_pro_1pm` | Shelly Pro 1PM |
| `shelly_pro_3em` | Shelly Pro 3EM |
| `solax` | Solax Inverter |
| `sdm630` | SDM630 Meter |
| `sg_ready` | SG-Ready Heatpump |
| `generic` | Generic Device |

---

## 🎯 Prioritäten

| Priority | Wert | Beschreibung |
|----------|------|--------------|
| CRITICAL | 0 | Immer AN (z.B. Kühlschrank) |
| HIGH | 1 | Hohe Priorität |
| MEDIUM | 2 | Mittlere Priorität |
| LOW | 3 | Niedrige Priorität |
| OPTIONAL | 4 | Nur bei Überschuss |

---

## 📝 Python Code Snippets

### Device hinzufügen
```python
from core.device_manager import DeviceManager, DeviceConfig

manager = DeviceManager()

device = DeviceConfig(
    id="test_1",
    name="Test Device",
    type="shelly_plug",
    ip="10.0.0.150",
    power=2000,
    priority="MEDIUM"
)

manager.add_device(device)
```

### Schedule setzen
```python
from core.optimizer.scheduler import Scheduler

scheduler = Scheduler()

schedule = {
    "monday": [[10, 14], [20, 22]],
    "tuesday": [[8, 18]]
}

scheduler.add_schedule("heater_1", schedule)
```

### Switching Plan berechnen
```python
from core.optimizer.prioritizer import Prioritizer

prioritizer = Prioritizer()

# ... devices hinzufügen ...

plan = prioritizer.calculate_switching_plan(
    available_power=5000
)

print(plan)  # {'device_1': True, 'device_2': False, ...}
```

---

## 📱 Web UI Bedienung

### Gerät hinzufügen
1. Web UI öffnen: http://10.0.0.252:8080/devices
2. "➕ Gerät hinzufügen" klicken
3. Formular ausfüllen
4. "Speichern" klicken

### Discovery ausführen
1. "🔍 Discovery" klicken
2. Netzwerk eingeben (z.B. 10.0.0.0/24)
3. "Scan starten" klicken
4. Gefundene Geräte auswählen
5. "Importieren" klicken

### Gerät bearbeiten
1. In Device-Karte auf "✏️ Edit" klicken
2. Änderungen vornehmen
3. "Speichern" klicken

### Gerät löschen
1. In Device-Karte auf "🗑️ Delete" klicken
2. Bestätigen

---

## 🔍 Logs & Debugging

### Live Logs
```bash
# EMS Core
sudo journalctl -u ems-core -f

# Web UI (wenn manuell gestartet)
tail -f logs/webui.log

# Alle Logs
tail -f logs/*.log
```

### Debug Mode
```python
# In core/main.py oder webui/app.py
logging.basicConfig(level=logging.DEBUG)
```

### Test einzelnes Modul
```python
python3 << EOF
from core.device_manager import DeviceManager
manager = DeviceManager()
print(f"Loaded {len(manager.devices)} devices")
EOF
```

---

## 📚 Dokumentation

| Datei | Inhalt |
|-------|--------|
| `README.md` | Projekt-Übersicht & Installation |
| `DEVELOPMENT.md` | Entwickler-Dokumentation |
| `CHANGELOG.md` | Versionshistorie |
| `DEPLOYMENT_SUMMARY.md` | Was wurde implementiert |
| `QUICK_REFERENCE.md` | Diese Datei |

---

## ⚡ Performance Tipps

1. **Optimization Interval**: Standard 30s, bei vielen Geräten ggf. erhöhen
2. **Hysteresis**: Mindestens 100W um Flapping zu vermeiden
3. **Min Runtime**: Bei trägen Geräten (Heizstab, WP) nutzen
4. **Discovery**: Nur bei Bedarf ausführen, nicht automatisch

---

## 🔐 Sicherheit

```bash
# Berechtigungen setzen
chmod 644 config/*.yaml config/*.json
chmod 755 *.sh

# Service als eigener User
useradd -r -s /bin/false ems
chown -R ems:ems /opt/ems-core2.0
```

---

## 🎓 Beispiel-Workflow

```bash
# 1. System starten
sudo systemctl start ems-core

# 2. Web UI öffnen
firefox http://10.0.0.252:8080/devices

# 3. Discovery
# → Im Web UI auf "Discovery" klicken
# → Netzwerk scannen
# → Geräte importieren

# 4. Geräte konfigurieren
# → Leistungswerte eintragen
# → Prioritäten setzen
# → Räume zuordnen

# 5. Zeitpläne erstellen
# → "Schedules" Tab
# → Zeitfenster definieren

# 6. System beobachten
sudo journalctl -u ems-core -f

# 7. Bei Änderungen
sudo systemctl restart ems-core
```

---

## 💾 Backup & Restore

### Backup
```bash
# Komplett
tar -czf ems-backup-$(date +%Y%m%d).tar.gz config/ logs/

# Nur Config
cp -r config/ config.backup/
```

### Restore
```bash
# Komplett
tar -xzf ems-backup-20250119.tar.gz

# Nur Config
cp -r config.backup/* config/
```

---

## 🆘 Support

- **GitHub Issues**: https://github.com/svkux/ems-core2.0/issues
- **Documentation**: Siehe DEVELOPMENT.md
- **Logs**: `sudo journalctl -u ems-core -xe`

---

**Version:** 2.0.0  
**Datum:** 2025-01-19  
**Status:** ✅ Production Ready
