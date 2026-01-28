#!/usr/bin/env python3
"""
EMS-Core v2.0 - Override API
REST API für manuelle Device-Steuerung
"""
from flask import Blueprint, jsonify, request
import logging

from core.device_override import OverrideManager, OverrideMode

logger = logging.getLogger(__name__)

# Blueprint
api_override = Blueprint('api_override', __name__, url_prefix='/api/override')

# Global Manager (wird von init_override_api gesetzt)
override_manager = None


def init_override_api(manager: OverrideManager):
    """Initialisiere API mit OverrideManager"""
    global override_manager
    override_manager = manager
    logger.info("Override API initialized")


@api_override.route('/status', methods=['GET'])
def get_all_status():
    """
    GET /api/override/status
    
    Hole Override-Status für alle Devices
    
    Response:
    {
        "success": true,
        "overrides": {
            "device_1": {
                "mode": "manual_on",
                "active": true,
                "set_by": "user",
                "set_at": "2026-01-27T14:30:00",
                "expires_at": "2026-01-27T15:30:00"
            }
        },
        "statistics": {
            "total_overrides": 3,
            "manual_on": 2,
            "manual_off": 1
        }
    }
    """
    try:
        overrides_dict = {}
        for device_id, override in override_manager.get_all_overrides().items():
            overrides_dict[device_id] = override_manager.get_override_status(device_id)
        
        stats = override_manager.get_statistics()
        
        return jsonify({
            'success': True,
            'overrides': overrides_dict,
            'statistics': stats
        })
    except Exception as e:
        logger.error(f"Error getting override status: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_override.route('/<device_id>', methods=['GET'])
def get_device_status(device_id):
    """
    GET /api/override/{device_id}
    
    Hole Override-Status für ein Device
    
    Response:
    {
        "success": true,
        "device_id": "device_1",
        "mode": "manual_on",
        "active": true,
        "set_by": "user",
        "set_at": "2026-01-27T14:30:00"
    }
    """
    try:
        status = override_manager.get_override_status(device_id)
        
        return jsonify({
            'success': True,
            **status
        })
    except Exception as e:
        logger.error(f"Error getting override status for {device_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_override.route('/<device_id>', methods=['POST'])
def set_device_override(device_id):
    """
    POST /api/override/{device_id}
    
    Setze Override für ein Device
    
    Body:
    {
        "mode": "manual_on",        # "auto", "manual_on", "manual_off"
        "duration_minutes": 60,     # Optional
        "reason": "Testing"         # Optional
    }
    
    Response:
    {
        "success": true,
        "message": "Override set successfully",
        "device_id": "device_1",
        "mode": "manual_on"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'mode' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required field: mode'
            }), 400
        
        # Validiere Mode
        try:
            mode = OverrideMode(data['mode'])
        except ValueError:
            return jsonify({
                'success': False,
                'error': f"Invalid mode. Must be one of: auto, manual_on, manual_off"
            }), 400
        
        # Optional Parameters
        duration_minutes = data.get('duration_minutes')
        reason = data.get('reason', '')
        set_by = data.get('set_by', 'api')
        
        # Setze Override
        success = override_manager.set_override(
            device_id=device_id,
            mode=mode,
            set_by=set_by,
            duration_minutes=duration_minutes,
            reason=reason
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Override set successfully',
                'device_id': device_id,
                'mode': mode.value,
                'duration_minutes': duration_minutes
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to set override'
            }), 500
            
    except Exception as e:
        logger.error(f"Error setting override for {device_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_override.route('/<device_id>', methods=['DELETE'])
def clear_device_override(device_id):
    """
    DELETE /api/override/{device_id}
    
    Entferne Override (zurück zu AUTO)
    
    Response:
    {
        "success": true,
        "message": "Override cleared",
        "device_id": "device_1"
    }
    """
    try:
        success = override_manager.clear_override(device_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Override cleared',
                'device_id': device_id
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to clear override'
            }), 500
            
    except Exception as e:
        logger.error(f"Error clearing override for {device_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_override.route('/all', methods=['DELETE'])
def clear_all_overrides():
    """
    DELETE /api/override/all
    
    Entferne alle Overrides
    
    Response:
    {
        "success": true,
        "message": "Cleared 5 overrides",
        "count": 5
    }
    """
    try:
        count = override_manager.clear_all_overrides()
        
        return jsonify({
            'success': True,
            'message': f'Cleared {count} overrides',
            'count': count
        })
    except Exception as e:
        logger.error(f"Error clearing all overrides: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_override.route('/cleanup', methods=['POST'])
def cleanup_expired():
    """
    POST /api/override/cleanup
    
    Entferne abgelaufene Overrides
    
    Response:
    {
        "success": true,
        "message": "Cleaned up 2 expired overrides",
        "count": 2
    }
    """
    try:
        count = override_manager.cleanup_expired()
        
        return jsonify({
            'success': True,
            'message': f'Cleaned up {count} expired overrides',
            'count': count
        })
    except Exception as e:
        logger.error(f"Error cleaning up overrides: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# Convenience Endpoints für schnelles Schalten

@api_override.route('/<device_id>/manual_on', methods=['POST'])
def set_manual_on(device_id):
    """
    POST /api/override/{device_id}/manual_on
    
    Quick: Setze Device auf MANUAL_ON
    
    Body (optional):
    {
        "duration_minutes": 60,
        "reason": "Manual control"
    }
    """
    try:
        data = request.get_json() or {}
        
        success = override_manager.set_override(
            device_id=device_id,
            mode=OverrideMode.MANUAL_ON,
            set_by='api',
            duration_minutes=data.get('duration_minutes'),
            reason=data.get('reason', 'Manual ON')
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Device {device_id} set to MANUAL_ON',
                'device_id': device_id,
                'mode': 'manual_on'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to set override'
            }), 500
            
    except Exception as e:
        logger.error(f"Error setting manual_on for {device_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_override.route('/<device_id>/manual_off', methods=['POST'])
def set_manual_off(device_id):
    """
    POST /api/override/{device_id}/manual_off
    
    Quick: Setze Device auf MANUAL_OFF
    
    Body (optional):
    {
        "duration_minutes": 60,
        "reason": "Manual control"
    }
    """
    try:
        data = request.get_json() or {}
        
        success = override_manager.set_override(
            device_id=device_id,
            mode=OverrideMode.MANUAL_OFF,
            set_by='api',
            duration_minutes=data.get('duration_minutes'),
            reason=data.get('reason', 'Manual OFF')
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Device {device_id} set to MANUAL_OFF',
                'device_id': device_id,
                'mode': 'manual_off'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to set override'
            }), 500
            
    except Exception as e:
        logger.error(f"Error setting manual_off for {device_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_override.route('/<device_id>/auto', methods=['POST'])
def set_auto(device_id):
    """
    POST /api/override/{device_id}/auto
    
    Quick: Zurück zu AUTO (entferne Override)
    """
    try:
        success = override_manager.clear_override(device_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Device {device_id} set to AUTO',
                'device_id': device_id,
                'mode': 'auto'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to clear override'
            }), 500
            
    except Exception as e:
        logger.error(f"Error setting auto for {device_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
