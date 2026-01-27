#!/usr/bin/env python3
"""
EMS-Core v2.0 - Shelly Controller
Vollstaendige Implementierung fuer Shelly Gen1, Gen2, Plus, Pro
"""
import aiohttp
import asyncio
import logging
from typing import Optional, Dict
from enum import Enum

logger = logging.getLogger(__name__)


class ShellyGeneration(Enum):
    """Shelly Generationen"""
    GEN1 = "gen1"  # Shelly 1, 1PM, Plug, PlugS
    GEN2 = "gen2"  # Shelly Plus, Pro


class ShellyController:
    """Controller fuer alle Shelly Devices"""
    
    def __init__(self, ip: str, device_type: str = "shelly_plug"):
        self.ip = ip
        self.device_type = device_type
        self.generation = self._detect_generation(device_type)
        self.relay_id = 0  # Default relay
        
    def _detect_generation(self, device_type: str) -> ShellyGeneration:
        """Erkenne Shelly Generation anhand Typ"""
        gen2_types = ["shelly_plus_1pm", "shelly_pro_1pm", "shelly_pro_3em"]
        
        if any(t in device_type for t in gen2_types):
            return ShellyGeneration.GEN2
        return ShellyGeneration.GEN1
    
    async def turn_on(self) -> bool:
        """Schalte Device EIN"""
        try:
            if self.generation == ShellyGeneration.GEN1:
                url = f"http://{self.ip}/relay/{self.relay_id}?turn=on"
            else:  # GEN2
                url = f"http://{self.ip}/rpc/Switch.Set?id={self.relay_id}&on=true"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as response:
                    if response.status == 200:
                        logger.info(f"✓ Shelly {self.ip}: Turned ON")
                        return True
                    else:
                        logger.error(f"✗ Shelly {self.ip}: Failed to turn on (HTTP {response.status})")
                        return False
                        
        except Exception as e:
            logger.error(f"✗ Shelly {self.ip}: Turn on failed - {e}")
            return False
    
    async def turn_off(self) -> bool:
        """Schalte Device AUS"""
        try:
            if self.generation == ShellyGeneration.GEN1:
                url = f"http://{self.ip}/relay/{self.relay_id}?turn=off"
            else:  # GEN2
                url = f"http://{self.ip}/rpc/Switch.Set?id={self.relay_id}&on=false"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as response:
                    if response.status == 200:
                        logger.info(f"✓ Shelly {self.ip}: Turned OFF")
                        return True
                    else:
                        logger.error(f"✗ Shelly {self.ip}: Failed to turn off (HTTP {response.status})")
                        return False
                        
        except Exception as e:
            logger.error(f"✗ Shelly {self.ip}: Turn off failed - {e}")
            return False
    
    async def get_status(self) -> Optional[Dict]:
        """Hole vollstaendigen Status"""
        try:
            if self.generation == ShellyGeneration.GEN1:
                url = f"http://{self.ip}/status"
            else:  # GEN2
                url = f"http://{self.ip}/rpc/Shelly.GetStatus"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_status(data)
                    else:
                        logger.error(f"✗ Shelly {self.ip}: Status request failed (HTTP {response.status})")
                        return None
                        
        except Exception as e:
            logger.error(f"✗ Shelly {self.ip}: Status request failed - {e}")
            return None
    
    def _parse_status(self, data: Dict) -> Dict:
        """Parse Status-Response basierend auf Generation"""
        try:
            if self.generation == ShellyGeneration.GEN1:
                # Gen1 Format
                relay = data.get('relays', [{}])[self.relay_id]
                meter = data.get('meters', [{}])[self.relay_id] if 'meters' in data else {}
                
                return {
                    'online': True,
                    'state': 'on' if relay.get('ison', False) else 'off',
                    'power': meter.get('power', 0.0),
                    'voltage': meter.get('voltage', 0.0),
                    'temperature': data.get('temperature', 0.0),
                    'overtemperature': data.get('overtemperature', False),
                    'has_update': data.get('has_update', False)
                }
            
            else:  # GEN2
                # Gen2 Format
                switch = data.get(f'switch:{self.relay_id}', {})
                
                return {
                    'online': True,
                    'state': 'on' if switch.get('output', False) else 'off',
                    'power': switch.get('apower', 0.0),
                    'voltage': switch.get('voltage', 0.0),
                    'temperature': switch.get('temperature', {}).get('tC', 0.0),
                    'overtemperature': False,  # Gen2 hat das nicht direkt
                    'has_update': False
                }
                
        except Exception as e:
            logger.error(f"✗ Shelly {self.ip}: Failed to parse status - {e}")
            return {
                'online': False,
                'state': 'unknown',
                'power': 0.0,
                'voltage': 0.0,
                'temperature': 0.0,
                'overtemperature': False,
                'has_update': False
            }
    
    async def get_power(self) -> Optional[float]:
        """Hole nur Power-Wert (schneller)"""
        try:
            status = await self.get_status()
            if status:
                return status.get('power', 0.0)
            return None
            
        except Exception as e:
            logger.error(f"✗ Shelly {self.ip}: Power request failed - {e}")
            return None
    
    async def toggle(self) -> bool:
        """Toggle Device (Ein/Aus)"""
        try:
            status = await self.get_status()
            if status:
                if status['state'] == 'on':
                    return await self.turn_off()
                else:
                    return await self.turn_on()
            return False
            
        except Exception as e:
            logger.error(f"✗ Shelly {self.ip}: Toggle failed - {e}")
            return False
    
    async def test_connection(self) -> bool:
        """Test ob Device erreichbar ist"""
        try:
            status = await self.get_status()
            return status is not None and status.get('online', False)
            
        except Exception as e:
            logger.error(f"✗ Shelly {self.ip}: Connection test failed - {e}")
            return False


# Synchrone Wrapper fuer Flask (da Flask nicht async ist)
def create_controller(ip: str, device_type: str = "shelly_plug") -> ShellyController:
    """Factory fuer Shelly Controller"""
    return ShellyController(ip, device_type)


def turn_on_sync(ip: str, device_type: str = "shelly_plug") -> bool:
    """Synchrone Version von turn_on"""
    controller = ShellyController(ip, device_type)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(controller.turn_on())
    loop.close()
    return result


def turn_off_sync(ip: str, device_type: str = "shelly_plug") -> bool:
    """Synchrone Version von turn_off"""
    controller = ShellyController(ip, device_type)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(controller.turn_off())
    loop.close()
    return result


def get_status_sync(ip: str, device_type: str = "shelly_plug") -> Optional[Dict]:
    """Synchrone Version von get_status"""
    controller = ShellyController(ip, device_type)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(controller.get_status())
    loop.close()
    return result


def get_power_sync(ip: str, device_type: str = "shelly_plug") -> Optional[float]:
    """Synchrone Version von get_power"""
    controller = ShellyController(ip, device_type)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(controller.get_power())
    loop.close()
    return result
