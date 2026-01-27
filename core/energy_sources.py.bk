#!/usr/bin/env python3
"""
EMS-Core v2.0 - Energy Sources Manager
Verwaltet verschiedene Energie-Datenquellen (PV, Grid, etc.)
"""
import asyncio
import json
import logging
from typing import Dict, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from datetime import datetime

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
    
    def __init__(self, config_file: str = "config/energy_sources.json"):
        self.config_file = Path(config_file)
        self.sources: Dict[str, EnergySource] = {}
        self.controllers = {}
        
        self.current_data = {
            'pv_power': 0.0,
            'grid_power': 0.0,
            'battery_power': 0.0,
            'battery_soc': 0.0,
            'house_consumption': 0.0,
            'available_power': 0.0
        }
        
        self.load_sources()
    
    def load_sources(self):
        """Lade Quellen aus JSON"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                
                for source_data in data.get('sources', []):
                    source = EnergySource(
                        id=source_data['id'],
                        name=source_data['name'],
                        type=SourceType(source_data['type']),
                        provider=SourceProvider(source_data['provider']),
                        config=source_data['config'],
                        enabled=source_data.get('enabled', True),
                        last_value=source_data.get('last_value', 0.0),
                        last_update=source_data.get('last_update')
                    )
                    self.sources[source.id] = source
                
                logger.info(f"Loaded {len(self.sources)} energy sources")
            else:
                logger.info("No energy sources config found, starting fresh")
        except Exception as e:
            logger.error(f"Failed to load energy sources: {e}")
    
    def save_sources(self):
        """Speichere Quellen als JSON"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            sources_list = []
            for source in self.sources.values():
                source_dict = {
                    'id': source.id,
                    'name': source.name,
                    'type': source.type.value,
                    'provider': source.provider.value,
                    'config': source.config,
                    'enabled': source.enabled,
                    'last_value': source.last_value,
                    'last_update': source.last_update
                }
                sources_list.append(source_dict)
            
            data = {'sources': sources_list}
            
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Saved {len(self.sources)} energy sources")
        except Exception as e:
            logger.error(f"Failed to save energy sources: {e}")
    
    def add_source(self, source: EnergySource):
        """Füge Datenquelle hinzu"""
        self.sources[source.id] = source
        self.save_sources()
        logger.info(f"Added energy source: {source.name} ({source.type.value} via {source.provider.value})")
    
    def remove_source(self, source_id: str):
        """Entferne Datenquelle"""
        if source_id in self.sources:
            del self.sources[source_id]
            self.save_sources()
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
                        logger.info(f"✓ HA {config['entity_id']}: {value}W")
                        return value
                    else:
                        logger.error(f"HA API error {response.status}: {config['entity_id']}")
                        return None
        except Exception as e:
            logger.error(f"Failed to read from Home Assistant: {e}")
            return None
    
    async def read_shelly_3em(self, config: Dict) -> Optional[Dict]:
        """Lese Wert von Shelly 3EM (Gen1)"""
        try:
            import aiohttp
            
            ip = config.get('ip')
            if not ip:
                logger.error("Shelly 3EM: No IP in config!")
                return None
            
            url = f"http://{ip}/status"
            logger.info(f"Reading Shelly 3EM from {url}...")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if 'emeters' in data and 'total_power' in data:
                            emeters = data['emeters']
                            result = {
                                'total_power': data.get('total_power', 0),
                                'phase_a': emeters[0].get('power', 0) if len(emeters) > 0 else 0,
                                'phase_b': emeters[1].get('power', 0) if len(emeters) > 1 else 0,
                                'phase_c': emeters[2].get('power', 0) if len(emeters) > 2 else 0
                            }
                            
                            logger.info(f"✓ Shelly 3EM: {result['total_power']}W (A:{result['phase_a']}W, B:{result['phase_b']}W, C:{result['phase_c']}W)")
                            return result
                        else:
                            logger.error(f"Shelly 3EM: Unexpected format")
                            return None
                    else:
                        logger.error(f"Shelly 3EM HTTP error: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Failed to read from Shelly 3EM: {e}")
            return None
    
    async def update_all_sources(self):
        """Aktualisiere alle Datenquellen"""
        
        pv_values = []
        grid_values = []
        battery_data = None
        
        logger.info(f"Updating {len(self.sources)} energy sources...")
        
        for source in self.sources.values():
            if not source.enabled:
                logger.debug(f"Skipping disabled: {source.id}")
                continue
            
            try:
                value = None
                
                # Home Assistant
                if source.provider == SourceProvider.HOME_ASSISTANT:
                    value = await self.read_home_assistant(source.config)
                
                # Shelly 3EM
                elif source.provider == SourceProvider.SHELLY_3EM:
                    data = await self.read_shelly_3em(source.config)
                    if data:
                        value = data['total_power']
                
                # Wert speichern
                if value is not None:
                    source.last_value = value
                    source.last_update = datetime.now().isoformat()
                    
                    if source.type == SourceType.PV_GENERATION:
                        pv_values.append(value)
                    elif source.type == SourceType.GRID_POWER:
                        grid_values.append(value)
                else:
                    logger.warning(f"✗ {source.name}: No data")
                        
            except Exception as e:
                logger.error(f"Source {source.id} error: {e}")
        
        # Berechne Werte
        self.current_data['pv_power'] = sum(pv_values) / len(pv_values) if pv_values else 0
        self.current_data['grid_power'] = sum(grid_values) / len(grid_values) if grid_values else 0
        
        if battery_data:
            self.current_data['battery_power'] = battery_data['power']
            self.current_data['battery_soc'] = battery_data['soc']
        
        self.current_data['house_consumption'] = (
            self.current_data['pv_power'] +
            self.current_data['grid_power'] +
            self.current_data['battery_power']
        )
        
        if self.current_data['grid_power'] < 0:
            self.current_data['available_power'] = abs(self.current_data['grid_power'])
        else:
            self.current_data['available_power'] = 0
        
        # Speichere aktualisierte Werte
        self.save_sources()
        
        logger.info(
            f"==> PV={self.current_data['pv_power']:.0f}W, "
            f"Grid={self.current_data['grid_power']:.0f}W, "
            f"House={self.current_data['house_consumption']:.0f}W"
        )
    
    def get_current_data(self) -> Dict:
        """Hole aktuelle Energie-Daten"""
        return self.current_data.copy()
    
    def get_source(self, source_id: str) -> Optional[EnergySource]:
        """Hole Datenquelle"""
        return self.sources.get(source_id)
