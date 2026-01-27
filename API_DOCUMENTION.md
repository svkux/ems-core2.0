# API Documentation - EMS-Core v2.0

REST API Dokumentation für EMS-Core.

**Base URL:** `http://YOUR-IP:8080`

---

## 📋 Inhaltsverzeichnis

1. [Energy API](#energy-api)
2. [Device API](#device-api)
3. [System API](#system-api)
4. [Error Handling](#error-handling)
5. [Examples](#examples)

---

## Energy API

Verwaltung von Energy Sources (PV, Grid, Battery) und Abruf aktueller Energiedaten.

### GET /api/energy/sources

Hole alle konfigurierten Energy Sources.

**Response:**
```json
{
  "success": true,
  "sources": [
    {
      "id": "pv_generation_1769422770",
      "name": "Growatt",
      "type": "pv_generation",
      "provider": "home_assistant",
      "config": {
        "url": "http://10.0.0.189:8123",
        "token": "...",
        "entity_id": "sensor.pv_power"
      },
      "enabled": true,
      "last_value": 3500.0,
      "last_update": "2026-01-27T10:00:00"
    }
  ],
  "count": 3
}
```

### POST /api/energy/sources

Füge eine neue Energy Source hinzu.

**Request Body:**
```json
{
  "name": "Meine PV",
  "type": "pv_generation",
  "provider": "home_assistant",
  "config": {
    "url": "http://10.0.0.189:8123",
    "token": "YOUR_HA_TOKEN",
    "entity_id": "sensor.pv_power"
  },
  "enabled": true
}
```

**Response:**
```json
{
  "success": true,
  "source": {
    "id": "pv_generation_1769500000",
    "name": "Meine PV",
    ...
  }
}
```

**Battery Source (mit SOC):**
```json
{
  "name": "Batterie",
  "type": "battery",
  "provider": "home_assistant",
  "config": {
    "url": "http://10.0.0.189:8123",
    "token": "YOUR_HA_TOKEN",
    "entity_id": "sensor.battery_power",
    "entity_id_soc": "sensor.battery_soc"
  },
  "enabled": true
}
```

### DELETE /api/energy/sources/{source_id}

Lösche eine Energy Source.

**Response:**
```json
{
  "success": true
}
```

### POST /api/energy/sources/{source_id}/toggle

Aktiviere/Deaktiviere eine Energy Source.

**Request Body:**
```json
{
  "enabled": true
}
```

**Response:**
```json
{
  "success": true
}
```

### GET /api/energy/current

Hole aktuelle Energiedaten (Echtzeit).

**Response:**
```json
{
  "pv_power": 3500.0,
  "grid_power": -1200.0,
  "battery_power": 500.0,
  "battery_soc": 80.0,
  "house_consumption": 2800.0,
  "available_power": 1200.0
}
```

**Felder:**
- `pv_power`: PV-Erzeugung in Watt
- `grid_power`: Netz (+Bezug, -Einspeisung) in Watt
- `battery_power`: Battery (+Laden, -Entladen) in Watt
- `battery_soc`: State of Charge in %
- `house_consumption`: Gesamtverbrauch in Watt
- `available_power`: Verfügbare Überschussleistung in Watt

### POST /api/energy/refresh

Triggere manuelle Aktualisierung aller Energy Sources.

**Response:**
```json
{
  "success": true,
  "data": {
    "pv_power": 3500.0,
    ...
  }
}
```

---

## Device API

Verwaltung und Steuerung von Devices (Shelly, SG-Ready, etc.).

### GET /api/devices

Hole alle Devices.

**Response:**
```json
{
  "success": true,
  "devices": [
    {
      "id": "device_001",
      "name": "Waschmaschine",
      "type": "shelly_plug",
      "category": "appliance",
      "priority": "MEDIUM",
      "power_rating": 2000,
      "can_control": true,
      "enabled": true,
      "connection_params": {
        "ip": "10.0.0.20"
      }
    }
  ],
  "count": 5
}
```

### GET /api/devices/{device_id}

Hole ein einzelnes Device.

**Response:**
```json
{
  "success": true,
  "device": {
    "id": "device_001",
    "name": "Waschmaschine",
    ...
  }
}
```

### POST /api/devices

Füge neues Device hinzu.

**Request Body:**
```json
{
  "name": "Waschmaschine",
  "type": "shelly_plug",
  "category": "appliance",
  "priority": "MEDIUM",
  "power_rating": 2000,
  "can_control": true,
  "enabled": true,
  "connection_params": {
    "ip": "10.0.0.20"
  }
}
```

**Device Types:**
- `shelly_plug` - Shelly Plug (Gen1)
- `shelly_1pm` - Shelly 1PM (Gen1)
- `shelly_plus_1pm` - Shelly Plus 1PM (Gen2)
- `shelly_pro_1pm` - Shelly Pro 1PM (Gen2)
- `sg_ready` - SG-Ready Wärmepumpe

**Categories:**
- `appliance` - Haushaltsgerät
- `heating` - Heizung
- `cooling` - Kühlung
- `ev_charging` - E-Auto Laden
- `lighting` - Beleuchtung
- `entertainment` - Unterhaltung
- `monitoring` - Monitoring
- `other` - Sonstiges

**Priorities:**
- `CRITICAL` - Immer AN
- `HIGH` - Hohe Priorität
- `MEDIUM` - Mittlere Priorität
- `LOW` - Niedrige Priorität
- `OPTIONAL` - Nur bei Überschuss

**Response:**
```json
{
  "success": true,
  "message": "Device added successfully",
  "device": {...}
}
```

### PUT /api/devices/{device_id}

Update Device.

**Request Body:** (nur Felder die geändert werden sollen)
```json
{
  "priority": "HIGH",
  "enabled": false
}
```

**Response:**
```json
{
  "success": true,
  "message": "Device updated successfully",
  "device": {...}
}
```

### DELETE /api/devices/{device_id}

Lösche Device.

**Response:**
```json
{
  "success": true,
  "message": "Device deleted successfully"
}
```

### POST /api/devices/{device_id}/control

Steuere Device (Ein/Aus/Toggle).

**Request Body:**
```json
{
  "action": "on"
}
```

**Actions:**
- `on` - Einschalten
- `off` - Ausschalten
- `toggle` - Umschalten

**Response:**
```json
{
  "success": true,
  "message": "Device device_001 turned on",
  "device_id": "device_001",
  "action": "on"
}
```

### GET /api/devices/{device_id}/status

Hole Live-Status von Hardware.

**Response:**
```json
{
  "success": true,
  "device_id": "device_001",
  "status": {
    "online": true,
    "state": "on",
    "power": 1850.5,
    "voltage": 230.0,
    "temperature": 45.2,
    "overtemperature": false
  }
}
```

### GET /api/devices/{device_id}/power

Hole nur aktuellen Power-Wert (schneller als vollständiger Status).

**Response:**
```json
{
  "success": true,
  "device_id": "device_001",
  "power": 1850.5,
  "unit": "W"
}
```

### POST /api/devices/control/batch

Steuere mehrere Devices gleichzeitig.

**Request Body:**
```json
{
  "device_ids": ["device_001", "device_002", "device_003"],
  "action": "off"
}
```

**Response:**
```json
{
  "success": true,
  "controlled": ["device_001", "device_002"],
  "failed": ["device_003: Connection timeout"],
  "count_success": 2,
  "count_failed": 1
}
```

### GET /api/devices/search

Suche Devices.

**Query Parameters:**
- `q` - Suchbegriff

**Example:**
```
GET /api/devices/search?q=wasch
```

**Response:**
```json
{
  "success": true,
  "results": [...],
  "count": 1
}
```

### GET /api/devices/filter

Filtere Devices.

**Query Parameters:**
- `type` - Device Type
- `category` - Kategorie
- `priority` - Priorität
- `enabled` - true/false

**Example:**
```
GET /api/devices/filter?category=appliance&priority=MEDIUM
```

**Response:**
```json
{
  "success": true,
  "devices": [...],
  "count": 3
}
```

### GET /api/devices/stats

Hole Device-Statistiken.

**Response:**
```json
{
  "success": true,
  "statistics": {
    "total_devices": 5,
    "enabled_devices": 4,
    "controllable_devices": 4,
    "by_type": {
      "shelly_plug": 3,
      "sg_ready": 1
    },
    "by_priority": {
      "CRITICAL": 1,
      "HIGH": 1,
      "MEDIUM": 2,
      "LOW": 1
    }
  }
}
```

### GET /api/devices/types

Hole verfügbare Device-Typen.

**Response:**
```json
{
  "success": true,
  "types": [
    {"value": "shelly_plug", "label": "Shelly Plug"},
    {"value": "shelly_1pm", "label": "Shelly 1PM"},
    ...
  ]
}
```

### GET /api/devices/priorities

Hole verfügbare Prioritäten.

**Response:**
```json
{
  "success": true,
  "priorities": [
    {
      "value": "CRITICAL",
      "label": "Critical",
      "description": "Always ON"
    },
    ...
  ]
}
```

### GET /api/devices/categories

Hole verfügbare Kategorien.

**Response:**
```json
{
  "success": true,
  "categories": [
    {"value": "appliance", "label": "Appliance"},
    {"value": "heating", "label": "Heating"},
    ...
  ]
}
```

---

## System API

### GET /health

Health Check Endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "EMS-Core Web UI",
  "version": "2.0"
}
```

### GET /api/devices/export

Exportiere alle Devices als JSON.

**Response:**
```json
{
  "success": true,
  "data": {
    "devices": [...],
    "exported_at": "2026-01-27T10:00:00",
    "version": "2.0"
  }
}
```

---

## Error Handling

### Standard Error Response

```json
{
  "success": false,
  "error": "Error message here"
}
```

### HTTP Status Codes

- `200` - OK
- `400` - Bad Request (Invalid input)
- `404` - Not Found (Resource doesn't exist)
- `500` - Internal Server Error
- `501` - Not Implemented (Feature not available)

### Error Examples

**404 - Device Not Found:**
```json
{
  "success": false,
  "error": "Device not found"
}
```

**400 - Invalid Input:**
```json
{
  "success": false,
  "error": "Invalid device type"
}
```

**500 - Control Failed:**
```json
{
  "success": false,
  "error": "Failed to execute on: Connection timeout"
}
```

---

## Examples

### Example 1: Vollständiger Device Workflow

```bash
# 1. Device hinzufügen
curl -X POST http://10.0.0.156:8080/api/devices \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Waschmaschine",
    "type": "shelly_plug",
    "category": "appliance",
    "priority": "MEDIUM",
    "power_rating": 2000,
    "can_control": true,
    "enabled": true,
    "connection_params": {"ip": "10.0.0.20"}
  }'

# 2. Device einschalten
curl -X POST http://10.0.0.156:8080/api/devices/device_001/control \
  -H "Content-Type: application/json" \
  -d '{"action": "on"}'

# 3. Status prüfen
curl http://10.0.0.156:8080/api/devices/device_001/status

# 4. Power messen
curl http://10.0.0.156:8080/api/devices/device_001/power

# 5. Device ausschalten
curl -X POST http://10.0.0.156:8080/api/devices/device_001/control \
  -H "Content-Type: application/json" \
  -d '{"action": "off"}'
```

### Example 2: Energy Monitoring

```bash
# 1. Aktuelle Werte abrufen
curl http://10.0.0.156:8080/api/energy/current

# 2. Manuelle Aktualisierung
curl -X POST http://10.0.0.156:8080/api/energy/refresh

# 3. Alle Sources anzeigen
curl http://10.0.0.156:8080/api/energy/sources
```

### Example 3: Battery Source hinzufügen

```bash
curl -X POST http://10.0.0.156:8080/api/energy/sources \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Batterie",
    "type": "battery",
    "provider": "home_assistant",
    "config": {
      "url": "http://10.0.0.189:8123",
      "token": "YOUR_HA_TOKEN",
      "entity_id": "sensor.battery_power",
      "entity_id_soc": "sensor.battery_soc"
    },
    "enabled": true
  }'
```

### Example 4: JavaScript Integration

```javascript
// Energy Data abrufen
async function getEnergyData() {
  const response = await fetch('http://10.0.0.156:8080/api/energy/current');
  const data = await response.json();
  
  console.log('PV Power:', data.pv_power, 'W');
  console.log('Battery SOC:', data.battery_soc, '%');
  console.log('House Consumption:', data.house_consumption, 'W');
}

// Device steuern
async function controlDevice(deviceId, action) {
  const response = await fetch(`http://10.0.0.156:8080/api/devices/${deviceId}/control`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({action})
  });
  
  const result = await response.json();
  console.log(result.message);
}

// Verwendung
getEnergyData();
controlDevice('device_001', 'on');
```

### Example 5: Python Integration

```python
import requests

BASE_URL = "http://10.0.0.156:8080"

# Energy Data
response = requests.get(f"{BASE_URL}/api/energy/current")
data = response.json()
print(f"PV: {data['pv_power']}W, Battery SOC: {data['battery_soc']}%")

# Device Control
response = requests.post(
    f"{BASE_URL}/api/devices/device_001/control",
    json={"action": "on"}
)
print(response.json()['message'])
```

---

## Rate Limiting

Aktuell gibt es **kein Rate Limiting**. Bei produktiver Nutzung sollte dies implementiert werden.

## Authentication

Aktuell gibt es **keine Authentication**. Alle API Endpoints sind öffentlich zugänglich.

**⚠️ Sicherheitshinweis:** In Produktionsumgebungen sollte ein Login-System implementiert werden!

---

## Changelog

- **v2.0.0** (2026-01-27) - Initial API Release
  - Energy API vollständig
  - Device API vollständig
  - System API basic

---

## Support

Bei Fragen zur API:
- Siehe [README.md](README.md)
- Siehe [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- GitHub Issues: https://github.com/svkux/ems-core2.0/issues
