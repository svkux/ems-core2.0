# Troubleshooting Guide - EMS-Core v2.0

Lösungen für häufige Probleme und Fehler.

## 📋 Inhaltsverzeichnis

1. [Installation & Setup](#installation--setup)
2. [Energy Sources](#energy-sources)
3. [Device Control](#device-control)
4. [Web UI](#web-ui)
5. [Optimizer](#optimizer)
6. [Services](#services)
7. [Network & Connectivity](#network--connectivity)

---

## Installation & Setup

### Problem: `ModuleNotFoundError: No module named 'aiohttp'`

**Symptom:**
```
ModuleNotFoundError: No module named 'aiohttp'
```

**Lösung:**
```bash
cd /opt/ems-core
source venv/bin/activate
pip install aiohttp pymodbus
```

### Problem: Services starten nicht

**Symptom:**
```
Failed to start ems-optimizer.service
```

**Debug:**
```bash
# Check Service Status
sudo systemctl status ems-optimizer

# Check Logs
sudo journalctl -u ems-optimizer -n 50

# Test manuell
cd /opt/ems-core
/opt/ems-core/venv/bin/python3 -m core.main
```

**Häufige Ursachen:**
- Python Path falsch in Service-Datei
- Virtual Environment nicht aktiviert
- Fehlende Dependencies

---

## Energy Sources

### Problem: Battery SOC zeigt 0%

**Symptom:**
- Battery SOC Anzeige bleibt bei 0%
- Logs zeigen: `HA Battery SOC API error 404`

**Ursachen & Lösungen:**

#### 1. Falsche Entity ID (häufigster Fehler!)

**Check:**
```bash
cat /opt/ems-core/config/energy_sources.json | grep entity_id_soc
```

**Sollte sein:**
```json
"entity_id_soc": "sensor.batterie_soc_2"
```

**NICHT:**
```json
"entity_id_soc": "sensor.sensor.batterie_soc_2"  // ❌ Doppeltes "sensor."
```

**Fix:**
```bash
nano /opt/ems-core/config/energy_sources.json
# Korrigiere die Entity ID
# Speichern: Ctrl+X, Y, Enter

sudo systemctl restart ems-webui ems-optimizer
```

#### 2. Mehrere Config-Dateien

**Check:**
```bash
find /opt/ems-core -name "energy_sources.json"
```

**Sollte zeigen:**
```
/opt/ems-core/config/energy_sources.json
```

**Falls mehrere gefunden:**
```bash
# Lösche WebUI Config
rm /opt/ems-core/webui/config/energy_sources.json

# Stelle sicher dass app.py richtigen Pfad nutzt
nano /opt/ems-core/webui/app.py
# Zeile finden:
# energy_manager = EnergySourcesManager()
# Ändern zu:
# energy_manager = EnergySourcesManager(config_file='/opt/ems-core/config/energy_sources.json')
```

#### 3. Home Assistant Entity existiert nicht

**Test:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://YOUR_HA_IP:8123/api/states/sensor.batterie_soc_2
```

**Sollte zurückgeben:**
```json
{"entity_id":"sensor.batterie_soc_2","state":"80.0",...}
```

**Falls 404:**
- Entity existiert nicht in Home Assistant
- Prüfe Entity ID in HA Developer Tools

#### 4. Python Cache Problem

**Fix:**
```bash
sudo systemctl stop ems-webui ems-optimizer
find /opt/ems-core -name "*.pyc" -delete
find /opt/ems-core -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
sudo systemctl start ems-optimizer ems-webui
```

### Problem: PV/Grid Werte werden nicht aktualisiert

**Debug:**
```bash
# Check Logs
sudo journalctl -u ems-webui --since "1 minute ago" | grep -i "updating"

# Manueller Refresh Test
curl -X POST http://localhost:8080/api/energy/refresh
curl http://localhost:8080/api/energy/current
```

**Lösung:**
- Prüfe Entity IDs in Config
- Prüfe Home Assistant Token
- Prüfe Netzwerk-Erreichbarkeit

### Problem: Shelly 3EM Timeout

**Symptom:**
```
Failed to read from Shelly 3EM: timeout
```

**Lösungen:**
```bash
# Test Netzwerk
ping 10.0.0.14

# Test HTTP
curl http://10.0.0.14/status

# Check Firewall
sudo ufw status
```

---

## Device Control

### Problem: Device kann nicht gesteuert werden

**Symptom:**
```
Failed to execute on: Connection refused
```

**Debug:**
```bash
# Test Device Status
curl http://localhost:8080/api/devices/DEVICE_ID/status

# Test Device Control
curl -X POST http://localhost:8080/api/devices/DEVICE_ID/control \
  -H "Content-Type: application/json" \
  -d '{"action":"on"}'
```

**Lösungen:**

1. **IP-Adresse prüfen:**
```bash
# Ping Device
ping DEVICE_IP

# Test HTTP direkt
curl http://DEVICE_IP/relay/0?turn=on  # Gen1
curl http://DEVICE_IP/rpc/Switch.Set?id=0&on=true  # Gen2
```

2. **Device Type korrekt?**
- Shelly Gen1: `shelly_plug`, `shelly_1pm`
- Shelly Gen2: `shelly_plus_1pm`, `shelly_pro_1pm`

3. **Firewall:**
```bash
# Auf Shelly: Keine Zugangsbeschränkung aktiv?
# Auf Server: Port offen?
```

### Problem: SG-Ready funktioniert nicht

**Symptom:**
- Wärmepumpe reagiert nicht auf Befehle

**Check:**
1. Sind beide Relais (Relay1 + Relay2) korrekt konfiguriert?
2. Sind die Relais mit den SG-Ready Eingängen verbunden?
3. Unterstützt die Wärmepumpe SG-Ready?

**Test:**
```bash
# Manuell testen
# Relay 1 EIN, Relay 2 AUS = RECOMMENDED Mode
curl http://RELAY1_IP/relay/0?turn=on
curl http://RELAY2_IP/relay/0?turn=off
```

---

## Web UI

### Problem: WebUI lädt nicht / 404 Error

**Symptom:**
- Browser zeigt "Connection refused"
- Oder: 404 Not Found

**Debug:**
```bash
# Check ob Service läuft
sudo systemctl status ems-webui

# Check Port
sudo netstat -tlnp | grep 8080

# Check Logs
sudo journalctl -u ems-webui -n 50
```

**Lösungen:**

1. **Service nicht gestartet:**
```bash
sudo systemctl start ems-webui
```

2. **Port bereits belegt:**
```bash
# Finde Prozess
sudo lsof -i :8080

# Kill alten Prozess
pkill -f "python.*app.py"

# Restart Service
sudo systemctl restart ems-webui
```

3. **Firewall blockiert:**
```bash
sudo ufw allow 8080/tcp
```

### Problem: "Cannot GET /api/energy/current"

**Symptom:**
```
{"error": "Not found"}
```

**Lösung:**
Energy API wurde nicht geladen.

**Check:**
```bash
sudo journalctl -u ems-webui | grep "Energy Sources API"
```

**Sollte zeigen:**
```
✓ Energy Sources API registered
```

**Falls nicht:**
- Prüfe ob `energy_sources.py` existiert
- Prüfe Import-Fehler in Logs

### Problem: Auto-Refresh funktioniert nicht

**Symptom:**
- Timestamp aktualisiert sich
- Werte bleiben gleich

**Lösung:**
Frontend ruft Backend nicht auf.

**Check HTML:**
```bash
grep "updateValues.*triggerBackend" /opt/ems-core/webui/templates/energy_sources.html
```

**Sollte zeigen:**
```javascript
updateValues(true)  // ← mit triggerBackend=true
```

**Falls nicht:** Update `energy_sources.html` (siehe CHANGELOG.md)

---

## Optimizer

### Problem: Optimizer schaltet Devices nicht

**Symptom:**
- Optimizer läuft
- Devices werden nicht gesteuert

**Debug:**
```bash
# Check Optimizer Logs
sudo journalctl -u ems-optimizer -f

# Sollte zeigen:
# "💡 Available Power: XXW"
# "🎯 Executing X control actions..."
```

**Häufige Ursachen:**

1. **Keine verfügbare Power:**
```
Available Power: 0W
```
→ PV-Überschuss zu gering oder nicht vorhanden

2. **Keine steuerbaren Devices:**
```
Loaded 0 devices
```
→ Devices noch nicht konfiguriert

3. **Alle Devices bereits richtig geschaltet:**
```
✅ No control actions needed
```
→ System arbeitet korrekt!

### Problem: Optimizer crashed

**Symptom:**
```
ems-optimizer.service: Main process exited
```

**Debug:**
```bash
# Letzte Logs vor Crash
sudo journalctl -u ems-optimizer -n 100

# Manuell starten (zeigt Fehler direkt)
cd /opt/ems-core
/opt/ems-core/venv/bin/python3 -m core.main
```

**Häufige Fehler:**
- Import Error → Dependency fehlt
- Config Fehler → JSON Syntax Error
- Network Timeout → Shelly nicht erreichbar

---

## Services

### Problem: Service startet nicht automatisch beim Boot

**Check:**
```bash
systemctl is-enabled ems-optimizer
systemctl is-enabled ems-webui
```

**Sollte zeigen:** `enabled`

**Falls `disabled`:**
```bash
sudo systemctl enable ems-optimizer
sudo systemctl enable ems-webui
```

### Problem: Service restarte ständig

**Symptom:**
```
ems-optimizer.service: Start request repeated too quickly
```

**Bedeutet:** Service crashed sofort nach Start

**Debug:**
```bash
# Logs anschauen
sudo journalctl -u ems-optimizer -n 100

# Manuell starten um Fehler zu sehen
cd /opt/ems-core
/opt/ems-core/venv/bin/python3 -m core.main
```

---

## Network & Connectivity

### Problem: "Connection refused" zu Home Assistant

**Test:**
```bash
curl http://10.0.0.189:8123/api/
# Sollte HA API Info zurückgeben
```

**Falls Connection refused:**
- HA läuft nicht
- HA Firewall blockiert
- Falsche IP

### Problem: "Connection timeout" zu Shelly

**Test:**
```bash
ping 10.0.0.14
curl --max-time 5 http://10.0.0.14/status
```

**Lösungen:**
- Shelly eingeschaltet?
- Richtige IP?
- Netzwerk-Segment erreichbar?
- VLAN korrekt konfiguriert?

### Problem: DNS Resolution Failed

**Symptom:**
```
Failed to resolve hostname
```

**Fix:**
Verwende IP-Adressen statt Hostnamen in Config

---

## Logs & Debugging

### Nützliche Kommandos

```bash
# Alle Logs seit Start
sudo journalctl -u ems-optimizer --no-pager

# Live Logs (Follow)
sudo journalctl -u ems-optimizer -f

# Logs der letzten Stunde
sudo journalctl -u ems-optimizer --since "1 hour ago"

# Nur Errors
sudo journalctl -u ems-optimizer -p err

# Beide Services zusammen
sudo journalctl -u ems-optimizer -u ems-webui -f

# Nach Text suchen
sudo journalctl -u ems-webui | grep -i "battery"
```

### Debug Mode aktivieren

```bash
# In core/main.py oder webui/app.py
logging.basicConfig(
    level=logging.DEBUG,  # ← von INFO zu DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

---

## Emergency Recovery

### System nicht erreichbar / Alles crashed

**Hard Reset:**
```bash
# Stoppe alles
sudo systemctl stop ems-optimizer ems-webui

# Kill alle Python Prozesse
pkill -9 python3

# Lösche Cache
find /opt/ems-core -name "*.pyc" -delete
find /opt/ems-core -type d -name "__pycache__" -exec rm -rf {} +

# Config Backup laden
cp /opt/ems-core/config/energy_sources.json.backup /opt/ems-core/config/energy_sources.json

# Neu starten
sudo systemctl start ems-optimizer ems-webui
```

### Komplett-Neuinstallation

```bash
# Backup Config
cp -r /opt/ems-core/config /tmp/ems-config-backup

# Deinstallation
sudo systemctl stop ems-optimizer ems-webui
sudo systemctl disable ems-optimizer ems-webui
sudo rm /etc/systemd/system/ems-*.service
sudo systemctl daemon-reload

# Code löschen
sudo rm -rf /opt/ems-core

# Neuinstallation (siehe INSTALLATION.md)
# ...

# Config restore
cp -r /tmp/ems-config-backup/* /opt/ems-core/config/
```

---

## Support

### Weitere Hilfe benötigt?

1. **GitHub Issues:** https://github.com/svkux/ems-core2.0/issues
2. **Logs sammeln:**
   ```bash
   sudo journalctl -u ems-optimizer -u ems-webui --since "1 hour ago" > ems-logs.txt
   ```
3. **System Info:**
   ```bash
   uname -a
   python3 --version
   cat /opt/ems-core/config/energy_sources.json
   ```

### Debug-Checklist

- [ ] Logs geprüft
- [ ] Services laufen
- [ ] Netzwerk erreichbar
- [ ] Config korrekt (JSON valid)
- [ ] Dependencies installiert
- [ ] Python Cache gelöscht
- [ ] Manuelle Tests durchgeführt
