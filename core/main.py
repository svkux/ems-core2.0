#!/usr/bin/env python3
"""
EMS-Core v2.0 - Main Optimizer
Hauptsteuerung des Energie-Management-Systems
"""
import asyncio
import logging
import signal
from pathlib import Path
from typing import Dict, Optional

import yaml

from core.optimizer.scheduler import Scheduler
from core.optimizer.prioritizer import Prioritizer, Device, Priority

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EMSCore:
    """Haupt-Energie-Management-System"""
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        self.config_path = Path(config_path)
        self.config = self.load_config()
        self.running = False
        
        self.scheduler = Scheduler("config/schedules.json")
        self.prioritizer = Prioritizer()
        
        self.controllers = {}
        
        self.energy_data = {
            'pv_power': 0.0,
            'battery_power': 0.0,
            'battery_soc': 0.0,
            'grid_power': 0.0,
            'available_power': 0.0
        }
        
    def load_config(self) -> Dict:
        """Lade Konfiguration"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    return yaml.safe_load(f)
            else:
                logger.warning("Config not found, using defaults")
                return self.get_default_config()
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict:
        """Standard-Konfiguration"""
        return {
            'optimization_interval': 30,
            'hysteresis': 100,
            'battery': {
                'min_soc': 20,
                'max_soc': 95,
                'priority_soc': 50
            }
        }
    
    async def initialize(self):
        """Initialisiere System"""
        logger.info("Initializing EMS-Core v2.0...")
        await self.load_devices()
        logger.info("EMS-Core initialized")
    
    async def load_devices(self):
        """Lade Geräte"""
        devices_path = Path("config/devices.yaml")
        try:
            if devices_path.exists():
                with open(devices_path, 'r') as f:
                    devices_config = yaml.safe_load(f)
                
                for device_cfg in devices_config.get('devices', []):
                    device = Device(
                        id=device_cfg['id'],
                        name=device_cfg['name'],
                        power=device_cfg.get('power', 0),
                        priority=Priority[device_cfg.get('priority', 'MEDIUM')],
                        can_control=device_cfg.get('can_control', True),
                        min_runtime=device_cfg.get('min_runtime', 0)
                    )
                    self.prioritizer.add_device(device)
                
                logger.info(f"Loaded {len(devices_config.get('devices', []))} devices")
        except Exception as e:
            logger.error(f"Failed to load devices: {e}")
    
    async def optimize(self):
        """Führe Optimierung durch"""
        try:
            # Update scheduled status
            for device_id in self.prioritizer.devices:
                is_scheduled = self.scheduler.is_in_schedule(device_id)
                self.prioritizer.devices[device_id].scheduled = is_scheduled
            
            # Calculate plan
            plan = self.prioritizer.calculate_switching_plan(
                available_power=self.energy_data['available_power']
            )
            
            logger.info(f"Optimization: {sum(plan.values())}/{len(plan)} devices ON")
            
        except Exception as e:
            logger.error(f"Optimization failed: {e}")
    
    async def run(self):
        """Hauptschleife"""
        self.running = True
        interval = self.config['optimization_interval']
        
        logger.info(f"Starting optimization loop (interval: {interval}s)")
        
        while self.running:
            try:
                await self.optimize()
                await asyncio.sleep(interval)
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(interval)
    
    async def shutdown(self):
        """Beende System"""
        logger.info("Shutting down EMS-Core...")
        self.running = False


async def main():
    """Haupt-Funktion"""
    ems = EMSCore()
    
    def signal_handler(sig, frame):
        logger.info(f"Received signal {sig}")
        asyncio.create_task(ems.shutdown())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await ems.initialize()
        await ems.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        await ems.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
