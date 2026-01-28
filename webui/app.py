#!/usr/bin/env python3
"""
EMS-Core v2.0 - Web UI
Flask Application mit Device & Energy Management
"""
from flask import Flask, render_template, jsonify
import logging
import sys
import asyncio
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
energy_manager = None
try:
    from core.energy_sources import EnergySourcesManager
    from webui.api_energy import api_energy, init_energy_api
    
    energy_manager = EnergySourcesManager(config_file='/opt/ems-core/config/energy_sources.json')
    init_energy_api(energy_manager)
    app.register_blueprint(api_energy)
    logger.info("✓ Energy Sources API registered")
except Exception as e:
    logger.error(f"✗ Failed to load Energy API: {e}")

# Override Manager
override_manager = None
try:
    from core.device_override import OverrideManager
    from webui.api_override import api_override, init_override_api
    
    override_manager = OverrideManager(overrides_file='/opt/ems-core/config/device_overrides.json')
    init_override_api(override_manager)
    app.register_blueprint(api_override)
    logger.info("✓ Override API registered")
except Exception as e:
    logger.error(f"✗ Failed to load Override API: {e}")


# Helper function for async calls in Flask routes
def run_async(coro):
    """
    Helper um async Funktionen in sync Flask Routes zu benutzen
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)


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


@app.route('/dashboard')
def dashboard():
    """Dashboard mit Live-Übersicht"""
    return render_template('dashboard.html')


@app.route('/api/dashboard/summary')
def dashboard_summary():
    """
    Dashboard Summary Endpoint
    Liefert alle wichtigen Daten für das Dashboard
    """
    try:
        # Energy Data
        energy_data = {}
        if energy_manager:
            energy_data = energy_manager.get_current_data()
        
        # Device Stats
        device_stats = device_manager.get_statistics()
        
        # Active Devices (enabled und on)
        active_devices = []
        for device in device_manager.get_all_devices():
            if device.enabled:
                active_devices.append({
                    'id': device.id,
                    'name': device.name,
                    'type': device.type,
                    'priority': device.priority,
                    'power': device.power
                })
        
        return jsonify({
            'success': True,
            'energy': energy_data,
            'device_stats': device_stats,
            'active_devices': active_devices,
            'timestamp': energy_data.get('last_update', None)
        })
    except Exception as e:
        logger.error(f"Dashboard summary error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'EMS-Core Web UI',
        'version': '2.0',
        'components': {
            'device_manager': len(device_manager.devices),
            'energy_manager': len(energy_manager.sources) if energy_manager else 0
        }
    })


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {error}")
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    logger.info("="*60)
    logger.info("🚀 EMS-Core v2.0 - Web UI")
    logger.info("="*60)
    logger.info(f"✅ Loaded {len(device_manager.devices)} devices")
    if energy_manager:
        logger.info(f"✅ Loaded {len(energy_manager.sources)} energy sources")
    logger.info("")
    logger.info("🌐 Starting Web UI on http://0.0.0.0:8080")
    logger.info("="*60)
    
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=True,
        threaded=True
    )
