#!/usr/bin/env python3
"""
EMS-Core v2.0 - Device Override Manager
Manuelles Überschreiben von automatischer Steuerung
"""
import json
import logging
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class OverrideMode(Enum):
    """Override Modi"""
    AUTO = "auto"              # Automatische Steuerung (PV + Schedule)
    MANUAL_ON = "manual_on"    # Manuell EIN (überschreibt alles)
    MANUAL_OFF = "manual_off"  # Manuell AUS (überschreibt alles)


class DeviceOverride:
    """Override-Status für ein Device"""
    
    def __init__(self, 
                 device_id: str,
                 mode: OverrideMode = OverrideMode.AUTO,
                 set_by: str = "system",
                 set_at: Optional[str] = None,
                 expires_at: Optional[str] = None,
                 reason: str = ""):
        self.device_id = device_id
        self.mode = mode
        self.set_by = set_by  # "user", "system", "api"
        self.set_at = set_at or datetime.now().isoformat()
        self.expires_at = expires_at  # Optional: Auto-Reset nach X Minuten
        self.reason = reason
    
    def is_expired(self) -> bool:
        """Prüfe ob Override abgelaufen ist"""
        if not self.expires_at:
            return False
        
        try:
            expires = datetime.fromisoformat(self.expires_at)
            return datetime.now() > expires
        except:
            return False
    
    def to_dict(self) -> Dict:
        """Konvertiere zu Dict"""
        return {
            'device_id': self.device_id,
            'mode': self.mode.value,
            'set_by': self.set_by,
            'set_at': self.set_at,
            'expires_at': self.expires_at,
            'reason': self.reason
        }


class OverrideManager:
    """Manager für Device Overrides"""
    
    def __init__(self, overrides_file: str = "config/device_overrides.json"):
        self.overrides_file = Path(overrides_file)
        self.overrides: Dict[str, DeviceOverride] = {}
        
        self.load_overrides()
    
    def load_overrides(self):
        """Lade Overrides aus JSON"""
        try:
            if self.overrides_file.exists():
                with open(self.overrides_file, 'r') as f:
                    data = json.load(f)
                
                for override_data in data.get('overrides', []):
                    override = DeviceOverride(
                        device_id=override_data['device_id'],
                        mode=OverrideMode(override_data['mode']),
                        set_by=override_data.get('set_by', 'system'),
                        set_at=override_data.get('set_at'),
                        expires_at=override_data.get('expires_at'),
                        reason=override_data.get('reason', '')
                    )
                    
                    # Prüfe ob abgelaufen
                    if not override.is_expired():
                        self.overrides[override.device_id] = override
                    else:
                        logger.info(f"Override for {override.device_id} expired")
                
                logger.info(f"✅ Loaded {len(self.overrides)} device overrides")
            else:
                logger.info("ℹ️ No overrides file found")
        except Exception as e:
            logger.error(f"❌ Failed to load overrides: {e}", exc_info=True)
    
    def save_overrides(self):
        """Speichere Overrides als JSON"""
        try:
            self.overrides_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Filter abgelaufene Overrides
            active_overrides = []
            for override in self.overrides.values():
                if not override.is_expired():
                    active_overrides.append(override.to_dict())
            
            data = {
                'overrides': active_overrides,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.overrides_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.debug(f"💾 Saved {len(active_overrides)} overrides")
        except Exception as e:
            logger.error(f"❌ Failed to save overrides: {e}", exc_info=True)
    
    def set_override(self, 
                    device_id: str, 
                    mode: OverrideMode,
                    set_by: str = "user",
                    duration_minutes: Optional[int] = None,
                    reason: str = "") -> bool:
        """
        Setze Override für ein Device
        
        Args:
            device_id: Device ID
            mode: Override Mode (AUTO, MANUAL_ON, MANUAL_OFF)
            set_by: Wer hat Override gesetzt (user, system, api)
            duration_minutes: Optional - Override läuft nach X Minuten ab
            reason: Optionaler Grund
            
        Returns:
            True wenn erfolgreich
        """
        try:
            # Berechne Ablauf-Zeit
            expires_at = None
            if duration_minutes:
                expires_at = (datetime.now() + timedelta(minutes=duration_minutes)).isoformat()
            
            override = DeviceOverride(
                device_id=device_id,
                mode=mode,
                set_by=set_by,
                expires_at=expires_at,
                reason=reason
            )
            
            # Speichere oder entferne Override
            if mode == OverrideMode.AUTO:
                # AUTO = kein Override mehr
                if device_id in self.overrides:
                    del self.overrides[device_id]
                    logger.info(f"🔓 Removed override for {device_id} - back to AUTO")
            else:
                self.overrides[device_id] = override
                expires_msg = f" (expires in {duration_minutes}min)" if duration_minutes else ""
                logger.info(f"🔒 Set override for {device_id}: {mode.value}{expires_msg}")
            
            self.save_overrides()
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to set override: {e}", exc_info=True)
            return False
    
    def get_override(self, device_id: str) -> Optional[DeviceOverride]:
        """
        Hole Override für ein Device
        
        Returns:
            DeviceOverride oder None wenn kein Override aktiv
        """
        override = self.overrides.get(device_id)
        
        # Prüfe ob abgelaufen
        if override and override.is_expired():
            logger.info(f"Override for {device_id} expired, removing")
            del self.overrides[device_id]
            self.save_overrides()
            return None
        
        return override
    
    def clear_override(self, device_id: str) -> bool:
        """
        Entferne Override (zurück zu AUTO)
        
        Returns:
            True wenn erfolgreich
        """
        return self.set_override(device_id, OverrideMode.AUTO)
    
    def clear_all_overrides(self) -> int:
        """
        Entferne alle Overrides
        
        Returns:
            Anzahl entfernter Overrides
        """
        count = len(self.overrides)
        self.overrides = {}
        self.save_overrides()
        logger.info(f"🔓 Cleared all {count} overrides")
        return count
    
    def get_all_overrides(self) -> Dict[str, DeviceOverride]:
        """Hole alle aktiven Overrides"""
        # Filter abgelaufene
        active = {}
        for device_id, override in list(self.overrides.items()):
            if not override.is_expired():
                active[device_id] = override
            else:
                del self.overrides[device_id]
        
        if len(active) != len(self.overrides):
            self.save_overrides()
        
        return active
    
    def get_override_status(self, device_id: str) -> Dict:
        """
        Hole Override-Status für ein Device
        
        Returns:
            Dict mit Status-Info
        """
        override = self.get_override(device_id)
        
        if not override:
            return {
                'device_id': device_id,
                'mode': 'auto',
                'active': False
            }
        
        return {
            'device_id': device_id,
            'mode': override.mode.value,
            'active': True,
            'set_by': override.set_by,
            'set_at': override.set_at,
            'expires_at': override.expires_at,
            'reason': override.reason
        }
    
    def check_override_decision(self, device_id: str) -> Optional[Dict]:
        """
        Prüfe ob Override eine Entscheidung erzwingt
        
        Returns:
            Decision Dict oder None wenn kein Override
        """
        override = self.get_override(device_id)
        
        if not override:
            return None
        
        if override.mode == OverrideMode.MANUAL_ON:
            return {
                'allowed': True,
                'action': 'force_on',
                'reason': f'Manual Override: ON{" - " + override.reason if override.reason else ""}',
                'override': True,
                'set_by': override.set_by,
                'set_at': override.set_at
            }
        
        elif override.mode == OverrideMode.MANUAL_OFF:
            return {
                'allowed': False,
                'action': 'force_off',
                'reason': f'Manual Override: OFF{" - " + override.reason if override.reason else ""}',
                'override': True,
                'set_by': override.set_by,
                'set_at': override.set_at
            }
        
        return None
    
    def get_statistics(self) -> Dict:
        """Hole Statistiken"""
        stats = {
            'total_overrides': len(self.overrides),
            'manual_on': 0,
            'manual_off': 0,
            'with_expiry': 0,
            'by_setter': {}
        }
        
        for override in self.overrides.values():
            if override.mode == OverrideMode.MANUAL_ON:
                stats['manual_on'] += 1
            elif override.mode == OverrideMode.MANUAL_OFF:
                stats['manual_off'] += 1
            
            if override.expires_at:
                stats['with_expiry'] += 1
            
            stats['by_setter'][override.set_by] = stats['by_setter'].get(override.set_by, 0) + 1
        
        return stats
    
    def cleanup_expired(self) -> int:
        """
        Entferne alle abgelaufenen Overrides
        
        Returns:
            Anzahl entfernter Overrides
        """
        removed = 0
        for device_id, override in list(self.overrides.items()):
            if override.is_expired():
                del self.overrides[device_id]
                removed += 1
        
        if removed > 0:
            self.save_overrides()
            logger.info(f"🧹 Cleaned up {removed} expired overrides")
        
        return removed


if __name__ == "__main__":
    # Test
    logging.basicConfig(level=logging.INFO)
    
    print("\n" + "="*60)
    print("EMS Override Manager - Test")
    print("="*60)
    
    manager = OverrideManager()
    
    # Test Override setzen
    print("\n1. Set MANUAL_ON Override:")
    manager.set_override(
        device_id="test_device_1",
        mode=OverrideMode.MANUAL_ON,
        set_by="user",
        duration_minutes=60,
        reason="Testing manual control"
    )
    
    # Status abrufen
    status = manager.get_override_status("test_device_1")
    print(f"Status: {status}")
    
    # Decision prüfen
    decision = manager.check_override_decision("test_device_1")
    print(f"Decision: {decision}")
    
    # Statistiken
    stats = manager.get_statistics()
    print(f"\n2. Statistics:")
    print(f"  Total Overrides: {stats['total_overrides']}")
    print(f"  Manual ON: {stats['manual_on']}")
    print(f"  Manual OFF: {stats['manual_off']}")
    
    # Clear Override
    print("\n3. Clear Override:")
    manager.clear_override("test_device_1")
    status = manager.get_override_status("test_device_1")
    print(f"Status after clear: {status}")
    
    print("\n" + "="*60)
