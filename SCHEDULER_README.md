# EMS-Core v2.0 - Scheduler

## 🕐 Übersicht

Der Scheduler ermöglicht zeitbasierte Steuerung von Geräten mit flexiblen Regeln:
- **Zeit-Fenster** - "Gerät nur zwischen 10-14 Uhr erlauben"
- **Zeit-Blockierung** - "Gerät nachts (0-6 Uhr) sperren"
- **Konditional** - "Gerät nur wenn PV > 2000W UND 11-16 Uhr"

## 📋 Schedule-Typen

### 1. TIME_WINDOW
Erlaubt Geräte-Steuerung nur innerhalb eines Zeit-Fensters.

**Beispiel:**
```
Waschmaschine nur Mo-Fr 10-14 Uhr
→ Innerhalb: allow/force_on
→ Außerhalb: force_off
```

### 2. TIME_BLOCK
Blockiert Geräte-Steuerung innerhalb eines Zeit-Fensters.

**Beispiel:**
```
Wärmepumpe nachts 22-06 Uhr sperren
→ Innerhalb: force_off
→ Außerhalb: allow
```

### 3. CONDITIONAL
Zeit-Fenster + Energie-Bedingungen.

**Beispiel:**
```
Pool-Pumpe nur bei PV > 2000W UND 11-16 Uhr
→ Zeit OK + Bedingung erfüllt: allow/force_on
→ Sonst: force_off
```

## 🏗️ Architektur

```
core/optimizer/
├── scheduler.py           # Scheduler Engine
├── schedule_manager.py    # CRUD für Schedules
└── ...

config/
└── schedules.json         # Schedule Definitionen

core/
└── main.py                # Integration (main_with_scheduler.py)
```

## 🚀 Installation

### 1. Dateien deployen

```bash
cd /opt/ems-core

# Erstelle optimizer Verzeichnis
mkdir -p core/optimizer

# Kopiere Scheduler-Dateien
cp /path/to/scheduler.py core/optimizer/scheduler.py
cp /path/to/schedule_manager.py core/optimizer/schedule_manager.py

# Ersetze main.py mit Scheduler-Version
cp core/main.py core/main.py.backup
cp /path/to/main_with_scheduler.py core/main.py

# Permissions
chmod 644 core/optimizer/scheduler.py
chmod 644 core/optimizer/schedule_manager.py
chmod 644 core/main.py
```

### 2. Optimizer neu starten

```bash
sudo systemctl restart ems-optimizer
```

### 3. Logs prüfen

```bash
sudo journalctl -u ems-optimizer -f

# Erwartete Ausgabe:
# ✅ Loaded X schedules
# ✅ Scheduler enabled
```

## 📝 Schedule Beispiele

### Beispiel 1: Waschmaschine werktags 10-14 Uhr

```json
{
  "id": "washer_weekday_window",
  "name": "Waschmaschine werktags 10-14 Uhr",
  "device_id": "shelly_plug_1",
  "schedule_type": "time_window",
  "enabled": true,
  "time_window": {
    "start_time": "10:00",
    "end_time": "14:00",
    "days": [0, 1, 2, 3, 4]
  },
  "action_in_window": "allow",
  "action_outside_window": "force_off",
  "description": "Waschmaschine nur werktags mittags erlauben"
}
```

### Beispiel 2: Wärmepumpe nachts blockieren

```json
{
  "id": "heatpump_night_block",
  "name": "Wärmepumpe nachts sperren",
  "device_id": "sg_ready_1",
  "schedule_type": "time_block",
  "enabled": true,
  "time_window": {
    "start_time": "22:00",
    "end_time": "06:00",
    "days": [0, 1, 2, 3, 4, 5, 6]
  },
  "action_in_window": "force_off",
  "action_outside_window": "allow",
  "description": "Wärmepumpe nachts 22-06 Uhr deaktiviert"
}
```

### Beispiel 3: Pool-Pumpe nur bei viel PV

```json
{
  "id": "pool_pv_conditional",
  "name": "Pool-Pumpe nur bei PV > 2000W",
  "device_id": "shelly_plug_pool",
  "schedule_type": "conditional",
  "enabled": true,
  "time_window": {
    "start_time": "11:00",
    "end_time": "16:00",
    "days": [0, 1, 2, 3, 4, 5, 6]
  },
  "conditions": [
    {
      "parameter": "pv_power",
      "operator": ">",
      "value": 2000.0
    }
  ],
  "action_in_window": "force_on",
  "action_outside_window": "force_off",
  "description": "Pool-Pumpe nur mittags bei genug PV"
}
```

### Beispiel 4: Priority Override

```json
{
  "id": "washer_high_priority_noon",
  "name": "Waschmaschine mittags HIGH Priority",
  "device_id": "shelly_plug_1",
  "schedule_type": "time_window",
  "enabled": true,
  "time_window": {
    "start_time": "12:00",
    "end_time": "14:00",
    "days": [0, 1, 2, 3, 4, 5, 6]
  },
  "action_in_window": "allow",
  "action_outside_window": "allow",
  "override_priority": true,
  "priority_in_window": "HIGH",
  "description": "Waschmaschine mittags auf HIGH Priority setzen"
}
```

## ⚙️ Konfiguration

### config/schedules.json

```json
{
  "schedules": [
    {
      "id": "schedule_1",
      "name": "Mein Schedule",
      "device_id": "device_1",
      "schedule_type": "time_window",
      ...
    }
  ]
}
```

### Felder

| Feld | Typ | Pflicht | Beschreibung |
|------|-----|---------|--------------|
| `id` | string | ✅ | Eindeutige ID |
| `name` | string | ✅ | Anzeige-Name |
| `device_id` | string | ✅ | Ziel-Gerät ID |
| `schedule_type` | enum | ✅ | time_window, time_block, conditional |
| `enabled` | boolean | ❌ | Aktiv (default: true) |
| `time_window` | object | ✅ | Zeit-Fenster Definition |
| `conditions` | array | ❌ | Für conditional Typ |
| `action_in_window` | enum | ❌ | allow, force_on, force_off (default: allow) |
| `action_outside_window` | enum | ❌ | allow, force_off (default: allow) |
| `override_priority` | boolean | ❌ | Priority überschreiben? |
| `priority_in_window` | enum | ❌ | CRITICAL, HIGH, MEDIUM, LOW |
| `description` | string | ❌ | Beschreibung |

### time_window

```json
{
  "start_time": "10:00",      // HH:MM Format
  "end_time": "14:00",        // HH:MM Format
  "days": [0, 1, 2, 3, 4]     // 0=Mo, 6=So
}
```

**Overnight Windows:**
```json
{
  "start_time": "22:00",
  "end_time": "06:00",        // Über Mitternacht!
  "days": [0, 1, 2, 3, 4, 5, 6]
}
```

### conditions

```json
{
  "conditions": [
    {
      "parameter": "pv_power",      // pv_power, battery_soc, grid_power
      "operator": ">",              // >, <, >=, <=, ==, !=
      "value": 2000.0
    },
    {
      "parameter": "battery_soc",
      "operator": ">=",
      "value": 50.0
    }
  ]
}
```

**Verfügbare Parameter:**
- `pv_power` - PV-Erzeugung in W
- `grid_power` - Netz-Leistung in W (negativ = Einspeisung)
- `battery_power` - Batterie-Leistung in W
- `battery_soc` - Batterie SOC in %
- `house_consumption` - Hausverbrauch in W

## 🔄 Entscheidungs-Logik

### Prioritäten

1. **Schedule force_off** → höchste Priorität
2. **Schedule force_on** → zweithöchste
3. **Device Priority** (CRITICAL → OPTIONAL)
4. **Schedule allow** → niedrigste

### Beispiel-Szenario

**Device:** Waschmaschine (Priority: MEDIUM)  
**PV:** 3000W  
**Schedule:** force_off außerhalb 10-14 Uhr  
**Zeit:** 09:30 Uhr

**Entscheidung:**
1. Schedule prüfen → außerhalb Fenster
2. Action: force_off
3. **Result: AUS** (trotz genug PV!)

### Mehrere Schedules

Wenn mehrere Schedules auf ein Device zutreffen:
```
force_off > force_on > allow
```

**Beispiel:**
- Schedule 1: force_on (wegen PV)
- Schedule 2: force_off (wegen Uhrzeit)
- **Result: force_off gewinnt**

## 📊 Monitoring

### Logs

```bash
# Schedule-Entscheidungen im Log
sudo journalctl -u ems-optimizer -f

# Beispiel-Ausgabe:
# 🕐 Schedule: Waschmaschine werktags 10-14 Uhr - outside time window
# ✅ 🕐 Waschmaschine -> OFF | Reason: Schedule force_off
```

### Status Prüfen

```python
from core.optimizer.scheduler import Scheduler
from core.optimizer.schedule_manager import ScheduleManager

manager = ScheduleManager()
scheduler = Scheduler(manager)

# Alle aktiven Schedules
active = scheduler.get_all_active_schedules()

for item in active:
    print(f"Schedule: {item['schedule'].name}")
    print(f"In Window: {item['in_window']}")
    print(f"Decision: {item['decision']}")
```

## 🧪 Testing

### Test Scheduler

```bash
cd /opt/ems-core
python3 core/optimizer/scheduler.py
```

**Erwartete Ausgabe:**
```
============================================================
EMS Scheduler - Test
============================================================

09:00:
  Allowed: False
  Action: force_off
  Reason: Schedule 'Waschmaschine 10-14 Uhr' - outside time window

12:00:
  Allowed: True
  Action: allow
  Reason: Schedule 'Waschmaschine 10-14 Uhr' - inside time window

15:00:
  Allowed: False
  Action: force_off
  Reason: Schedule 'Waschmaschine 10-14 Uhr' - outside time window
```

### Test Schedule Manager

```bash
python3 core/optimizer/schedule_manager.py
```

## 🐛 Troubleshooting

### Schedule wird nicht angewendet

**1. Prüfe enabled Flag:**
```bash
cat config/schedules.json | grep -A 5 "schedule_id"
```

**2. Prüfe Device ID:**
```bash
# Muss mit device_id in devices.yaml übereinstimmen
cat config/devices.yaml | grep "id:"
```

**3. Prüfe Logs:**
```bash
sudo journalctl -u ems-optimizer -f | grep Schedule
```

### Conditional Schedule funktioniert nicht

**1. Prüfe Parameter-Namen:**
```python
# Muss exakt sein:
"pv_power"       # ✅ Richtig
"pv_generation"  # ❌ Falsch
```

**2. Prüfe Energy Data:**
```bash
# Im Log sollte stehen:
# 📊 Updating energy data...
# ==> PV=XXXXw, Grid=XXXXw, ...
```

**3. Prüfe Operator:**
```python
# Gültige Operatoren:
">", "<", ">=", "<=", "==", "!="
```

### Overnight Window Problem

**Problem:** Window 22:00-06:00 funktioniert nicht richtig.

**Lösung:** Code handhabt das automatisch:
```python
# start_time > end_time → Overnight behandeln
if time_window.start_time > time_window.end_time:
    # OK: 22:00 - 06:00 wird erkannt
```

## 🎯 Best Practices

### 1. Start mit einfachen TIME_WINDOW

Beginne mit simplen Zeitfenstern bevor du CONDITIONAL nutzt:
```json
{
  "schedule_type": "time_window",
  "time_window": {
    "start_time": "10:00",
    "end_time": "16:00",
    "days": [0, 1, 2, 3, 4, 5, 6]
  },
  "action_in_window": "allow",
  "action_outside_window": "force_off"
}
```

### 2. Test Schedules einzeln

Aktiviere nur 1 Schedule pro Device zum Testen:
```json
{
  "enabled": true  // Nur dieser eine
}
```

### 3. Nutze aussagekräftige Namen

```json
// ✅ Gut
"name": "Waschmaschine werktags 10-14 Uhr"

// ❌ Schlecht
"name": "Schedule 1"
```

### 4. Dokumentiere mit description

```json
"description": "Waschmaschine nur werktags mittags erlauben, um Netz-Bezug zu vermeiden"
```

### 5. Priority Override sparsam nutzen

Überschreibe Priority nur wenn wirklich nötig:
```json
{
  "override_priority": true,
  "priority_in_window": "HIGH"
  // Nur wenn Device außerhalb des Fensters MEDIUM ist,
  // aber innerhalb HIGH sein soll
}
```

## 🔒 Sicherheit

### Critical Devices

CRITICAL Devices sollten **keine** force_off Schedules haben:
```json
// ❌ Gefährlich für CRITICAL Devices
{
  "device_id": "critical_device_1",
  "action_in_window": "force_off"  // Kann kritisches Gerät ausschalten!
}
```

### Backup Config

```bash
# Vor Schedule-Änderungen
cp config/schedules.json config/schedules.json.backup
```

## 📈 Performance

- **Overhead:** ~5ms pro Schedule pro Cycle
- **Memory:** ~1KB pro Schedule
- **Empfehlung:** Max 50 Schedules pro System

## 🚧 Roadmap

### Geplante Features
- [ ] Jahreszeiten-Support (Sommer/Winter)
- [ ] Feiertage-Erkennung
- [ ] Wetter-basierte Conditions
- [ ] Schedule Templates
- [ ] Web UI für Schedule Management
- [ ] Schedule Import/Export
- [ ] History Log (welcher Schedule wann ausgelöst)

## 📚 API Integration

### REST API (TODO)

```bash
# GET /api/schedules
curl http://localhost:8080/api/schedules

# POST /api/schedules
curl -X POST http://localhost:8080/api/schedules \
  -H "Content-Type: application/json" \
  -d @schedule.json

# PUT /api/schedules/{id}
curl -X PUT http://localhost:8080/api/schedules/schedule_1 \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}'

# DELETE /api/schedules/{id}
curl -X DELETE http://localhost:8080/api/schedules/schedule_1
```

## 💡 Beispiel Use-Cases

### 1. PV-Optimierung
```
Pool-Pumpe nur bei viel Sonne (11-16 Uhr, PV > 2000W)
→ CONDITIONAL Schedule
```

### 2. Lastspitzen vermeiden
```
Wärmepumpe nachts (22-06 Uhr) deaktivieren
→ TIME_BLOCK Schedule
```

### 3. Tarif-Optimierung
```
E-Auto laden nur nachts (23-07 Uhr) bei günstigem Tarif
→ TIME_WINDOW Schedule
```

### 4. Komfort
```
Heizung werktags ab 06:00 auf HIGH Priority
→ TIME_WINDOW mit Priority Override
```

---

**Version:** 2.0  
**Letzte Aktualisierung:** 27. Januar 2026  
**Autor:** svkux
