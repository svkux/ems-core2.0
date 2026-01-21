#!/bin/bash
################################################################################
# EMS-Core v2.0 - GitHub Update Script
# Synchronisiert alle Änderungen mit GitHub
################################################################################

set -e

# Farben
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "============================================================================"
echo "  EMS-Core v2.0 - GitHub Update"
echo "============================================================================"
echo ""

# Prüfe Git
if ! command -v git &> /dev/null; then
    echo -e "${YELLOW}Git nicht installiert!${NC}"
    exit 1
fi

# Prüfe ob Git Repo
if [ ! -d ".git" ]; then
    echo -e "${YELLOW}Kein Git Repository!${NC}"
    echo "Initialisiere Git Repository..."
    git init
    git remote add origin https://github.com/svkux/ems-core2.0.git
fi

# Status anzeigen
echo -e "${BLUE}[INFO]${NC} Git Status:"
git status --short

echo ""
echo -e "${BLUE}[INFO]${NC} Neue/geänderte Dateien:"
echo ""

# Liste neue Dateien
cat << 'EOF'
✅ Neue Kern-Module:
   - core/device_manager.py
   - core/main.py
   - core/optimizer/__init__.py
   - core/optimizer/scheduler.py
   - core/optimizer/prioritizer.py

✅ Web UI Erweiterungen:
   - webui/app.py (aktualisiert)
   - webui/api_routes.py (neu)
   - webui/templates/devices.html (neu)

✅ Konfiguration:
   - config/settings.yaml
   - config/devices.yaml
   - config/schedules.json
   - config/priorities.json
   - config/device_mapping.json (wird automatisch erstellt)

✅ Scripts:
   - deploy_ems_updates.sh
   - test_ems_system.py
   - update_github.sh

✅ Service:
   - ems-core.service

✅ Dokumentation:
   - README.md
   - DEVELOPMENT.md (neu)
   - CHANGELOG.md (neu)
EOF

echo ""
read -p "Alle Änderungen zu Git hinzufügen? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Abgebrochen."
    exit 0
fi

# Git Add
echo -e "${BLUE}[INFO]${NC} Füge Dateien hinzu..."

git add core/device_manager.py
git add core/main.py
git add core/optimizer/
git add webui/app.py
git add webui/api_routes.py
git add webui/templates/devices.html
git add config/*.yaml
git add config/*.json
git add deploy_ems_updates.sh
git add test_ems_system.py
git add update_github.sh
git add ems-core.service
git add README.md
git add .gitignore

# Optional: Füge neue Docs hinzu wenn vorhanden
[ -f "DEVELOPMENT.md" ] && git add DEVELOPMENT.md
[ -f "CHANGELOG.md" ] && git add CHANGELOG.md

echo -e "${GREEN}[SUCCESS]${NC} Dateien hinzugefügt"

# Commit Message
echo ""
echo "Commit Message eingeben (oder Enter für Standard-Message):"
read -r COMMIT_MSG

if [ -z "$COMMIT_MSG" ]; then
    COMMIT_MSG="feat: Add Device Manager and Web UI for device management

- Implemented DeviceManager for centralized device configuration
- Added REST API endpoints for device CRUD operations
- Created Device Management Web UI with add/edit/delete functionality
- Added device discovery import workflow
- Updated core/main.py with device integration
- Implemented scheduler and prioritizer modules
- Added comprehensive testing suite
- Updated documentation"
fi

# Git Commit
echo -e "${BLUE}[INFO]${NC} Erstelle Commit..."
git commit -m "$COMMIT_MSG"

echo -e "${GREEN}[SUCCESS]${NC} Commit erstellt"

# Push
echo ""
read -p "Zu GitHub pushen? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}[INFO]${NC} Pushing to GitHub..."
    
    # Prüfe Branch
    BRANCH=$(git branch --show-current)
    
    git push -u origin $BRANCH
    
    echo -e "${GREEN}[SUCCESS]${NC} Push erfolgreich!"
else
    echo "Push übersprungen. Manuell ausführen mit:"
    echo "  git push -u origin main"
fi

echo ""
echo "============================================================================"
echo -e "${GREEN}GitHub Update abgeschlossen!${NC}"
echo "============================================================================"
echo ""
echo "Repository: https://github.com/svkux/ems-core2.0"
echo ""
