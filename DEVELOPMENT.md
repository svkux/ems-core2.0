# Development Guide

Willkommen bei der EMS-Core v2.0 Entwicklung! Diese Anleitung hilft dir beim Setup und der Entwicklung neuer Features.

## 📋 Table of Contents

- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Creating New Features](#creating-new-features)
- [API Development](#api-development)
- [UI Development](#ui-development)
- [Debugging](#debugging)
- [Contributing](#contributing)

## 🚀 Development Setup

### Prerequisites

- Python 3.8+
- Git
- Virtual Environment Support
- Text Editor (VSCode empfohlen)

### Initial Setup

```bash
# 1. Clone Repository
git clone https://github.com/svkux/ems-core2.0.git
cd ems-core2.0

# 2. Create Virtual Environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# oder
venv\Scripts\activate  # Windows

# 3. Install Dependencies
pip install -r requirements.txt

# 4. Install Development Dependencies
pip install -r requirements-dev.txt  # Falls vorhanden
# Oder manuell:
pip install pytest pytest-asyncio black flake8 mypy
```

### Configuration

```bash
# Erstelle Config-Verzeichnis
mkdir -p config

# Kopiere Example Configs
cp config.example/devices.yaml config/devices.yaml
cp config.example/energy_sources.json config/energy_sources.json
cp config.example/schedules.json config/schedules.json

# Editiere Configs
nano config/devices.yaml
```

### Running in Development Mode

```bash
# Terminal 1: Optimizer
cd /path/to/ems-core2.0
source venv/bin/activate
python3 core/main.py

# Terminal 2: WebUI
cd /path/to/ems-core2.0
source venv/bin/activate
python3 webui/app.py
```

## 📁 Project Structure

```
ems-core2.0/
├── core/                       # Backend Core
│   ├── main.py                 # Optimizer Loop (Entry Point)
│   ├── device_manager.py       # Device CRUD
│   ├── device_override.py      # Manual Override
│   ├── energy_sources.py       # Energy Data Management
│   ├── controllers/            # Device Controllers
│   │   ├── shelly.py
│   │   └── sg_ready.py
│   └── optimizer/              # Optimizer Logic
│       ├── scheduler.py
│       └── schedule_manager.py
│
├── webui/                      # Frontend Web UI
│   ├── app.py                  # Flask App (Entry Point)
│   ├── api_routes.py           # Device API
│   ├── api_energy.py           # Energy API
│   ├── api_override.py         # Override API
│   ├── templates/              # Jinja2 Templates
│   │   ├── base.html           # Base Template
│   │   ├── index.html
│   │   ├── dashboard.html
│   │   ├── devices.html
│   │   └── energy_sources.html
│   └── static/                 # Static Files (TODO)
│       ├── css/
│       ├── js/
│       └── img/
│
├── config/                     # Configuration Files
│   ├── devices.yaml
│   ├── energy_sources.json
│   ├── schedules.json
│   └── device_overrides.json
│
├── docs/                       # Documentation
│   ├── INSTALLATION.md
│   ├── SCHEDULER_README.md
│   ├── OVERRIDE_README.md
│   └── ...
│
├── tests/                      # Unit Tests
│   ├── test_device_manager.py
│   ├── test_scheduler.py
│   └── ...
│
├── deploy/                     # Deployment Scripts
│   ├── ems-optimizer.service
│   ├── ems-webui.service
│   └── deploy_services.sh
│
├── requirements.txt            # Python Dependencies
├── README.md
├── CHANGELOG.md
└── LICENSE
```

## 🎨 Coding Standards

### Python Style Guide

Wir folgen **PEP 8** mit einigen Anpassungen:

```python
# Imports sortiert
import asyncio
import logging
from typing import List, Dict, Optional
from datetime import datetime

# Local imports
from core.device_manager import DeviceManager

# Constants in UPPER_CASE
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 5

# Klassen in PascalCase
class DeviceManager:
    pass

# Funktionen in snake_case
def get_device_status():
    pass

# Private mit underscore
def _internal_helper():
    pass
```

### Docstrings

```python
def calculate_available_power(self, energy_data: Dict) -> float:
    """
    Berechne verfügbare Power für optionale Devices
    
    Args:
        energy_data: Dict mit pv_power, grid_power, battery_soc
        
    Returns:
        Verfügbare Leistung in Watt
        
    Example:
        >>> available = optimizer.calculate_available_power({
        ...     'pv_power': 3000,
        ...     'grid_power': -1200,
        ...     'battery_soc': 85
        ... })
        >>> print(available)
        1100.0
    """
    # Implementation
```

### Type Hints

```python
from typing import Dict, List, Optional

def get_device(self, device_id: str) -> Optional[DeviceConfig]:
    """Hole Device nach ID"""
    return self.devices.get(device_id)

async def update_energy_data(self) -> Dict[str, float]:
    """Update Energy Data"""
    # Implementation
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

# Info für normale Operationen
logger.info("✅ Device added: {device.name}")

# Debug für Details
logger.debug(f"Raw data: {data}")

# Warning für Probleme
logger.warning("⚠️ Device not reachable: {device.ip}")

# Error für Fehler
logger.error(f"❌ Failed to update: {e}", exc_info=True)
```

### Error Handling

```python
# Immer spezifische Exceptions
try:
    value = int(data['value'])
except KeyError:
    logger.error("Missing 'value' in data")
    return None
except ValueError:
    logger.error("Invalid value format")
    return None
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    return None
```

## 🧪 Testing

### Unit Tests

```bash
# Alle Tests ausführen
pytest

# Mit Coverage
pytest --cov=core --cov=webui

# Spezifischer Test
pytest tests/test_device_manager.py

# Mit Output
pytest -v -s
```

### Test Example

```python
# tests/test_device_manager.py
import pytest
from core.device_manager import DeviceManager, DeviceConfig

def test_add_device():
    """Test device addition"""
    manager = DeviceManager()
    
    device = DeviceConfig(
        id="test_1",
        name="Test Device",
        type="shelly_plug",
        ip="192.168.1.100",
        power=2000
    )
    
    assert manager.add_device(device) == True
    assert len(manager.devices) == 1
    assert manager.get_device("test_1") == device

@pytest.mark.asyncio
async def test_optimizer_cycle():
    """Test optimizer cycle"""
    # Implementation
```

### Manual Testing

```bash
# Test Device Manager
python3 core/device_manager.py

# Test Scheduler
python3 core/optimizer/scheduler.py

# Test Override Manager
python3 core/device_override.py

# Test API
curl http://localhost:8080/api/devices
curl http://localhost:8080/api/override/status
```

## 🎯 Creating New Features

### 1. Plan Feature

1. Create GitHub Issue
2. Discuss approach
3. Create feature branch

```bash
git checkout -b feature/my-new-feature
```

### 2. Implement Backend

```python
# core/my_feature.py

import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class MyFeatureManager:
    """Manager für My Feature"""
    
    def __init__(self):
        logger.info("MyFeature initialized")
    
    def do_something(self) -> Dict:
        """Do something useful"""
        try:
            # Implementation
            return {'success': True}
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}
```

### 3. Add API Endpoint

```python
# webui/api_myfeature.py

from flask import Blueprint, jsonify, request

api_myfeature = Blueprint('api_myfeature', __name__, url_prefix='/api/myfeature')

@api_myfeature.route('/action', methods=['POST'])
def do_action():
    """Perform action"""
    try:
        data = request.get_json()
        # Process
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
```

### 4. Register in app.py

```python
# webui/app.py

from webui.api_myfeature import api_myfeature

app.register_blueprint(api_myfeature)
```

### 5. Add UI

```html
<!-- webui/templates/myfeature.html -->
{% extends "base.html" %}

{% block title %}My Feature - EMS-Core{% endblock %}

{% block content %}
<div class="page-header">
    <h1>My Feature</h1>
</div>

<div class="card">
    <button class="btn btn-primary" onclick="performAction()">
        Do Something
    </button>
</div>
{% endblock %}

{% block extra_js %}
<script>
async function performAction() {
    const response = await fetch('/api/myfeature/action', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({...})
    });
    
    const data = await response.json();
    if (data.success) {
        showNotification('Success!', 'success');
    }
}
</script>
{% endblock %}
```

### 6. Add Tests

```python
# tests/test_myfeature.py

def test_my_feature():
    """Test my feature"""
    # Implementation
```

### 7. Document

```markdown
# docs/MYFEATURE_README.md

# My Feature

## Overview
...

## Usage
...

## API
...
```

### 8. Commit & Push

```bash
git add .
git commit -m "feat: Add MyFeature

- Implemented backend logic
- Added API endpoints
- Created UI
- Added tests
- Updated documentation"

git push origin feature/my-new-feature
```

### 9. Create Pull Request

## 🌐 API Development

### REST API Best Practices

```python
# Erfolgreiche Response
return jsonify({
    'success': True,
    'data': {...},
    'message': 'Optional success message'
})

# Fehler Response
return jsonify({
    'success': False,
    'error': 'Error message',
    'code': 'ERROR_CODE'
}), 400  # Passender HTTP Status Code
```

### HTTP Status Codes

- `200 OK` - Erfolgreiche GET/PUT/DELETE
- `201 Created` - Erfolgreiche POST (Ressource erstellt)
- `400 Bad Request` - Ungültige Anfrage
- `404 Not Found` - Ressource nicht gefunden
- `500 Internal Server Error` - Server-Fehler

### API Versioning

```python
# Für Breaking Changes, neue Version erstellen
api_v2 = Blueprint('api_v2', __name__, url_prefix='/api/v2')
```

## 🎨 UI Development

### Template Struktur

```html
{% extends "base.html" %}

{% block title %}Seiten-Titel{% endblock %}

{% block breadcrumbs %}
<div class="breadcrumbs">
    <a href="/">Home</a>
    <span class="separator">›</span>
    <span>Aktuelle Seite</span>
</div>
{% endblock %}

{% block extra_css %}
<style>
    /* Seiten-spezifisches CSS */
</style>
{% endblock %}

{% block content %}
<!-- Hauptinhalt -->
{% endblock %}

{% block extra_js %}
<script>
    // Seiten-spezifisches JavaScript
</script>
{% endblock %}
```

### CSS Utilities (aus base.html)

```css
/* Buttons */
.btn, .btn-primary, .btn-success, .btn-danger, .btn-secondary
.btn-sm

/* Badges */
.badge, .badge-success, .badge-warning, .badge-danger, .badge-info

/* Cards */
.card, .card-header

/* Colors */
var(--primary), var(--success), var(--danger), var(--warning)
```

### JavaScript Helpers

```javascript
// Notification anzeigen
showNotification('Erfolgreich gespeichert', 'success');
showNotification('Fehler aufgetreten', 'error');

// Loading State
element.classList.add('loading');
// ... API Call
element.classList.remove('loading');
```

## 🐛 Debugging

### Python Debugging

```python
# Breakpoint setzen
import pdb; pdb.set_trace()

# Logging Debug Level
logging.basicConfig(level=logging.DEBUG)
```

### Flask Debugging

```python
# In app.py
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=True  # Enable Debug Mode
    )
```

### Browser DevTools

```
F12 → Console
F12 → Network (API Calls prüfen)
F12 → Elements (HTML/CSS prüfen)
```

### Systemd Service Debugging

```bash
# Service Status
sudo systemctl status ems-optimizer

# Logs live
sudo journalctl -u ems-optimizer -f

# Logs mit Zeitstempel
sudo journalctl -u ems-optimizer --since "10 minutes ago"

# Alle Fehler
sudo journalctl -u ems-optimizer -p err
```

## 🤝 Contributing

### Workflow

1. Fork Repository
2. Create Feature Branch
3. Make Changes
4. Write Tests
5. Update Documentation
6. Commit mit aussagekräftiger Message
7. Push to your Fork
8. Create Pull Request

### Commit Message Format

```
<type>: <subject>

<body>

<footer>
```

**Types:**
- `feat`: Neues Feature
- `fix`: Bug Fix
- `docs`: Dokumentation
- `style`: Code-Formatierung
- `refactor`: Code-Umstrukturierung
- `test`: Tests
- `chore`: Build/Dependencies

**Example:**
```
feat: Add dark mode toggle

- Implemented theme switcher in base.html
- Added CSS variables for dark theme
- Saved preference to localStorage
- Updated documentation

Closes #123
```

### Pull Request Template

```markdown
## Description
Kurze Beschreibung der Änderungen

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Manual testing performed
- [ ] All tests passing

## Checklist
- [ ] Code follows style guide
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
```

## 📚 Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Python asyncio](https://docs.python.org/3/library/asyncio.html)
- [Jinja2 Templates](https://jinja.palletsprojects.com/)
- [pytest](https://docs.pytest.org/)

---

**Happy Coding! 🚀**
