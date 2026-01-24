"""
EMS-Core v2.0 - Energy Sources API
"""
from flask import Blueprint, request, jsonify
import logging

logger = logging.getLogger(__name__)

api_energy = Blueprint('api_energy', __name__, url_prefix='/api/energy')
energy_manager = None

def init_energy_api(manager):
    global energy_manager
    energy_manager = manager

def source_to_dict(source):
    """Convert EnergySource to dict with Enums as strings"""
    return {
        'id': source.id,
        'name': source.name,
        'type': source.type.value,
        'provider': source.provider.value,
        'config': source.config,
        'enabled': source.enabled,
        'last_value': source.last_value,
        'last_update': source.last_update
    }

@api_energy.route('/sources', methods=['GET'])
def get_sources():
    try:
        sources = [source_to_dict(s) for s in energy_manager.sources.values()]
        return jsonify({
            'success': True,
            'sources': sources,
            'count': len(sources)
        })
    except Exception as e:
        logger.error(f"Failed to get sources: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@api_energy.route('/sources', methods=['POST'])
def add_source():
    try:
        from core.energy_sources import EnergySource, SourceType, SourceProvider
        import time
        
        data = request.get_json()
        source_id = f"{data['type']}_{int(time.time())}"
        
        source = EnergySource(
            id=source_id,
            name=data['name'],
            type=SourceType(data['type']),
            provider=SourceProvider(data['provider']),
            config=data['config'],
            enabled=data.get('enabled', True)
        )
        
        energy_manager.add_source(source)
        
        return jsonify({
            'success': True,
            'source': source_to_dict(source)
        })
    except Exception as e:
        logger.error(f"Failed to add source: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@api_energy.route('/sources/<source_id>', methods=['DELETE'])
def delete_source(source_id):
    try:
        energy_manager.remove_source(source_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_energy.route('/sources/<source_id>/toggle', methods=['POST'])
def toggle_source(source_id):
    try:
        data = request.get_json()
        source = energy_manager.sources.get(source_id)
        
        if source:
            source.enabled = data.get('enabled', True)
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'Not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_energy.route('/current', methods=['GET'])
def get_current():
    try:
        return jsonify(energy_manager.get_current_data())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_energy.route('/refresh', methods=['POST'])
def refresh():
    try:
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(energy_manager.update_all_sources())
        
        return jsonify({
            'success': True,
            'data': energy_manager.get_current_data()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
