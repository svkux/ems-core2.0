#!/bin/bash
################################################################################
# EMS-Core v2.0 - Komplettes System Setup
# Führt alle Schritte für eine vollständige Installation aus
################################################################################

set -e

# Farben
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

echo ""
echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║                    EMS-Core v2.0 - System Setup                        ║"
echo "║                   Komplette Installation & Konfiguration               ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
echo ""

# Prüfe Root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${YELLOW}[WARNING]${NC} Script nicht als root ausgeführt."
    echo "Einige Schritte benötigen sudo-Rechte."
    echo ""
fi

# Prüfe Verzeichnis
if [ ! -f "PROJECT.md" ]; then
    echo -e "${RED}[ERROR]${NC} Bitte im ems-core2.0 Hauptverzeichnis ausführen!"
    exit 1
fi

EMS_DIR=$(pwd)
echo -e "${BLUE}[INFO]${NC} EMS Directory: $EMS_DIR"
echo ""

################################################################################
# STEP 1: Backup
################################################################################
echo -e "${PURPLE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${PURPLE}STEP 1/7: Backup erstellen${NC}"
echo -e "${PURPLE}═══════════════════════════════════════════════════════════${NC}"

BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

for file in config core webui; do
    if [ -e "$file" ]; then
        cp -r "$file" "$BACKUP_DIR/" 2>/dev/null || true
    fi
done

echo -e "${GREEN}✓${NC} Backup erstellt in: $BACKUP_DIR"
echo ""

################################################################################
# STEP 2: Dependencies
################################################################################
echo -e "${PURPLE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${PURPLE}STEP 2/7: Dependencies prüfen${NC}"
echo -e "${PURPLE}═══════════════════════════════════════════════════════════${NC}"

# Python Version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${BLUE}[INFO]${NC} Python Version: $PYTHON_VERSION"

# Virtual Environment
if [ ! -d "venv" ]; then
    echo -e "${BLUE}[INFO]${NC} Erstelle Virtual Environment..."
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Virtual Environment erstellt"
else
    echo -e "${GREEN}✓${NC} Virtual Environment existiert bereits"
fi

# Activate venv
source venv/bin/activate

# Install packages
echo -e "${BLUE}[INFO]${NC} Installiere Python-Pakete..."
pip install -q --upgrade pip
pip install -q flask pyyaml aiohttp pymodbus requests

echo -e "${GREEN}✓${NC} Dependencies installiert"
echo ""

################################################################################
# STEP 3: Ordnerstruktur
################################################################################
echo -e "${PURPLE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${PURPLE}STEP 3/7: Ordnerstruktur erstellen${NC}"
echo -e "${PURPLE}═══════════════════════════════════════════════════════════${NC}"

mkdir -p core/optimizer
mkdir -p core/controllers
mkdir -p core/integrations
mkdir -p webui/templates
mkdir -p webui/static
mkdir -p config
mkdir -p logs
mkdir -p tests

echo -e "${GREEN}✓${NC} Ordnerstruktur erstellt"
echo ""

################################################################################
# STEP 4: Deploy Files
################################################################################
echo -e "${PURPLE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${PURPLE}STEP 4/7: Dateien deployen${NC}"
echo -e "${PURPLE}═══════════════════════════════════════════════════════════${NC}"

if [ -f "deploy_ems_updates.sh" ]; then
    echo -e "${BLUE}[INFO]${NC} Führe Deployment-Script aus..."
    chmod +x deploy_ems_updates.sh
    ./deploy_ems_updates.sh
    echo -e "${GREEN}✓${NC} Deployment abgeschlossen"
else
    echo -e "${YELLOW}[WARNING]${NC} deploy_ems_updates.sh nicht gefunden"
    echo "Bitte manuell deployen oder Artifact-Files einfügen"
fi

echo ""

################################################################################
# STEP 5: Konfiguration
################################################################################
echo -e "${PURPLE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${PURPLE}STEP 5/7: Konfiguration${NC}"
echo -e "${PURPLE}═══════════════════════════════════════════════════════════${NC}"

# Prüfe Konfig-Dateien
CONFIG_FILES=("settings.yaml" "devices.yaml" "schedules.json" "priorities.json")
MISSING_CONFIG=0

for file in "${CONFIG_FILES[@]}"; do
    if [ -f "config/$file" ]; then
        echo -e "${GREEN}✓${NC} config/$file vorhanden"
    else
        echo -e "${YELLOW}⚠${NC} config/$file fehlt"
        MISSING_CONFIG=1
    fi
done

if [ $MISSING_CONFIG -eq 1 ]; then
    echo ""
    echo -e "${YELLOW}[WARNING]${NC} Einige Konfig-Dateien fehlen."
    echo "Diese werden beim ersten Start automatisch erstellt."
fi

# IP-Adresse Konfiguration
echo ""
echo -e "${BLUE}[INFO]${NC} IP-Adresse für Web UI konfigurieren..."
read -p "Web UI IP-Adresse (default: 0.0.0.0): " WEBUI_IP
WEBUI_IP=${WEBUI_IP:-0.0.0.0}

read -p "Web UI Port (default: 8080): " WEBUI_PORT
WEBUI_PORT=${WEBUI_PORT:-8080}

echo -e "${GREEN}✓${NC} Web UI wird erreichbar sein unter: http://$WEBUI_IP:$WEBUI_PORT"
echo ""

################################################################################
# STEP 6: Tests
################################################################################
echo -e "${PURPLE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${PURPLE}STEP 6/7: System-Tests${NC}"
echo -e "${PURPLE}═══════════════════════════════════════════════════════════${NC}"

if [ -f "test_ems_system.py" ]; then
    echo -e "${BLUE}[INFO]${NC} Führe System-Tests aus..."
    python3 test_ems_system.py
    echo -e "${GREEN}✓${NC} Tests abgeschlossen"
else
    echo -e "${YELLOW}[WARNING]${NC} test_ems_system.py nicht gefunden"
fi

echo ""

################################################################################
# STEP 7: Service Setup
################################################################################
echo -e "${PURPLE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${PURPLE}STEP 7/7: Systemd Service${NC}"
echo -e "${PURPLE}═══════════════════════════════════════════════════════════${NC}"

if [ -f "ems-core.service" ]; then
    read -p "Systemd Service installieren? (y/n) " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [ "$EUID" -ne 0 ]; then
            echo -e "${YELLOW}[INFO]${NC} Benötigt sudo..."
            sudo cp ems-core.service /etc/systemd/system/
            sudo systemctl daemon-reload
            sudo systemctl enable ems-core
            echo -e "${GREEN}✓${NC} Service installiert und aktiviert"
        else
            cp ems-core.service /etc/systemd/system/
            systemctl daemon-reload
            systemctl enable ems-core
            echo -e "${GREEN}✓${NC} Service installiert und aktiviert"
        fi
        
        read -p "Service jetzt starten? (y/n) " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            if [ "$EUID" -ne 0 ]; then
                sudo systemctl start ems-core
            else
                systemctl start ems-core
            fi
            echo -e "${GREEN}✓${NC} Service gestartet"
        fi
    else
        echo "Service-Installation übersprungen"
    fi
else
    echo -e "${YELLOW}[WARNING]${NC} ems-core.service nicht gefunden"
fi

echo ""

################################################################################
# SUMMARY
################################################################################
echo ""
echo "╔════════════════════════════════════════════════════════════════════════╗"
echo "║                         SETUP ABGESCHLOSSEN!                           ║"
echo "╚════════════════════════════════════════════════════════════════════════╝"
echo ""

echo -e "${GREEN}✓ Installation erfolgreich!${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "                           NÄCHSTE SCHRITTE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "1️⃣  Konfiguration anpassen:"
echo "   nano config/settings.yaml"
echo "   nano config/devices.yaml"
echo ""

echo "2️⃣  Web UI starten (Development):"
echo "   source venv/bin/activate"
echo "   python3 webui/app.py"
echo ""

echo "3️⃣  Web UI öffnen:"
echo "   http://$WEBUI_IP:$WEBUI_PORT/devices"
echo ""

echo "4️⃣  Main Optimizer starten:"
echo "   python3 core/main.py"
echo ""

echo "5️⃣  Service Status prüfen:"
echo "   sudo systemctl status ems-core"
echo "   sudo journalctl -u ems-core -f"
echo ""

echo "6️⃣  GitHub Sync:"
echo "   ./update_github.sh"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "                              DOKUMENTATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "📖 README.md           - Projekt-Übersicht"
echo "📖 DEVELOPMENT.md      - Entwickler-Dokumentation"
echo "📖 CHANGELOG.md        - Versionshistorie"
echo "📖 DEPLOYMENT_SUMMARY  - Was wurde implementiert"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "                              WICHTIGE BEFEHLE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cat << 'EOF'
# System starten
sudo systemctl start ems-core

# System stoppen
sudo systemctl stop ems-core

# Logs anschauen
sudo journalctl -u ems-core -f

# Tests ausführen
python3 test_ems_system.py

# GitHub Update
./update_github.sh

# Web UI Development
python3 webui/app.py
EOF

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo -e "${BLUE}[INFO]${NC} Backup wurde erstellt in: $BACKUP_DIR"
echo -e "${BLUE}[INFO]${NC} Bei Problemen: siehe DEPLOYMENT_SUMMARY.md"
echo ""

echo -e "${GREEN}Viel Erfolg mit EMS-Core v2.0! 🚀${NC}"
echo ""
