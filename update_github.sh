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
echo -e "${BLUE}[INFO]${NC} Neue/geänderte Dateien werden hinzugefügt..."
echo ""

read -p "Alle Änderungen zu Git hinzufügen? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Abgebrochen."
    exit 0
fi

# Git Add - AKTUALISIERT mit allen neuen Dateien
echo -e "${BLUE}[INFO]${NC} Füge Dateien hinzu..."

# Core Module
git add core/device_manager.py
git add core/main.py
git add core/energy_sources.py
git add core/optimizer/

# Controllers
git add core/controllers/

# Integrations
git add core/integrations/

# Web UI
git add webui/app.py
git add webui/api_routes.py
git add webui/api_energy.py
git add webui/templates/

# Config
git add config/*.yaml
git add config/*.json

# Scripts
git add deploy_ems_updates.sh
git add test_ems_system.py
git add update_github.sh
git add setup_complete_system.sh

# Services
git add ems-core.service

# Dokumentation
git add README.md
git add .gitignore
git add DEPLOYMENT_SUMMARY.md
git add QUICK_REFERENCE.md

# Optional Docs
[ -f "DEVELOPMENT.md" ] && git add DEVELOPMENT.md
[ -f "CHANGELOG.md" ] && git add CHANGELOG.md

echo -e "${GREEN}[SUCCESS]${NC} Dateien hinzugefügt"

# Commit Message
echo ""
echo "Commit Message eingeben (oder Enter für Standard-Message):"
read -r COMMIT_MSG

if [ -z "$COMMIT_MSG" ]; then
    COMMIT_MSG="feat: Add Energy Sources Management System

## New Features
- Energy Sources Manager with multi-provider support
- Support for Home Assistant, Shelly, Solax Modbus, SDM630
- Web UI for Energy Sources configuration
- REST API for energy data management
- Real-time energy monitoring
- Automatic house consumption calculation

## Improvements
- Updated Device Management UI
- Enhanced API error handling
- Fixed JSON serialization for Enums
- Updated documentation (DEPLOYMENT_SUMMARY, QUICK_REFERENCE)

## Technical
- core/energy_sources.py - Energy data aggregation
- webui/api_energy.py - Energy Sources API
- webui/templates/energy_sources.html - Energy UI
- Async data updates from multiple sources"
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
