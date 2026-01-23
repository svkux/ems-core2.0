"""
EMS-Core v2.0 - Energy Sources API
REST API für Energy Sources Management
"""
from flask import Blueprint, request, jsonify
import logging
from dataclasses import asdict

logger = logging.getLogger(__name__)

# Blueprint
api_energy = Blueprint('api_energy', __name__, url_prefix='/api/energy')

# Global Manager (wird von app.py initialisiert)
energy_manager = None


def init_energy_api(manager):
    """Initialisiere API mit Manager"""
    global energy_manager
    energy_manager = manager


@api_energy.route('/sources', methods=['GET'])
def get_sources():
    """Hole alle Energy Sources"""
    try:
        sources = list(energy_manager.sources.values())
        return jsonify({
            'success': True,
            'sources': [asdict(s) for s in sources],
            'count': len(sources)
        })
    except Exception as e:
        logger.error(f"Failed to get sources: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_energy.route('/sources', methods=['POST'])
def add_source():
    """Füge neue Energy Source hinzu"""
    try:
        from core.energy_sources import EnergySource, SourceType, SourceProvider
        
        data = request.get_json()
        
        # Generate ID
        import time
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
            'source': asdict(source)
        })
    except Exception as e:
        logger.error(f"Failed to add source: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_energy.route('/sources/<source_id>', methods=['DELETE'])
def delete_source(source_id):
    """Lösche Energy Source"""
    try:
        energy_manager.remove_source(source_id)
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Failed to delete source: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_energy.route('/sources/<source_id>/toggle', methods=['POST'])
def toggle_source(source_id):
    """Enable/Disable Source"""
    try:
        data = request.get_json()
        source = energy_manager.sources.get(source_id)
        
        if source:
            source.enabled = data.get('enabled', True)
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Source not found'}), 404
    except Exception as e:
        logger.error(f"Failed to toggle source: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_energy.route('/current', methods=['GET'])
def get_current():
    """Hole aktuelle Energie-Werte"""
    try:
        data = energy_manager.get_current_data()
        return jsonify(data)
    except Exception as e:
        logger.error(f"Failed to get current data: {e}")
        return jsonify({'error': str(e)}), 500


@api_energy.route('/refresh', methods=['POST'])
def refresh():
    """Aktualisiere alle Quellen"""
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
        logger.error(f"Failed to refresh: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
