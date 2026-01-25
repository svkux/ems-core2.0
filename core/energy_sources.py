#!/usr/bin/env python3
"""
EMS-Core v2.0 - Energy Sources Manager
Verwaltet verschiedene Energie-Datenquellen (PV, Grid, etc.)
"""
import asyncio
import logging
from typing import Dict, Optional, List
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class SourceType(Enum):
    """Energie-Quellen Typen"""
    PV_GENERATION = "pv_generation"
    GRID_POWER = "grid_power"
    BATTERY = "battery"
    HOUSE_CONSUMPTION = "house_consumption"


class SourceProvider(Enum):
    """Provider für Datenquellen"""
    HOME_ASSISTANT = "home_assistant"
    SHELLY = "shelly"
    SHELLY_3EM = "shelly_3em"
    SOLAX_MODBUS = "solax_modbus"
    SDM630_MODBUS = "sdm630_modbus"
    SHELLY_PRO_3EM = "shelly_pro_3em"
    CALCULATED = "calculated"


@dataclass
class EnergySource:
    """Definition einer Energie-Datenquelle"""
    id: str
    name: str
    type: SourceType
    provider: SourceProvider
    config: Dict
    enabled: bool = True
    last_value: float = 0.0
    last_update: Optional[str] = None


class EnergySourcesManager:
    """Manager für alle Energie-Datenquellen"""
    
    def __init__(self):
        self.sources: Dict[str, EnergySource] = {}
        
        # Controller
        self.controllers = {}
        
        # Aktuelle Werte
        self.current_data = {
            'pv_power': 0.0,
            'grid_power': 0.0,
            'battery_power': 0.0,
            'battery_soc': 0.0,
            'house_consumption': 0.0,
            'available_power': 0.0
        }
    
    def add_source(self, source: EnergySource):
        """Füge Datenquelle hinzu"""
        self.sources[source.id] = source
        logger.info(f"Added energy source: {source.name} ({source.type.value} via {source.provider.value})")
    
    def remove_source(self, source_id: str):
        """Entferne Datenquelle"""
        if source_id in self.sources:
            del self.sources[source_id]
            logger.info(f"Removed energy source: {source_id}")
    
    async def read_home_assistant(self, config: Dict) -> Optional[float]:
        """Lese Wert von Home Assistant"""
        try:
            import aiohttp
            
            url = f"{config['url']}/api/states/{config['entity_id']}"
            headers = {
                "Authorization": f"Bearer {config['token']}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        value = float(data['state'])
                        logger.debug(f"HA {config['entity_id']}: {value}W")
                        return value
                    else:
                        logger.error(f"HA API error: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Failed to read from Home Assistant: {e}")
            return None
    
    async def read_shelly_3em(self, config: Dict) -> Optional[Dict]:
        """
        Lese Wert von Shelly 3EM (Gen1)
        
        Returns: {"total_power": 1865.3, "phase_a": 1611.5, ...}
        """
        try:
            import aiohttp
            
            url = f"http://{config['ip']}/status"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if 'emeters' in data:
                            emeters = data['emeters']
                            result = {
                                'total_power': data.get('total_power', 0),
                                'phase_a': emeters[0].get('power', 0) if len(emeters) > 0 else 0,
                                'phase_b': emeters[1].get('power', 0) if len(emeters) > 1 else 0,
                                'phase_c': emeters[2].get('power', 0) if len(emeters) > 2 else 0
                            }
                            
                            logger.info(f"Shelly 3EM: {result['total_power']}W (A:{result['phase_a']}W, B:{result['phase_b']}W, C:{result['phase_c']}W)")
                            return result
                        else:
                            logger.error(f"Unknown Shelly 3EM format")
                            return None
                    else:
                        logger.error(f"Shelly 3EM error: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Failed to read from Shelly 3EM: {e}")
            return None
    
    async def read_shelly(self, config: Dict) -> Optional[float]:
        """Lese Wert von Shelly Gen1/2"""
        try:
            import aiohttp
            
            url = f"http://{config['ip']}/status"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Shelly Gen2/Plus
                        if 'switch:0' in data:
                            switch_data = data[f"switch:{config.get('channel', 0)}"]
                            value = switch_data.get(config.get('metric', 'apower'), 0)
                        # Shelly Gen1
                        elif 'meters' in data:
                            meter = data['meters'][config.get('channel', 0)]
                            value = meter.get(config.get('metric', 'power'), 0)
                        else:
                            logger.error(f"Unknown Shelly format")
                            return None
                        
                        logger.debug(f"Shelly {config['ip']}: {value}W")
                        return float(value)
                    else:
                        logger.error(f"Shelly error: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Failed to read from Shelly: {e}")
            return None
    
    async def read_shelly_pro_3em(self, config: Dict) -> Optional[Dict]:
        """Lese Wert von Shelly Pro 3EM"""
        try:
            import aiohttp
            
            url = f"http://{config['ip']}/rpc/EM.GetStatus?id=0"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        result = {
                            'total_power': data.get('total_act_power', 0),
                            'phase_a': data.get('a_act_power', 0),
                            'phase_b': data.get('b_act_power', 0),
                            'phase_c': data.get('c_act_power', 0)
                        }
                        
                        logger.debug(f"Shelly Pro 3EM: {result['total_power']}W")
                        return result
                    else:
                        logger.error(f"Shelly Pro 3EM error: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Failed to read from Shelly Pro 3EM: {e}")
            return None
    
    async def read_solax_modbus(self, config: Dict) -> Optional[Dict]:
        """Lese Daten von Solax via Modbus"""
        try:
            from core.controllers.solax import SolaxModbusController
            
            if 'solax_controller' not in self.controllers:
                self.controllers['solax_controller'] = SolaxModbusController(
                    host=config['ip'],
                    port=config.get('port', 502),
                    unit_id=config.get('unit_id', 1)
                )
            
            controller = self.controllers['solax_controller']
            data = await controller.read_realtime_data()
            
            if data:
                logger.debug(f"Solax: PV={data.get('pv_power', 0)}W, Grid={data.get('grid_power', 0)}W")
                return data
            return None
            
        except Exception as e:
            logger.error(f"Failed to read from Solax: {e}")
            return None
    
    async def read_sdm630_modbus(self, config: Dict) -> Optional[Dict]:
        """Lese Daten von SDM630 via Modbus"""
        try:
            from core.controllers.sdm630 import SDM630ModbusController
            
            if 'sdm630_controller' not in self.controllers:
                self.controllers['sdm630_controller'] = SDM630ModbusController(
                    host=config['ip'],
                    port=config.get('port', 502),
                    unit_id=config.get('unit_id', 1)
                )
            
            controller = self.controllers['sdm630_controller']
            data = await controller.read_power()
            
            if data:
                logger.debug(f"SDM630: {data.get('total_power', 0)}W")
                return data
            return None
            
        except Exception as e:
            logger.error(f"Failed to read from SDM630: {e}")
            return None
    
    async def update_all_sources(self):
        """Aktualisiere alle Datenquellen"""
        
        pv_values = []
        grid_values = []
        battery_data = None
        
        logger.info("Updating all energy sources...")
        
        for source in self.sources.values():
            if not source.enabled:
                logger.debug(f"Skipping disabled source: {source.id}")
                continue
            
            try:
                value = None
                
                # Home Assistant
                if source.provider == SourceProvider.HOME_ASSISTANT:
                    value = await self.read_home_assistant(source.config)
                
                # Shelly 3EM (Gen1)
                elif source.provider == SourceProvider.SHELLY_3EM:
                    data = await self.read_shelly_3em(source.config)
                    if data:
                        value = data['total_power']
                
                # Shelly
                elif source.provider == SourceProvider.SHELLY:
                    value = await self.read_shelly(source.config)
                
                # Shelly Pro 3EM
                elif source.provider == SourceProvider.SHELLY_PRO_3EM:
                    data = await self.read_shelly_pro_3em(source.config)
                    if data:
                        value = data['total_power']
                
                # Solax Modbus
                elif source.provider == SourceProvider.SOLAX_MODBUS:
                    data = await self.read_solax_modbus(source.config)
                    if data:
                        if source.type == SourceType.PV_GENERATION:
                            value = data.get('pv_power', 0)
                        elif source.type == SourceType.GRID_POWER:
                            value = data.get('grid_power', 0)
                        elif source.type == SourceType.BATTERY:
                            battery_data = {
                                'power': data.get('battery_power', 0),
                                'soc': data.get('battery_soc', 0)
                            }
                
                # SDM630 Modbus
                elif source.provider == SourceProvider.SDM630_MODBUS:
                    data = await self.read_sdm630_modbus(source.config)
                    if data:
                        value = data.get('total_power', 0)
                
                # Wert speichern
                if value is not None:
                    source.last_value = value
                    logger.info(f"✓ {source.name}: {value}W")
                    
                    # Nach Typ sammeln
                    if source.type == SourceType.PV_GENERATION:
                        pv_values.append(value)
                    elif source.type == SourceType.GRID_POWER:
                        grid_values.append(value)
                else:
                    logger.warning(f"✗ {source.name}: No data received")
                        
            except Exception as e:
                logger.error(f"Failed to update source {source.id}: {e}")
        
        # Mittelwerte berechnen
        self.current_data['pv_power'] = sum(pv_values) / len(pv_values) if pv_values else 0
        self.current_data['grid_power'] = sum(grid_values) / len(grid_values) if grid_values else 0
        
        if battery_data:
            self.current_data['battery_power'] = battery_data['power']
            self.current_data['battery_soc'] = battery_data['soc']
        
        # Hausverbrauch berechnen
        self.current_data['house_consumption'] = (
            self.current_data['pv_power'] +
            self.current_data['grid_power'] +
            self.current_data['battery_power']
        )
        
        # Verfügbare Leistung
        if self.current_data['grid_power'] < 0:
            self.current_data['available_power'] = abs(self.current_data['grid_power'])
        else:
            self.current_data['available_power'] = 0
        
        logger.info(
            f"==> PV={self.current_data['pv_power']:.0f}W, "
            f"Grid={self.current_data['grid_power']:.0f}W, "
            f"House={self.current_data['house_consumption']:.0f}W, "
            f"Available={self.current_data['available_power']:.0f}W"
        )
    
    def get_current_data(self) -> Dict:
        """Hole aktuelle Energie-Daten"""
        return self.current_data.copy()
    
    def get_source(self, source_id: str) -> Optional[EnergySource]:
        """Hole Datenquelle"""
        return self.sources.get(source_id)
    
    def get_sources_by_type(self, source_type: SourceType) -> List[EnergySource]:
        """Hole alle Quellen eines Typs"""
        return [s for s in self.sources.values() if s.type == source_type]

