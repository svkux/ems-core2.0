# Installation Guide - EMS-Core v2.0

Vollständige Installationsanleitung für EMS-Core v2.0.

## 📋 Voraussetzungen

### System
- **OS:** Ubuntu 20.04+ oder Debian 11+
- **RAM:** Minimum 512 MB, empfohlen 1 GB+
- **Disk:** Minimum 1 GB freier Speicher
- **Python:** Version 3.8 oder höher
- **Netzwerk:** Zugriff auf Shelly Devices, Home Assistant (optional)

### Zugriffsrechte
- Root oder sudo Zugriff erforderlich für Systemd Services

## 🚀 Schritt 1: System Vorbereitung

```bash
# System aktualisieren
sudo apt update
sudo apt upgrade -y

# Python und Dependencies installieren
sudo apt install -y python3 python3-pip python3-venv git

# Optional: Build-Tools für pymodbus
sudo apt install -y build-essential python3-dev
```

## 📦 Schritt 2: Repository Klonen

```bash
# Erstelle Installations-Verzeichnis
sudo mkdir -p /opt/ems-core
cd /opt/ems-core

# Clone Repository
git clone https://github.com/svkux/ems-core2.0.git .

# Oder: Download als ZIP und entpacken
wget https://github.com/svkux/ems-core2.0/archive/refs/heads/main.zip
unzip main.zip
mv ems-core2.0-main/* .
```

## 🐍 Schritt 3: Python Virtual Environment

```bash
cd /opt/ems-core

# Virtual Environment erstellen
python3 -m venv venv

# Aktivieren
source venv/bin/activate

# Dependencies installieren
pip install --upgrade pip
pip install -r requirements.txt
```

### requirements.txt sollte enthalten:

```
Flask>=2.3.0
aiohttp>=3.9.0
pymodbus>=3.5.0
pyyaml>=6.0
```

Falls `requirements.txt` fehlt, erstelle sie:

```bash
cat > requirements.txt << EOF
Flask>=2.3.0
aiohttp>=3.9.0
pymodbus>=3.5.0
pyyaml>=6.0
EOF

pip install -r requirements.txt
```

## 📁 Schritt 4: Verzeichnis-Struktur

```bash
# Erstelle notwendige Verzeichnisse
mkdir -p /opt/ems-core/config
mkdir -p /opt/ems-core/logs
mkdir -p /opt/ems-core/webui/templates
mkdir -p /opt/ems-core/core/controllers
mkdir -p /opt/ems-core/core/optimizer

# Setze Berechtigungen
chmod +x /opt/ems-core/core/main.py
chmod +x /opt/ems-core/webui/app.py
```

## ⚙️ Schritt 5: Systemd Services

### Automatisches Deployment:

```bash
cd /opt/ems-core
sudo ./deploy_services.sh
```

### Manuelle Installation:

#### Optimizer Service

```bash
sudo nano /etc/systemd/system/ems-optimizer.service
```

Füge ein:
```ini
[Unit]
Description=EMS-Core v2.0 Optimizer - Energy Management System
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=/opt/ems-core
Environment="PATH=/opt/ems-core/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=/opt/ems-core/venv/bin/python3 -m core.main

Restart=always
RestartSec=10

StandardOutput=journal
StandardError=journal
SyslogIdentifier=ems-optimizer

[Install]
WantedBy=multi-user.target
```

#### WebUI Service

```bash
sudo nano /etc/systemd/system/ems-webui.service
```

Füge ein:
```ini
[Unit]
Description=EMS-Core v2.0 Web UI - Flask Application
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=/opt/ems-core/webui
Environment="PATH=/opt/ems-core/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=/opt/ems-core/venv/bin/python3 app.py

Restart=always
RestartSec=10

StandardOutput=journal
StandardError=journal
SyslogIdentifier=ems-webui

[Install]
WantedBy=multi-user.target
```

#### Services aktivieren und starten

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable (Auto-Start)
sudo systemctl enable ems-optimizer
sudo systemctl enable ems-webui

# Start Services
sudo systemctl start ems-optimizer
sudo systemctl start ems-webui

# Status prüfen
sudo systemctl status ems-optimizer
sudo systemctl status ems-webui
```

## 🔧 Schritt 6: Basis-Konfiguration

### Energy Sources konfigurieren

1. Öffne Web UI: `http://YOUR-IP:8080/energy_sources`
2. Gehe zum Tab "🔌 Quellen"
3. Füge deine Energy Sources hinzu:

**Beispiel: PV via Home Assistant**
```
Typ: PV Erzeugung
Provider: Home Assistant
Name: Meine PV
URL: http://10.0.0.189:8123
Token: [Long-lived access token]
Entity ID: sensor.pv_power
```

**Beispiel: Grid via Shelly 3EM**
```
Typ: Netz-Messung
Provider: Shelly 3EM
Name: Netz Zähler
IP: 10.0.0.14
```

**Beispiel: Battery via Home Assistant**
```
Typ: Batterie
Provider: Home Assistant
Name: Batterie
URL: http://10.0.0.189:8123
Token: [Long-lived access token]
Entity ID (Power): sensor.battery_power
Entity ID (SOC): sensor.battery_soc
```

### Devices hinzufügen

1. Öffne: `http://YOUR-IP:8080/devices`
2. Klicke "➕ Gerät hinzufügen"
3. Konfiguriere deine Devices:

**Beispiel: Shelly Plug**
```
Name: Waschmaschine
Typ: shelly_plug
IP: 10.0.0.20
Kategorie: appliance
Priorität: MEDIUM
Power Rating: 2000 W
```

## ✅ Schritt 7: Verifizierung

### Test 1: Web UI erreichbar

```bash
curl http://localhost:8080/health
# Sollte zurückgeben: {"status":"healthy","service":"EMS-Core Web UI","version":"2.0"}
```

### Test 2: Energy API

```bash
curl http://localhost:8080/api/energy/current
# Sollte aktuelle Energie-Daten zurückgeben
```

### Test 3: Device Control (falls Devices konfiguriert)

```bash
# Device Status abrufen
curl http://localhost:8080/api/devices

# Device einschalten (ersetze DEVICE_ID)
curl -X POST http://localhost:8080/api/devices/DEVICE_ID/control \
  -H "Content-Type: application/json" \
  -d '{"action":"on"}'
```

### Test 4: Logs prüfen

```bash
# Optimizer läuft und aktualisiert?
sudo journalctl -u ems-optimizer -n 20

# WebUI läuft?
sudo journalctl -u ems-webui -n 20
```

## 🔐 Schritt 8: Sicherheit (Optional, aber empfohlen)

### Firewall konfigurieren

```bash
# UFW installieren (falls nicht vorhanden)
sudo apt install ufw

# Erlaube SSH
sudo ufw allow 22/tcp

# Erlaube Web UI (nur aus lokalem Netz)
sudo ufw allow from 10.0.0.0/24 to any port 8080

# Aktiviere Firewall
sudo ufw enable
```

### Reverse Proxy (Optional)

Für HTTPS und Domain-Zugriff kannst du nginx als Reverse Proxy nutzen:

```bash
sudo apt install nginx certbot python3-certbot-nginx

sudo nano /etc/nginx/sites-available/ems-core
```

```nginx
server {
    listen 80;
    server_name ems.example.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/ems-core /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Optional: SSL mit Let's Encrypt
sudo certbot --nginx -d ems.example.com
```

## 🔄 Schritt 9: Updates

### Update von GitHub

```bash
cd /opt/ems-core

# Stoppe Services
sudo systemctl stop ems-optimizer ems-webui

# Backup Config
cp -r config config.backup

# Pull Updates
git pull origin main

# Update Dependencies
source venv/bin/activate
pip install --upgrade -r requirements.txt

# Starte Services
sudo systemctl start ems-optimizer ems-webui
```

### Manuelles Update

```bash
# Backup erstellen
sudo tar -czf /opt/ems-core-backup-$(date +%Y%m%d).tar.gz /opt/ems-core

# Neue Dateien kopieren
# ...

# Services neu starten
sudo systemctl restart ems-optimizer ems-webui
```

## 🧹 Deinstallation

Falls du EMS-Core entfernen möchtest:

```bash
# Services stoppen und deaktivieren
sudo systemctl stop ems-optimizer ems-webui
sudo systemctl disable ems-optimizer ems-webui

# Service-Dateien entfernen
sudo rm /etc/systemd/system/ems-optimizer.service
sudo rm /etc/systemd/system/ems-webui.service
sudo systemctl daemon-reload

# Installations-Verzeichnis entfernen
sudo rm -rf /opt/ems-core

# Optional: Python Packages entfernen
pip uninstall Flask aiohttp pymodbus pyyaml
```

## 🆘 Support

Bei Problemen:
1. Prüfe die Logs: `sudo journalctl -u ems-optimizer -u ems-webui -n 100`
2. Siehe [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
3. Öffne ein Issue auf GitHub

## ✅ Installation abgeschlossen!

Dein EMS-Core läuft jetzt! 🎉

**Nächste Schritte:**
1. Öffne Web UI: `http://YOUR-IP:8080`
2. Konfiguriere Energy Sources
3. Füge Devices hinzu
4. Beobachte den Optimizer in Aktion# Installation Guide - EMS-Core v2.0

Vollständige Installationsanleitung für EMS-Core v2.0.

## 📋 Voraussetzungen

### System
- **OS:** Ubuntu 20.04+ oder Debian 11+
- **RAM:** Minimum 512 MB, empfohlen 1 GB+
- **Disk:** Minimum 1 GB freier Speicher
- **Python:** Version 3.8 oder höher
- **Netzwerk:** Zugriff auf Shelly Devices, Home Assistant (optional)

### Zugriffsrechte
- Root oder sudo Zugriff erforderlich für Systemd Services

## 🚀 Schritt 1: System Vorbereitung

```bash
# System aktualisieren
sudo apt update
sudo apt upgrade -y

# Python und Dependencies installieren
sudo apt install -y python3 python3-pip python3-venv git

# Optional: Build-Tools für pymodbus
sudo apt install -y build-essential python3-dev
```

## 📦 Schritt 2: Repository Klonen

```bash
# Erstelle Installations-Verzeichnis
sudo mkdir -p /opt/ems-core
cd /opt/ems-core

# Clone Repository
git clone https://github.com/svkux/ems-core2.0.git .

# Oder: Download als ZIP und entpacken
wget https://github.com/svkux/ems-core2.0/archive/refs/heads/main.zip
unzip main.zip
mv ems-core2.0-main/* .
```

## 🐍 Schritt 3: Python Virtual Environment

```bash
cd /opt/ems-core

# Virtual Environment erstellen
python3 -m venv venv

# Aktivieren
source venv/bin/activate

# Dependencies installieren
pip install --upgrade pip
pip install -r requirements.txt
```

### requirements.txt sollte enthalten:

```
Flask>=2.3.0
aiohttp>=3.9.0
pymodbus>=3.5.0
pyyaml>=6.0
```

Falls `requirements.txt` fehlt, erstelle sie:

```bash
cat > requirements.txt << EOF
Flask>=2.3.0
aiohttp>=3.9.0
pymodbus>=3.5.0
pyyaml>=6.0
EOF

pip install -r requirements.txt
```

## 📁 Schritt 4: Verzeichnis-Struktur

```bash
# Erstelle notwendige Verzeichnisse
mkdir -p /opt/ems-core/config
mkdir -p /opt/ems-core/logs
mkdir -p /opt/ems-core/webui/templates
mkdir -p /opt/ems-core/core/controllers
mkdir -p /opt/ems-core/core/optimizer

# Setze Berechtigungen
chmod +x /opt/ems-core/core/main.py
chmod +x /opt/ems-core/webui/app.py
```

## ⚙️ Schritt 5: Systemd Services

### Automatisches Deployment:

```bash
cd /opt/ems-core
sudo ./deploy_services.sh
```

### Manuelle Installation:

#### Optimizer Service

```bash
sudo nano /etc/systemd/system/ems-optimizer.service
```

Füge ein:
```ini
[Unit]
Description=EMS-Core v2.0 Optimizer - Energy Management System
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=/opt/ems-core
Environment="PATH=/opt/ems-core/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=/opt/ems-core/venv/bin/python3 -m core.main

Restart=always
RestartSec=10

StandardOutput=journal
StandardError=journal
SyslogIdentifier=ems-optimizer

[Install]
WantedBy=multi-user.target
```

#### WebUI Service

```bash
sudo nano /etc/systemd/system/ems-webui.service
```

Füge ein:
```ini
[Unit]
Description=EMS-Core v2.0 Web UI - Flask Application
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=/opt/ems-core/webui
Environment="PATH=/opt/ems-core/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=/opt/ems-core/venv/bin/python3 app.py

Restart=always
RestartSec=10

StandardOutput=journal
StandardError=journal
SyslogIdentifier=ems-webui

[Install]
WantedBy=multi-user.target
```

#### Services aktivieren und starten

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable (Auto-Start)
sudo systemctl enable ems-optimizer
sudo systemctl enable ems-webui

# Start Services
sudo systemctl start ems-optimizer
sudo systemctl start ems-webui

# Status prüfen
sudo systemctl status ems-optimizer
sudo systemctl status ems-webui
```

## 🔧 Schritt 6: Basis-Konfiguration

### Energy Sources konfigurieren

1. Öffne Web UI: `http://YOUR-IP:8080/energy_sources`
2. Gehe zum Tab "🔌 Quellen"
3. Füge deine Energy Sources hinzu:

**Beispiel: PV via Home Assistant**
```
Typ: PV Erzeugung
Provider: Home Assistant
Name: Meine PV
URL: http://10.0.0.189:8123
Token: [Long-lived access token]
Entity ID: sensor.pv_power
```

**Beispiel: Grid via Shelly 3EM**
```
Typ: Netz-Messung
Provider: Shelly 3EM
Name: Netz Zähler
IP: 10.0.0.14
```

**Beispiel: Battery via Home Assistant**
```
Typ: Batterie
Provider: Home Assistant
Name: Batterie
URL: http://10.0.0.189:8123
Token: [Long-lived access token]
Entity ID (Power): sensor.battery_power
Entity ID (SOC): sensor.battery_soc
```

### Devices hinzufügen

1. Öffne: `http://YOUR-IP:8080/devices`
2. Klicke "➕ Gerät hinzufügen"
3. Konfiguriere deine Devices:

**Beispiel: Shelly Plug**
```
Name: Waschmaschine
Typ: shelly_plug
IP: 10.0.0.20
Kategorie: appliance
Priorität: MEDIUM
Power Rating: 2000 W
```

## ✅ Schritt 7: Verifizierung

### Test 1: Web UI erreichbar

```bash
curl http://localhost:8080/health
# Sollte zurückgeben: {"status":"healthy","service":"EMS-Core Web UI","version":"2.0"}
```

### Test 2: Energy API

```bash
curl http://localhost:8080/api/energy/current
# Sollte aktuelle Energie-Daten zurückgeben
```

### Test 3: Device Control (falls Devices konfiguriert)

```bash
# Device Status abrufen
curl http://localhost:8080/api/devices

# Device einschalten (ersetze DEVICE_ID)
curl -X POST http://localhost:8080/api/devices/DEVICE_ID/control \
  -H "Content-Type: application/json" \
  -d '{"action":"on"}'
```

### Test 4: Logs prüfen

```bash
# Optimizer läuft und aktualisiert?
sudo journalctl -u ems-optimizer -n 20

# WebUI läuft?
sudo journalctl -u ems-webui -n 20
```

## 🔐 Schritt 8: Sicherheit (Optional, aber empfohlen)

### Firewall konfigurieren

```bash
# UFW installieren (falls nicht vorhanden)
sudo apt install ufw

# Erlaube SSH
sudo ufw allow 22/tcp

# Erlaube Web UI (nur aus lokalem Netz)
sudo ufw allow from 10.0.0.0/24 to any port 8080

# Aktiviere Firewall
sudo ufw enable
```

### Reverse Proxy (Optional)

Für HTTPS und Domain-Zugriff kannst du nginx als Reverse Proxy nutzen:

```bash
sudo apt install nginx certbot python3-certbot-nginx

sudo nano /etc/nginx/sites-available/ems-core
```

```nginx
server {
    listen 80;
    server_name ems.example.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/ems-core /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Optional: SSL mit Let's Encrypt
sudo certbot --nginx -d ems.example.com
```

## 🔄 Schritt 9: Updates

### Update von GitHub

```bash
cd /opt/ems-core

# Stoppe Services
sudo systemctl stop ems-optimizer ems-webui

# Backup Config
cp -r config config.backup

# Pull Updates
git pull origin main

# Update Dependencies
source venv/bin/activate
pip install --upgrade -r requirements.txt

# Starte Services
sudo systemctl start ems-optimizer ems-webui
```

### Manuelles Update

```bash
# Backup erstellen
sudo tar -czf /opt/ems-core-backup-$(date +%Y%m%d).tar.gz /opt/ems-core

# Neue Dateien kopieren
# ...

# Services neu starten
sudo systemctl restart ems-optimizer ems-webui
```

## 🧹 Deinstallation

Falls du EMS-Core entfernen möchtest:

```bash
# Services stoppen und deaktivieren
sudo systemctl stop ems-optimizer ems-webui
sudo systemctl disable ems-optimizer ems-webui

# Service-Dateien entfernen
sudo rm /etc/systemd/system/ems-optimizer.service
sudo rm /etc/systemd/system/ems-webui.service
sudo systemctl daemon-reload

# Installations-Verzeichnis entfernen
sudo rm -rf /opt/ems-core

# Optional: Python Packages entfernen
pip uninstall Flask aiohttp pymodbus pyyaml
```

## 🆘 Support

Bei Problemen:
1. Prüfe die Logs: `sudo journalctl -u ems-optimizer -u ems-webui -n 100`
2. Siehe [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
3. Öffne ein Issue auf GitHub

## ✅ Installation abgeschlossen!

Dein EMS-Core läuft jetzt! 🎉

**Nächste Schritte:**
1. Öffne Web UI: `http://YOUR-IP:8080`
2. Konfiguriere Energy Sources
3. Füge Devices hinzu
4. Beobachte den Optimizer in Aktion
