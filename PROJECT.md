# EMS-Core v2.0 - Standalone Energy Management

## 🎯 Projekt-Ziel
Eigenständiges Energie-Management-System ohne Home Assistant.
Optimiert PV-Eigenverbrauch durch intelligente Verbraucher-Steuerung.

## 📋 Architektur
```
EMS-Core (LXC Container)
├── Device Discovery (Shelly, Solax, SDM630)
├── Web UI (Port 8080)
├── Controller (direkte Geräte-Steuerung)
├── Optimizer (Priorisierung, Zeitpläne)
└── SG-Ready (Wärmepumpen-Steuerung)
```

## ✅ Implementierter Stand

### Module (fertig):
1. **Device Discovery** (`core/integrations/discovery.py`)
   - Automatisches Netzwerk-Scannen
   - Erkennt: Shelly (Gen1/2/Pro), Solax (Modbus), SDM630
   
2. **Web UI** (`webui/app.py` + `templates/index.html`)
   - Tabs: Discovery, Config, Prioritäten, Zeitpläne, Manuell
   - Drag & Drop Prioritäten
   
3. **Controller** (`core/controllers/*.py`)
   - ShellyController (Gen1/Gen2/Plus/Pro)
   - ShellyProEM3Controller (3-Phasen Meter)
   - SolaxModbusController (PV, Batterie, Grid)
   - SDM630ModbusController (Smartmeter)
   
4. **SG-Ready** (`core/controllers/sg_ready.py`)
   - 4 Modi: LOCKED, NORMAL, COMFORT, FORCED
   - Wärmepumpen-Steuerung via 2 Shelly-Relais

### Module (fehlen noch):
- `core/main.py` - Haupt-Optimizer
- `core/optimizer/scheduler.py` - Zeitpläne
- `core/optimizer/prioritizer.py` - Prioritäts-Logik

## 🔧 Installation
Siehe: `install_ems_complete.sh`

## 🌐 Web UI
http://10.0.0.252:8080

## 📝 Konfiguration
- `config/settings.yaml` - System-Einstellungen
- `config/devices.yaml` - Geräte-Konfiguration

## 🎯 Use Cases
1. Maximale Eigenverbrauch ✅
2. Netzbezug minimieren ✅
3. Batterie schonen ✅
4. Stromkosten optimieren ✅

## 🔌 Geräte
- ~15 Shelly Plugs/1PM
- 1x Shelly Pro 3EM (Wärmepumpen-Messung)
- 2x Shelly (SG-Ready Relais)
- 1x Solax Wechselrichter (Modbus)
- 1x SDM630 Simulator (Wallbox-Steuerung)
- 1x Aira Wärmepumpe (SG-Ready)

## 📊 Prioritäten (Nutzer-definiert)
Reihenfolge wird via Drag & Drop im Web UI festgelegt

## ⏰ Zeitpläne
Format: JSON mit Zeitfenstern pro Verbraucher
```json
{
  "device_id": "heizstab",
  "schedule": {
    "monday": [[10, 14], [20, 22]],
    "tuesday": [[10, 14]]
  }
}
```

## 🔄 Nächste Schritte
1. Main Optimizer implementieren
2. Scheduler-System
3. Tests mit echten Geräten
4. Fine-Tuning Algorithmen

## 📞 Support
Bei Fragen zum Code: Siehe Artifacts in Claude Chat

---
Stand: 2026-01-10
Version: 2.0.0-dev
