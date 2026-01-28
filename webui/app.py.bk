#!/usr/bin/env python3
"""
EMS-Core v2.0 - Web UI
Flask Application mit Device & Energy Management
"""
from flask import Flask, render_template, jsonify
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.device_manager import DeviceManager
from webui.api_routes import api, init_api

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask App
app = Flask(__name__)
app.config['SECRET_KEY'] = 'ems-core-secret-key'

# Device Manager
device_manager = DeviceManager()
init_api(device_manager, None)
app.register_blueprint(api)

# Energy Sources Manager
try:
    from core.energy_sources import EnergySourcesManager
    from webui.api_energy import api_energy, init_energy_api
    
    energy_manager = EnergySourcesManager(config_file='/opt/ems-core/config/energy_sources.json')
    init_energy_api(energy_manager)
    app.register_blueprint(api_energy)
    logger.info("✓ Energy Sources API registered")
except Exception as e:
    logger.error(f"✗ Failed to load Energy API: {e}")

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/devices')
def devices_page():
    return render_template('devices.html')

@app.route('/energy_sources')
def energy_sources_page():
    return render_template('energy_sources.html')

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'EMS-Core Web UI',
        'version': '2.0'
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info("Starting EMS-Core Web UI...")
    logger.info(f"Loaded {len(device_manager.devices)} devices")
    
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=True,
        threaded=True
    )
