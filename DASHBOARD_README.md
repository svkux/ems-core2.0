# EMS-Core v2.0 - Dashboard

## 📊 Übersicht

Das Dashboard bietet eine Live-Übersicht über:
- **Energie-Erzeugung** (PV, Batterie)
- **Energie-Verbrauch** (Haus, Netz)
- **Energie-Fluss** Visualisierung
- **Geräte-Status** mit Live-Updates
- **Metriken** (Eigenverbrauch, Autarkie-Grad)

## 🎯 Features

### 1. Energy Cards
Zeigt aktuelle Werte für:
- ☀️ **PV Erzeugung** - Aktuelle PV-Leistung in W
- 🔌 **Netz** - Netzbezug (+) oder Einspeisung (-)
- 🔋 **Batterie** - Batterie-Leistung und SOC in %
- 🏠 **Verbrauch** - Hausverbrauch in W

### 2. Energie-Fluss Visualisierung
- Interaktive Darstellung der Energie-Ströme
- Zeigt Richtung und Stärke der Energie-Flüsse
- Icons für PV, Haus, Batterie, Netz

### 3. Metriken

**Eigenverbrauch:**
- Berechnung: `(PV genutzt / PV erzeugt) * 100`
- Zeigt wie viel der PV-Erzeugung direkt im Haus genutzt wird
- Progress Bar für visuelle Darstellung

**Autarkie-Grad:**
- Berechnung: `(PV genutzt / Hausverbrauch) * 100`
- Zeigt wie viel des Verbrauchs durch PV gedeckt wird
- Progress Bar für visuelle Darstellung

**Verfügbare Leistung:**
- PV-Überschuss für optionale Verbraucher
- Wird vom Optimizer für Entscheidungen genutzt

### 4. Geräte-Status
- Liste aller aktiven Geräte
- Status-Icons (On/Off)
- Prioritäts-Badges (CRITICAL, HIGH, MEDIUM, LOW)
- Nennleistung pro Gerät

## 🚀 Installation

### 1. Template-Dateien deployen

```bash
cd /opt/ems-core

# Kopiere Templates
cp /path/to/dashboard.html webui/templates/dashboard.html
cp /path/to/index.html webui/templates/index.html

# Setze Permissions
chmod 644 webui/templates/dashboard.html
chmod 644 webui/templates/index.html
```

### 2. WebUI Service neu starten

```bash
sudo systemctl restart ems-webui
```

### 3. Dashboard aufrufen

```
http://YOUR-IP:8080/dashboard
```

## 📡 API Endpoints

Das Dashboard nutzt folgenden Endpoint:

### GET `/api/dashboard/summary`

**Response:**
```json
{
  "success": true,
  "energy": {
    "pv_power": 3500.0,
    "grid_power": -1200.0,
    "battery_power": 500.0,
    "battery_soc": 85.0,
    "house_consumption": 1800.0,
    "available_power": 1200.0
  },
  "device_stats": {
    "total_devices": 5,
    "enabled_devices": 4,
    "controllable_devices": 4,
    "by_type": {
      "shelly_plug": 3,
      "sg_ready": 1
    },
    "by_priority": {
      "CRITICAL": 1,
      "HIGH": 2,
      "MEDIUM": 1
    }
  },
  "active_devices": [
    {
      "id": "shelly_plug_1",
      "name": "Waschmaschine",
      "type": "shelly_plug",
      "priority": "MEDIUM",
      "power": 2000
    }
  ],
  "timestamp": "2026-01-27T14:30:00"
}
```

## 🎨 Design

### Farbschema
- **Primary:** `#667eea` (Purple)
- **Accent:** `#764ba2` (Dark Purple)
- **Success:** `#10b981` (Green)
- **Warning:** `#fbbf24` (Yellow)
- **Info:** `#3b82f6` (Blue)
- **Danger:** `#ef4444` (Red)

### Responsive Design
- Desktop: Grid-Layout mit 2 Spalten
- Tablet: 1 Spalte
- Mobile: Optimiert für kleine Screens

### Icons
- ☀️ PV/Solar
- 🔌 Netz/Grid
- 🔋 Batterie
- 🏠 Haus/Verbrauch
- ♨️ Wärmepumpe
- ⚙️ Generic Device

## 🔄 Auto-Refresh

Das Dashboard aktualisiert sich automatisch:
- **Interval:** 5 Sekunden
- **Methode:** Fetch API (async)
- **Fehlerbehandlung:** Zeigt Fehlermeldung bei Connection-Loss

## 🛠️ Anpassungen

### Refresh-Intervall ändern

In `dashboard.html` Zeile ~550:
```javascript
// Auto-refresh every 5 seconds
updateInterval = setInterval(loadDashboard, 5000);

// Ändern zu z.B. 10 Sekunden:
updateInterval = setInterval(loadDashboard, 10000);
```

### Farben ändern

Im `<style>` Block am Anfang von `dashboard.html`:
```css
/* Primary Gradient */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Energy Card Colors */
.energy-card.pv {
    border-left: 4px solid #fbbf24; /* Gelb für PV */
}
```

### Device Icons anpassen

In `dashboard.html` Zeile ~490:
```javascript
function getDeviceIcon(type) {
    const icons = {
        'shelly_plug': '🔌',
        'sg_ready': '♨️',
        // Füge weitere hinzu:
        'custom_device': '🎯'
    };
    return icons[type] || '⚙️';
}
```

## 📊 Metriken-Formeln

### Eigenverbrauch (Self-Consumption)
```
PV_genutzt = min(PV_Power, House_Consumption)
Eigenverbrauch = (PV_genutzt / PV_Power) * 100
```

**Beispiel:**
- PV: 3000W
- Haus: 1500W
- PV_genutzt: 1500W
- Eigenverbrauch: (1500 / 3000) * 100 = **50%**

### Autarkie-Grad (Self-Sufficiency)
```
PV_genutzt = min(PV_Power, House_Consumption)
Autarkie = (PV_genutzt / House_Consumption) * 100
```

**Beispiel:**
- PV: 3000W
- Haus: 2000W
- PV_genutzt: 2000W
- Autarkie: (2000 / 2000) * 100 = **100%**

### Verfügbare Leistung
```
Wenn Grid < 0 (Einspeisung):
    Available = abs(Grid) - Hysterese
Sonst:
    Available = 0
```

## 🐛 Troubleshooting

### Dashboard zeigt keine Daten

**1. Prüfe API Endpoint:**
```bash
curl http://localhost:8080/api/dashboard/summary
```

**2. Prüfe WebUI Logs:**
```bash
sudo journalctl -u ems-webui -f
```

**3. Prüfe Browser Console:**
- F12 drücken
- Console Tab öffnen
- Nach Fehler-Meldungen suchen

### Fehlermeldung "Verbindungsfehler"

**Mögliche Ursachen:**
1. WebUI Service nicht gestartet
2. Port 8080 blockiert
3. Firewall-Regel

**Lösung:**
```bash
# Service Status prüfen
sudo systemctl status ems-webui

# Service neu starten
sudo systemctl restart ems-webui

# Port prüfen
sudo netstat -tulpn | grep 8080
```

### Geräte werden nicht angezeigt

**Prüfe Device Manager:**
```bash
cd /opt/ems-core
python3 core/device_manager.py
```

**Prüfe devices.yaml:**
```bash
cat config/devices.yaml
```

### Energy-Werte bleiben bei 0

**Prüfe Energy Sources:**
```bash
# Logs vom Optimizer
sudo journalctl -u ems-optimizer -f

# Prüfe Config
cat config/energy_sources.json
```

## 📈 Performance

### Optimierungen
- **Lazy Loading:** Bilder werden lazy geladen
- **Debouncing:** API Calls werden gebündelt
- **Caching:** Browser-Cache für statische Assets
- **Async:** Alle API Calls sind asynchron

### Load Times
- **Initial Load:** < 1s
- **Refresh:** < 500ms
- **Memory:** ~10-20 MB

## 🔒 Security

### Hinweise
- Dashboard ist **nicht authentifiziert**
- Zugriff nur im lokalen Netzwerk empfohlen
- Für öffentlichen Zugriff: Reverse Proxy mit Auth (nginx, Caddy)

### Beispiel nginx Config
```nginx
location /dashboard {
    auth_basic "EMS Dashboard";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://localhost:8080/dashboard;
}
```

## 🎯 Roadmap

### Nächste Features
- [ ] Historische Charts (24h, 7d, 30d)
- [ ] Export als CSV/PDF
- [ ] Push Notifications
- [ ] Wetter-Prognose Integration
- [ ] Mobile App (PWA)
- [ ] Dark Mode
- [ ] Multi-Language Support

## 💡 Tipps

### Best Practices
1. **Regelmäßige Updates:** System alle 5-10 Sekunden aktualisieren
2. **Error Handling:** Immer Fallback-Werte bereitstellen
3. **Performance:** Große Listen paginieren
4. **UX:** Loading-States für bessere User Experience

### Monitoring
- Nutze Browser DevTools für Performance-Analyse
- Prüfe Network Tab für API Response-Times
- Memory Profiler für Memory Leaks

## 📞 Support

Bei Fragen oder Problemen:
- **GitHub Issues:** https://github.com/svkux/ems-core2.0/issues
- **Dokumentation:** [README.md](../README.md)
- **Troubleshooting:** [TROUBLESHOOTING.md](../TROUBLESHOOTING.md)

---

**Version:** 2.0  
**Letzte Aktualisierung:** 27. Januar 2026  
**Autor:** svkux
