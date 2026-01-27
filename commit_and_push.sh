#!/bin/bash
#
# EMS-Core v2.0 - Git Commit & Push Script
# Sichert alle Änderungen zu GitHub
#

set -e

echo "================================================"
echo "EMS-Core v2.0 - Git Backup zu GitHub"
echo "================================================"
echo ""

cd /opt/ems-core

# Check if git repo
if [ ! -d ".git" ]; then
    echo "❌ Kein Git Repository! Initialisiere..."
    git init
    git remote add origin https://github.com/svkux/ems-core2.0.git
    echo "✅ Git Repository initialisiert"
fi

# Git Config (falls nicht gesetzt)
git config user.name "svkux" 2>/dev/null || true
git config user.email "your-email@example.com" 2>/dev/null || true

# Status zeigen
echo "📊 Git Status:"
git status --short
echo ""

# Dateien zum Commit hinzufügen
echo "➕ Füge Dateien hinzu..."

# Core Files
git add core/*.py
git add core/controllers/*.py
git add core/optimizer/*.py 2>/dev/null || true

# WebUI Files
git add webui/*.py
git add webui/templates/*.html

# Documentation
git add *.md

# Config (aber ohne sensible Daten!)
git add requirements.txt
git add deploy_services.sh
git add ems-optimizer.service
git add ems-webui.service

# .gitignore erstellen falls nicht vorhanden
if [ ! -f ".gitignore" ]; then
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Logs
logs/
*.log

# Config mit sensiblen Daten
config/*.json
config/*.yaml
!config/README.md

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Backup Files
*.backup
*.bak
EOF
    git add .gitignore
    echo "✅ .gitignore erstellt"
fi

echo "✅ Dateien hinzugefügt"
echo ""

# Commit Message
if [ -z "$1" ]; then
    COMMIT_MSG="Update EMS-Core v2.0 - $(date '+%Y-%m-%d %H:%M')"
else
    COMMIT_MSG="$1"
fi

echo "💾 Erstelle Commit: ${COMMIT_MSG}"
git commit -m "${COMMIT_MSG}" || {
    echo "ℹ️ Keine Änderungen zum Committen"
    exit 0
}

echo "✅ Commit erstellt"
echo ""

# Push zu GitHub
echo "🚀 Push zu GitHub..."
git push -u origin main || git push -u origin master || {
    echo "❌ Push fehlgeschlagen!"
    echo ""
    echo "Mögliche Gründe:"
    echo "1. Remote Repository existiert nicht"
    echo "2. Keine Berechtigung (SSH Key oder Token fehlt)"
    echo "3. Branch Name falsch (main vs master)"
    echo ""
    echo "Manuell pushen mit:"
    echo "  git push -u origin main"
    echo ""
    exit 1
}

echo "✅ Push erfolgreich!"
echo ""

# Aktuellen Stand zeigen
echo "📊 Repository Status:"
git log --oneline -5
echo ""

echo "================================================"
echo "✅ Backup zu GitHub abgeschlossen!"
echo "================================================"
echo ""
echo "Repository: https://github.com/svkux/ems-core2.0"
echo ""#!/bin/bash
#
# EMS-Core v2.0 - Git Commit & Push Script
# Sichert alle Änderungen zu GitHub
#

set -e

echo "================================================"
echo "EMS-Core v2.0 - Git Backup zu GitHub"
echo "================================================"
echo ""

cd /opt/ems-core

# Check if git repo
if [ ! -d ".git" ]; then
    echo "❌ Kein Git Repository! Initialisiere..."
    git init
    git remote add origin https://github.com/svkux/ems-core2.0.git
    echo "✅ Git Repository initialisiert"
fi

# Git Config (falls nicht gesetzt)
git config user.name "svkux" 2>/dev/null || true
git config user.email "your-email@example.com" 2>/dev/null || true

# Status zeigen
echo "📊 Git Status:"
git status --short
echo ""

# Dateien zum Commit hinzufügen
echo "➕ Füge Dateien hinzu..."

# Core Files
git add core/*.py
git add core/controllers/*.py
git add core/optimizer/*.py 2>/dev/null || true

# WebUI Files
git add webui/*.py
git add webui/templates/*.html

# Documentation
git add *.md

# Config (aber ohne sensible Daten!)
git add requirements.txt
git add deploy_services.sh
git add ems-optimizer.service
git add ems-webui.service

# .gitignore erstellen falls nicht vorhanden
if [ ! -f ".gitignore" ]; then
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Logs
logs/
*.log

# Config mit sensiblen Daten
config/*.json
config/*.yaml
!config/README.md

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Backup Files
*.backup
*.bak
EOF
    git add .gitignore
    echo "✅ .gitignore erstellt"
fi

echo "✅ Dateien hinzugefügt"
echo ""

# Commit Message
if [ -z "$1" ]; then
    COMMIT_MSG="Update EMS-Core v2.0 - $(date '+%Y-%m-%d %H:%M')"
else
    COMMIT_MSG="$1"
fi

echo "💾 Erstelle Commit: ${COMMIT_MSG}"
git commit -m "${COMMIT_MSG}" || {
    echo "ℹ️ Keine Änderungen zum Committen"
    exit 0
}

echo "✅ Commit erstellt"
echo ""

# Push zu GitHub
echo "🚀 Push zu GitHub..."
git push -u origin main || git push -u origin master || {
    echo "❌ Push fehlgeschlagen!"
    echo ""
    echo "Mögliche Gründe:"
    echo "1. Remote Repository existiert nicht"
    echo "2. Keine Berechtigung (SSH Key oder Token fehlt)"
    echo "3. Branch Name falsch (main vs master)"
    echo ""
    echo "Manuell pushen mit:"
    echo "  git push -u origin main"
    echo ""
    exit 1
}

echo "✅ Push erfolgreich!"
echo ""

# Aktuellen Stand zeigen
echo "📊 Repository Status:"
git log --oneline -5
echo ""

echo "================================================"
echo "✅ Backup zu GitHub abgeschlossen!"
echo "================================================"
echo ""
echo "Repository: https://github.com/svkux/ems-core2.0"
echo ""
