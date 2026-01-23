#!/usr/bin/env python3
"""
EMS-Core v2.0 - Web UI
Flask Application mit Device Management
"""
from flask import Flask, render_template, jsonify
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.device_manager import DeviceManager
from core.integrations.discovery import DeviceDiscovery
from webui.api_routes import api, init_api

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask App erstellen
app = Flask(__name__)
app.config['SECRET_KEY'] = 'ems-core-secret-key-change-in-production'

# Initialisiere Manager
device_manager = DeviceManager()
device_discovery = DeviceDiscovery()

# Initialisiere API
init_api(device_manager, device_discovery)

# Registriere Blueprint
app.register_blueprint(api)


# ============================================================================
# Web UI Routes
# ============================================================================

@app.route('/')
def index():
    """Haupt-Dashboard"""
    return render_template('index.html')


@app.route('/devices')
def devices_page():
    """Device Management Page"""
    return render_template('devices.html')


@app.route('/discovery')
def discovery_page():
    """Device Discovery Page"""
    return render_template('discovery.html')


@app.route('/priorities')
def priorities_page():
    """Priorities Management Page"""
    return render_template('priorities.html')


@app.route('/schedules')
def schedules_page():
    """Schedules Management Page"""
    return render_template('schedules.html')


@app.route('/settings')
def settings_page():
    """Settings Page"""
    return render_template('settings.html')

@app.route('/energy_sources')
def energy_sources_page():
    """Energy Sources Page"""
    return render_template('energy_sources.html')

# ============================================================================
# Health Check
# ============================================================================

@app.route('/health')
def health():
    """Health Check Endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'EMS-Core Web UI',
        'version': '2.0'
    })


# ============================================================================
# Error Handlers
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {error}")
    return jsonify({'error': 'Internal server error'}), 500


# ============================================================================
# Main
# ============================================================================

if __name__ == '__main__':
    logger.info("Starting EMS-Core Web UI...")
    logger.info(f"Loaded {len(device_manager.devices)} devices")
    
    # Start Flask
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=True,
        threaded=True
    )


# Energy Sources
from core.energy_sources import EnergySourcesManager
from webui.api_energy import api_energy, init_energy_api

energy_manager = EnergySourcesManager()
init_energy_api(energy_manager)
app.register_blueprint(api_energy)
