# GitHub Update - EMS-Core v2.0.1

## 📦 Zu kommittierende Dateien

### Neue Core-Dateien
```
core/device_override.py          # Manual Override Manager
core/optimizer/scheduler.py      # Scheduler Engine
core/optimizer/schedule_manager.py  # Schedule CRUD
```

### Aktualisierte Core-Dateien
```
core/main.py                     # Mit Override + Scheduler Integration
core/device_manager.py           # Improved validation & error handling
```

### Neue WebUI-Dateien
```
webui/api_override.py            # Override REST API
webui/templates/base.html        # Base Template mit Sidebar
```

### Aktualisierte WebUI-Dateien
```
webui/app.py                     # Mit Override API Integration
webui/templates/index.html       # Neues Design mit base.html
webui/templates/devices.html     # Mit Override Buttons
webui/templates/dashboard.html   # Update auf base.html (manuell)
webui/templates/energy_sources.html  # Update auf base.html (manuell)
```

### Neue Config-Dateien (Examples)
```
config.example/schedules.json    # Example Schedule Config
config.example/device_overrides.json  # Example Override Config
```

### Dokumentation
```
README.md                        # Komplett aktualisiert
CHANGELOG.md                     # Version 2.0.1 Eintrag
DEVELOPMENT.md                   # Neuer Development Guide

docs/BUGFIXES.md                 # Bug Fixes von 2.0.0 → 2.0.1
docs/SCHEDULER_README.md         # Scheduler Dokumentation
docs/OVERRIDE_README.md          # Manual Override Dokumentation
docs/WEBUI_README.md             # Web UI Redesign Guide
```

## 🚀 Git Workflow

### 1. Branch erstellen

```bash
cd /path/to/ems-core2.0
git checkout -b release/v2.0.1
```

### 2. Dateien hinzufügen

```bash
# Core Files
git add core/device_override.py
git add core/optimizer/scheduler.py
git add core/optimizer/schedule_manager.py
git add core/main.py
git add core/device_manager.py

# WebUI Files
git add webui/api_override.py
git add webui/app.py
git add webui/templates/base.html
git add webui/templates/index.html
git add webui/templates/devices.html

# Config Examples
mkdir -p config.example
git add config.example/schedules.json
git add config.example/device_overrides.json

# Documentation
git add README.md
git add CHANGELOG.md
git add DEVELOPMENT.md
git add docs/BUGFIXES.md
git add docs/SCHEDULER_README.md
git add docs/OVERRIDE_README.md
git add docs/WEBUI_README.md
```

### 3. Commit erstellen

```bash
git commit -m "release: Version 2.0.1

Major Features:
- Manual Override System with REST API
- Scheduler System (TIME_WINDOW, TIME_BLOCK, CONDITIONAL)
- Web UI Redesign with Sidebar Navigation
- Device List with Override Buttons

Bug Fixes:
- Fixed DeviceConfig inconsistencies in main.py
- Fixed async support in Flask app.py
- Improved error handling in device_manager.py

Documentation:
- Added comprehensive documentation for all new features
- Updated README.md with full feature list
- Added DEVELOPMENT.md for contributors

Breaking Changes:
- None (fully backward compatible)

See CHANGELOG.md for detailed changes."
```

### 4. Push & Create PR

```bash
# Push to GitHub
git push origin release/v2.0.1

# Erstelle Pull Request auf GitHub
# Titel: "Release v2.0.1 - Manual Override + Scheduler + UI Redesign"
```

### 5. Tag erstellen (nach Merge)

```bash
git checkout main
git pull origin main

# Tag erstellen
git tag -a v2.0.1 -m "Release v2.0.1

- Manual Override System
- Scheduler System
- Web UI Redesign
- Bug Fixes & Improvements

See CHANGELOG.md for full details."

# Tag pushen
git push origin v2.0.1
```

### 6. GitHub Release erstellen

Gehe zu: `https://github.com/svkux/ems-core2.0/releases/new`

**Tag:** `v2.0.1`  
**Title:** `EMS-Core v2.0.1 - Manual Override + Scheduler + UI Redesign`

**Description:**
```markdown
# EMS-Core v2.0.1

Major update with Manual Override, Scheduler System, and redesigned Web UI!

## 🎉 Highlights

### ✨ Manual Override System
- **One-Click Control**: EIN/AUS/AUTO Buttons for every device
- **Priority Override**: Manual control overrides PV-Optimization and Schedules
- **Time-Based**: Optional auto-expire after X minutes
- **REST API**: Full API support for automation
- **Persistent**: Survives system restarts

### 🕐 Scheduler System
Three schedule types for flexible automation:
- **TIME_WINDOW**: "Device only 10-14h"
- **TIME_BLOCK**: "Block device at night"
- **CONDITIONAL**: "Only when PV > 2000W AND 11-16h"

Features:
- Weekday support
- Priority override
- JSON-based persistence
- Full REST API

### 🎨 Web UI Redesign
- **Unified Navigation**: Sidebar on all pages
- **Breadcrumbs**: Better orientation
- **Device List**: With Manual Override buttons
- **Override Status**: Live status display with 👤 icon
- **Filter & Search**: Find devices quickly
- **Responsive**: Mobile-optimized
- **Toast Notifications**: User feedback

## 🐛 Bug Fixes
- Fixed DeviceConfig inconsistencies
- Fixed async support in Flask
- Improved error handling & validation

## 📚 Documentation
Comprehensive documentation for all features:
- SCHEDULER_README.md - Complete scheduler guide
- OVERRIDE_README.md - Manual override documentation
- WEBUI_README.md - UI redesign guide
- DEVELOPMENT.md - Developer guide
- Updated README.md & CHANGELOG.md

## 🔄 Migration
**Fully backward compatible!** No breaking changes.

See [CHANGELOG.md](CHANGELOG.md) for migration guide.

## 📦 Installation

### New Installation
```bash
git clone https://github.com/svkux/ems-core2.0.git
cd ems-core2.0
# Follow INSTALLATION.md
```

### Update from v2.0.0
```bash
cd /opt/ems-core
sudo systemctl stop ems-optimizer ems-webui
git pull origin main
# Follow migration guide in CHANGELOG.md
sudo systemctl start ems-optimizer ems-webui
```

## 📸 Screenshots

[Add screenshots here]

## 🙏 Credits
Thanks to everyone who provided feedback and suggestions!

---

**Full Changelog**: [v2.0.0...v2.0.1](https://github.com/svkux/ems-core2.0/compare/v2.0.0...v2.0.1)
```

## 📋 File Structure für GitHub

```
ems-core2.0/
├── .github/
│   ├── workflows/               # CI/CD (Optional)
│   │   └── tests.yml
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── PULL_REQUEST_TEMPLATE.md
│
├── core/
│   ├── __init__.py
│   ├── main.py
│   ├── device_manager.py
│   ├── device_override.py       # NEU
│   ├── energy_sources.py
│   ├── controllers/
│   │   ├── __init__.py
│   │   ├── shelly.py
│   │   └── sg_ready.py
│   └── optimizer/               # NEU
│       ├── __init__.py
│       ├── scheduler.py         # NEU
│       └── schedule_manager.py  # NEU
│
├── webui/
│   ├── __init__.py
│   ├── app.py
│   ├── api_routes.py
│   ├── api_energy.py
│   ├── api_override.py          # NEU
│   ├── templates/
│   │   ├── base.html            # NEU
│   │   ├── index.html           # UPDATED
│   │   ├── dashboard.html
│   │   ├── devices.html         # UPDATED
│   │   └── energy_sources.html
│   └── static/                  # TODO
│       ├── css/
│       ├── js/
│       └── img/
│
├── config.example/              # NEU
│   ├── devices.yaml
│   ├── energy_sources.json
│   ├── schedules.json           # NEU
│   └── device_overrides.json   # NEU
│
├── docs/
│   ├── INSTALLATION.md
│   ├── API_DOCUMENTATION.md
│   ├── TROUBLESHOOTING.md
│   ├── BUGFIXES.md              # NEU
│   ├── SCHEDULER_README.md      # NEU
│   ├── OVERRIDE_README.md       # NEU
│   └── WEBUI_README.md          # NEU
│
├── deploy/
│   ├── ems-optimizer.service
│   ├── ems-webui.service
│   └── deploy_services.sh
│
├── tests/                       # TODO
│   ├── __init__.py
│   ├── test_device_manager.py
│   ├── test_scheduler.py
│   └── test_override.py
│
├── .gitignore
├── requirements.txt
├── README.md                    # UPDATED
├── CHANGELOG.md                 # UPDATED
├── DEVELOPMENT.md               # NEU
├── LICENSE
└── setup.py                     # TODO
```

## 📝 .gitignore

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Config (sensitive)
config/devices.yaml
config/energy_sources.json
config/schedules.json
config/device_overrides.json
*.secret
*.key

# Logs
logs/
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Testing
.pytest_cache/
.coverage
htmlcov/

# Build
build/
dist/
*.egg-info/
```

## 📌 GitHub Labels

Erstelle folgende Labels für Issues:

- `bug` - Something isn't working
- `enhancement` - New feature or request
- `documentation` - Improvements or additions to documentation
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention is needed
- `priority: high` - High priority
- `priority: medium` - Medium priority
- `priority: low` - Low priority
- `status: in progress` - Currently being worked on
- `status: blocked` - Blocked by dependencies
- `type: feature` - New feature
- `type: bugfix` - Bug fix
- `type: refactor` - Code refactoring

## 🎯 Next Steps nach GitHub Update

1. **Update Wiki** (optional)
   - Installation Guide
   - Configuration Examples
   - FAQ

2. **Create Discussion Topics**
   - Feature Requests
   - General Questions
   - Show and Tell

3. **Update Project Board** (optional)
   - Roadmap Items
   - Current Tasks
   - Done Items

4. **Social Media** (optional)
   - Tweet Release
   - Reddit Post
   - Forum Announcement

## 📞 Support Kanäle

Nach Release einrichten:
- GitHub Issues für Bugs
- GitHub Discussions für Fragen
- Discord/Matrix für Community (optional)

---

**Checklist vor Release:**
- [ ] Alle Tests bestanden
- [ ] Dokumentation vollständig
- [ ] CHANGELOG.md aktualisiert
- [ ] Version in Code aktualisiert
- [ ] Screenshots erstellt
- [ ] Example Configs bereitgestellt
- [ ] Migration Guide getestet
- [ ] Release Notes geschrieben
