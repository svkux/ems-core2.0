# EMS-Core v2.0 - Bug Fixes & Improvements

**Datum:** 27. Januar 2026  
**Version:** 2.0.1

## 🐛 Behobene Bugs

### 1. DeviceConfig Inkonsistenzen in main.py

**Problem:**
- `main.py` verwendete `device.connection_params.get('ip')`, aber `DeviceConfig` hat direkt `device.ip`
- Führte zu AttributeError beim Zugriff auf Device-Daten

**Lösung:**
- Alle Zugriffe auf `device.connection_params.get('ip')` ersetzt durch `device.ip`
- Betroffen waren:
  - `get_device_current_state()` Zeile ~228
  - `execute_decisions()` Zeile ~267

**Code-Änderung:**
```python
# Vorher (FALSCH):
ip = device.connection_params.get('ip')

# Nachher (RICHTIG):
ip = device.ip
```

---

### 2. Power Attribut Inkonsistenz

**Problem:**
- `main.py` verwendete `device.power_rating`, aber `DeviceConfig` hat nur `device.power`
- Führte zu AttributeError bei Power-Berechnungen

**Lösung:**
- Alle Zugriffe auf `device.power_rating` ersetzt durch `device.power`
- Betroffen waren:
  - `make_control_decisions()` Zeile ~172
  - `decide_device_action()` Zeile ~193

**Code-Änderung:**
```python
# Vorher (FALSCH):
estimated_power = device.power_rating or 500

# Nachher (RICHTIG):
estimated_power = device.power or 500
```

---

## ✨ Verbesserungen

### app.py - Async Support

**Neu hinzugefügt:**
- `run_async()` Helper-Funktion für async Calls in sync Flask Routes
- Neuer `/api/dashboard/summary` Endpoint für Dashboard
- Neuer `/dashboard` Route für zukünftiges Dashboard
- Verbesserte Health Check mit Component Status

**Code:**
```python
def run_async(coro):
    """Helper um async Funktionen in sync Flask Routes zu benutzen"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)
```

---

### device_manager.py - Robustheit

**Verbesserte Validierung:**
- IP-Format Validierung (4 Oktette, 0-255)
- Port Range Check (1-65535)
- Bessere Error Messages

**Neue Features:**
- `get_devices_by_priority()` Methode
- `get_health_status()` Methode für Device Health Monitoring
- Erweiterte `search_devices()` mit room/category Support
- Besseres Error Handling mit exc_info=True für Debugging

**Health Status:**
```python
health = manager.get_health_status()
# Returns:
# {
#   'healthy': 5,    # Last seen < 5 min
#   'stale': 2,      # Last seen 5-60 min
#   'unknown': 1,    # Last seen > 60 min or never
#   'devices': [...]
# }
```

**Konstanten:**
```python
SUPPORTED_TYPES = [
    'shelly_plug', 'shelly_1pm', 'shelly_plus_1pm',
    'shelly_pro_1pm', 'shelly_pro_3em', 'shelly_3em',
    'solax', 'sdm630', 'sg_ready', 'generic'
]

VALID_PRIORITIES = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'OPTIONAL']
```

---

## 📝 Migration Guide

### 1. Backup erstellen
```bash
cd /opt/ems-core
cp core/main.py core/main.py.backup
cp core/device_manager.py core/device_manager.py.backup
cp webui/app.py webui/app.py.backup
```

### 2. Neue Dateien deployen
```bash
# Kopiere die neuen Dateien
cp /path/to/new/main.py core/main.py
cp /path/to/new/device_manager.py core/device_manager.py
cp /path/to/new/app.py webui/app.py
```

### 3. Services neu starten
```bash
sudo systemctl restart ems-optimizer
sudo systemctl restart ems-webui
```

### 4. Logs prüfen
```bash
# Check Optimizer
sudo journalctl -u ems-optimizer -f

# Check WebUI
sudo journalctl -u ems-webui -f
```

---

## 🧪 Testing

### Device Manager Test
```bash
cd /opt/ems-core
python3 core/device_manager.py
```

Erwartete Ausgabe:
```
============================================================
EMS Device Manager - Test
============================================================

📊 Statistics:
  Total Devices: X
  Enabled: X
  Controllable: X
  Total Power: XXXW

  By Type:
    shelly_plug: X
    ...

🏥 Health Status:
  Healthy: X
  Stale: X
  Unknown: X
============================================================
```

### Optimizer Test
```bash
cd /opt/ems-core
python3 core/main.py
```

Sollte keine AttributeError mehr werfen!

---

## 🔍 Bekannte Einschränkungen

1. **Async in Flask:** Der `run_async()` Helper ist eine Quick-Fix Lösung. Für Production sollte man zu Flask mit async Support (Quart) oder einen Background Worker (Celery) migrieren.

2. **Energy Manager Updates:** Aktuell werden Energy Sources nur vom Optimizer Loop updated. WebUI hat keinen eigenen Update-Mechanismus.

---

## 📚 Weitere Informationen

- Siehe [README.md](README.md) für allgemeine Dokumentation
- Siehe [TROUBLESHOOTING.md](TROUBLESHOOTING.md) für häufige Probleme
- GitHub Issues: https://github.com/svkux/ems-core2.0/issues

---

## ✅ Checklist für Deployment

- [ ] Backup erstellt
- [ ] Neue Dateien kopiert
- [ ] Services neu gestartet
- [ ] Logs gecheckt (keine Errors)
- [ ] Device Manager Test durchgeführt
- [ ] Optimizer läuft ohne Errors
- [ ] WebUI erreichbar
- [ ] Energy Sources werden aktualisiert
- [ ] Devices werden gesteuert

---

**Status:** ✅ Ready for Production  
**Getestet:** ⏳ Pending Real-World Testing  
**Breaking Changes:** ❌ Keine
