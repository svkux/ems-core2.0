"""
EMS-Core v2.0 - Web UI API Routes
REST API fuer Device Management + Control
"""
from flask import Blueprint, request, jsonify
import logging
from dataclasses import asdict

from core.device_manager import DeviceManager, DeviceConfig
from core.integrations.discovery import DeviceDiscovery
from core.controllers.shelly import get_status_sync, turn_on_sync, turn_off_sync, get_power_sync

logger = logging.getLogger(__name__)

# Blueprint erstellen
api = Blueprint('api', __name__, url_prefix='/api')

# Global Manager (wird von app.py initialisiert)
device_manager = None
device_discovery = None


def init_api(manager: DeviceManager, discovery: DeviceDiscovery):
    """Initialisiere API mit Manager-Instanzen"""
    global device_manager, device_discovery
    device_manager = manager
    device_discovery = discovery


# ============================================================================
# Device CRUD Endpoints
# ============================================================================

@api.route('/devices', methods=['GET'])
def get_devices():
    """Hole alle Geraete"""
    try:
        devices = device_manager.get_all_devices()
        return jsonify({
            'success': True,
            'devices': [asdict(d) for d in devices],
            'count': len(devices)
        })
    except Exception as e:
        logger.error(f"Failed to get devices: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api.route('/devices/<device_id>', methods=['GET'])
def get_device(device_id):
    """Hole einzelnes Geraet"""
    try:
        device = device_manager.get_device(device_id)
        if device:
            return jsonify({
                'success': True,
                'device': asdict(device)
            })
        else:
            return jsonify({'success': False, 'error': 'Device not found'}), 404
    except Exception as e:
        logger.error(f"Failed to get device: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api.route('/devices', methods=['POST'])
def add_device():
    """Fuege neues Geraet hinzu"""
    try:
        data = request.get_json()
        
        # Erstelle DeviceConfig
        device = DeviceConfig(**data)
        
        # Validiere
        valid, message = device_manager.validate_device(device)
        if not valid:
            return jsonify({'success': False, 'error': message}), 400
        
        # Hinzufuegen
        success = device_manager.add_device(device)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Device added successfully',
                'device': asdict(device)
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to add device'}), 500
            
    except Exception as e:
        logger.error(f"Failed to add device: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api.route('/devices/<device_id>', methods=['PUT'])
def update_device(device_id):
    """Update Geraet"""
    try:
        data = request.get_json()
        
        success = device_manager.update_device(device_id, data)
        
        if success:
            device = device_manager.get_device(device_id)
            return jsonify({
                'success': True,
                'message': 'Device updated successfully',
                'device': asdict(device)
            })
        else:
            return jsonify({'success': False, 'error': 'Device not found'}), 404
            
    except Exception as e:
        logger.error(f"Failed to update device: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api.route('/devices/<device_id>', methods=['DELETE'])
def delete_device(device_id):
    """Loesche Geraet"""
    try:
        success = device_manager.remove_device(device_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Device deleted successfully'
            })
        else:
            return jsonify({'success': False, 'error': 'Device not found'}), 404
            
    except Exception as e:
        logger.error(f"Failed to delete device: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# Device Control Endpoints
# ============================================================================

@api.route('/devices/<device_id>/control', methods=['POST'])
def control_device(device_id):
    """Steuere Geraet (ON/OFF/TOGGLE)"""
    try:
        data = request.get_json()
        action = data.get('action')  # 'on', 'off', 'toggle'
        
        device = device_manager.get_device(device_id)
        if not device:
            return jsonify({'success': False, 'error': 'Device not found'}), 404
        
        if not device.can_control:
            return jsonify({'success': False, 'error': 'Device not controllable'}), 400
        
        # Pruefe Device-Typ und rufe entsprechenden Controller auf
        if 'shelly' in device.type:
            ip = device.connection_params.get('ip')
            if not ip:
                return jsonify({'success': False, 'error': 'No IP address configured'}), 400
            
            # Fuehre Control-Aktion aus
            if action == 'on':
                success = turn_on_sync(ip, device.type)
            elif action == 'off':
                success = turn_off_sync(ip, device.type)
            elif action == 'toggle':
                # Toggle: erst Status holen, dann umschalten
                status = get_status_sync(ip, device.type)
                if status and status.get('state') == 'on':
                    success = turn_off_sync(ip, device.type)
                else:
                    success = turn_on_sync(ip, device.type)
            else:
                return jsonify({'success': False, 'error': f'Unknown action: {action}'}), 400
            
            if success:
                return jsonify({
                    'success': True,
                    'message': f'Device {device_id} turned {action}',
                    'device_id': device_id,
                    'action': action
                })
            else:
                return jsonify({'success': False, 'error': f'Failed to execute {action}'}), 500
        
        else:
            return jsonify({'success': False, 'error': f'Control not implemented for device type: {device.type}'}), 501
        
    except Exception as e:
        logger.error(f"Control failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api.route('/devices/<device_id>/status', methods=['GET'])
def device_status(device_id):
    """Hole Geraete-Status (Echtzeit von Hardware)"""
    try:
        device = device_manager.get_device(device_id)
        if not device:
            return jsonify({'success': False, 'error': 'Device not found'}), 404
        
        # Pruefe Device-Typ und rufe entsprechenden Controller auf
        if 'shelly' in device.type:
            ip = device.connection_params.get('ip')
            if not ip:
                return jsonify({'success': False, 'error': 'No IP address configured'}), 400
            
            status = get_status_sync(ip, device.type)
            
            if status:
                return jsonify({
                    'success': True,
                    'device_id': device_id,
                    'status': status
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Failed to read device status'
                }), 500
        
        else:
            return jsonify({
                'success': False,
                'error': f'Status reading not implemented for device type: {device.type}'
            }), 501
        
    except Exception as e:
        logger.error(f"Status failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api.route('/devices/<device_id>/power', methods=['GET'])
def device_power(device_id):
    """Hole nur aktuellen Power-Wert (schneller als vollstaendiger Status)"""
    try:
        device = device_manager.get_device(device_id)
        if not device:
            return jsonify({'success': False, 'error': 'Device not found'}), 404
        
        # Pruefe Device-Typ
        if 'shelly' in device.type:
            ip = device.connection_params.get('ip')
            if not ip:
                return jsonify({'success': False, 'error': 'No IP address configured'}), 400
            
            power = get_power_sync(ip, device.type)
            
            if power is not None:
                return jsonify({
                    'success': True,
                    'device_id': device_id,
                    'power': power,
                    'unit': 'W'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Failed to read power'
                }), 500
        
        else:
            return jsonify({
                'success': False,
                'error': f'Power reading not implemented for device type: {device.type}'
            }), 501
        
    except Exception as e:
        logger.error(f"Power reading failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api.route('/devices/control/batch', methods=['POST'])
def control_devices_batch(device_id):
    """Steuere mehrere Geraete gleichzeitig"""
    try:
        data = request.get_json()
        device_ids = data.get('device_ids', [])
        action = data.get('action')  # 'on', 'off'
        
        if not device_ids:
            return jsonify({'success': False, 'error': 'No device IDs provided'}), 400
        
        results = []
        errors = []
        
        for device_id in device_ids:
            try:
                device = device_manager.get_device(device_id)
                if not device:
                    errors.append(f'{device_id}: Not found')
                    continue
                
                if not device.can_control:
                    errors.append(f'{device_id}: Not controllable')
                    continue
                
                if 'shelly' in device.type:
                    ip = device.connection_params.get('ip')
                    if not ip:
                        errors.append(f'{device_id}: No IP configured')
                        continue
                    
                    if action == 'on':
                        success = turn_on_sync(ip, device.type)
                    elif action == 'off':
                        success = turn_off_sync(ip, device.type)
                    else:
                        errors.append(f'{device_id}: Unknown action')
                        continue
                    
                    if success:
                        results.append(device_id)
                    else:
                        errors.append(f'{device_id}: Control failed')
                
            except Exception as e:
                errors.append(f'{device_id}: {str(e)}')
        
        return jsonify({
            'success': len(results) > 0,
            'controlled': results,
            'failed': errors,
            'count_success': len(results),
            'count_failed': len(errors)
        })
        
    except Exception as e:
        logger.error(f"Batch control failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# Device Discovery Endpoints
# ============================================================================

@api.route('/devices/discover', methods=['POST'])
def discover_devices():
    """Starte Device Discovery"""
    try:
        data = request.get_json() or {}
        network = data.get('network', '10.0.0.0/24')
        
        logger.info(f"Starting discovery on network: {network}")
        
        # Run discovery
        discovered = device_discovery.scan_network(network) if device_discovery else []
        
        return jsonify({
            'success': True,
            'discovered': discovered,
            'count': len(discovered)
        })
        
    except Exception as e:
        logger.error(f"Discovery failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api.route('/devices/import', methods=['POST'])
def import_devices():
    """Importiere entdeckte Geraete"""
    try:
        data = request.get_json()
        discovered = data.get('devices', [])
        
        imported = device_manager.import_discovered_devices(discovered)
        
        return jsonify({
            'success': True,
            'imported': imported,
            'message': f'Successfully imported {imported} devices'
        })
        
    except Exception as e:
        logger.error(f"Import failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# Device Search & Filter
# ============================================================================

@api.route('/devices/search', methods=['GET'])
def search_devices():
    """Suche Geraete"""
    try:
        query = request.args.get('q', '')
        
        results = device_manager.search_devices(query)
        
        return jsonify({
            'success': True,
            'results': [asdict(d) for d in results],
            'count': len(results)
        })
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api.route('/devices/filter', methods=['GET'])
def filter_devices():
    """Filtere Geraete"""
    try:
        device_type = request.args.get('type')
        category = request.args.get('category')
        priority = request.args.get('priority')
        enabled = request.args.get('enabled')
        
        devices = device_manager.get_all_devices()
        
        # Apply filters
        if device_type:
            devices = [d for d in devices if d.type == device_type]
        if category:
            devices = [d for d in devices if d.category == category]
        if priority:
            devices = [d for d in devices if d.priority == priority]
        if enabled is not None:
            enabled_bool = enabled.lower() == 'true'
            devices = [d for d in devices if d.enabled == enabled_bool]
        
        return jsonify({
            'success': True,
            'devices': [asdict(d) for d in devices],
            'count': len(devices)
        })
        
    except Exception as e:
        logger.error(f"Filter failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# Device Statistics
# ============================================================================

@api.route('/devices/stats', methods=['GET'])
def device_statistics():
    """Hole Device-Statistiken"""
    try:
        stats = device_manager.get_statistics()
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
        
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# Export/Import
# ============================================================================

@api.route('/devices/export', methods=['GET'])
def export_devices():
    """Exportiere alle Geraete"""
    try:
        export_data = device_manager.export_to_dict()
        
        return jsonify({
            'success': True,
            'data': export_data
        })
        
    except Exception as e:
        logger.error(f"Export failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# Device Types & Categories
# ============================================================================

@api.route('/devices/types', methods=['GET'])
def get_device_types():
    """Hole verfuegbare Geraete-Typen"""
    types = [
        {'value': 'shelly_plug', 'label': 'Shelly Plug'},
        {'value': 'shelly_1pm', 'label': 'Shelly 1PM'},
        {'value': 'shelly_plus_1pm', 'label': 'Shelly Plus 1PM'},
        {'value': 'shelly_pro_1pm', 'label': 'Shelly Pro 1PM'},
        {'value': 'shelly_pro_3em', 'label': 'Shelly Pro 3EM'},
        {'value': 'solax', 'label': 'Solax Inverter'},
        {'value': 'sdm630', 'label': 'SDM630 Meter'},
        {'value': 'sg_ready', 'label': 'SG-Ready Heatpump'},
        {'value': 'generic', 'label': 'Generic Device'},
    ]
    
    return jsonify({
        'success': True,
        'types': types
    })


@api.route('/devices/priorities', methods=['GET'])
def get_priorities():
    """Hole verfuegbare Prioritaeten"""
    priorities = [
        {'value': 'CRITICAL', 'label': 'Critical', 'description': 'Always ON'},
        {'value': 'HIGH', 'label': 'High', 'description': 'High priority'},
        {'value': 'MEDIUM', 'label': 'Medium', 'description': 'Medium priority'},
        {'value': 'LOW', 'label': 'Low', 'description': 'Low priority'},
        {'value': 'OPTIONAL', 'label': 'Optional', 'description': 'Only with surplus'},
    ]
    
    return jsonify({
        'success': True,
        'priorities': priorities
    })


@api.route('/devices/categories', methods=['GET'])
def get_categories():
    """Hole verfuegbare Kategorien"""
    categories = [
        {'value': 'appliance', 'label': 'Appliance'},
        {'value': 'heating', 'label': 'Heating'},
        {'value': 'cooling', 'label': 'Cooling'},
        {'value': 'ev_charging', 'label': 'EV Charging'},
        {'value': 'lighting', 'label': 'Lighting'},
        {'value': 'entertainment', 'label': 'Entertainment'},
        {'value': 'monitoring', 'label': 'Monitoring'},
        {'value': 'other', 'label': 'Other'},
    ]
    
    return jsonify({
        'success': True,
        'categories': categories
    })
