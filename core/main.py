#!/usr/bin/env python3
"""
EMS-Core v2.0 - Main Optimizer Loop
Das Herzstück: Intelligente Energie-Verteilung basierend auf PV, Battery, Grid
"""
import asyncio
import logging
import time
from typing import List, Dict, Optional
from datetime import datetime

from core.device_manager import DeviceManager, DeviceConfig
from core.energy_sources import EnergySourcesManager
from core.controllers.shelly import ShellyController

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EMSOptimizer:
    """
    Energy Management System Optimizer
    
    Hauptaufgaben:
    1. Hole aktuelle Energy-Daten (PV, Grid, Battery)
    2. Berechne verfuegbare Power
    3. Entscheide welche Devices ein/aus basierend auf Prioritaet
    4. Fuehre Schaltbefehle aus
    5. Wiederhole alle X Sekunden
    """
    
    def __init__(self, 
                 device_manager: DeviceManager,
                 energy_manager: EnergySourcesManager,
                 cycle_interval: int = 30):
        """
        Args:
            device_manager: Verwaltet alle steuerbaren Devices
            energy_manager: Liefert Energie-Daten
            cycle_interval: Sekunden zwischen Optimierungs-Zyklen
        """
        self.device_manager = device_manager
        self.energy_manager = energy_manager
        self.cycle_interval = cycle_interval
        
        self.running = False
        self.current_state = {}
        
        # Strategien
        self.min_surplus_threshold = 200  # Minimum W um Devices zuzuschalten
        self.hysteresis = 100  # Hysterese um Flackern zu vermeiden
        
        logger.info("EMS Optimizer initialized")
    
    async def run(self):
        """Hauptschleife - laeuft kontinuierlich"""
        self.running = True
        logger.info("🚀 EMS Optimizer started")
        
        cycle_count = 0
        
        while self.running:
            try:
                cycle_count += 1
                logger.info(f"{'='*60}")
                logger.info(f"🔄 Optimization Cycle #{cycle_count}")
                logger.info(f"{'='*60}")
                
                # 1. Update Energy Data
                await self.update_energy_data()
                
                # 2. Get Current Energy Situation
                energy_data = self.energy_manager.get_current_data()
                
                # 3. Calculate Available Power
                available_power = self.calculate_available_power(energy_data)
                
                # 4. Make Control Decisions
                decisions = await self.make_control_decisions(energy_data, available_power)
                
                # 5. Execute Control Commands
                await self.execute_decisions(decisions)
                
                # 6. Log Summary
                self.log_cycle_summary(energy_data, available_power, decisions)
                
                # 7. Wait for next cycle
                logger.info(f"⏳ Waiting {self.cycle_interval}s for next cycle...")
                await asyncio.sleep(self.cycle_interval)
                
            except KeyboardInterrupt:
                logger.info("⚠️ Received interrupt signal")
                break
            except Exception as e:
                logger.error(f"❌ Error in optimization cycle: {e}", exc_info=True)
                await asyncio.sleep(5)  # Short wait before retry
        
        logger.info("🛑 EMS Optimizer stopped")
    
    async def update_energy_data(self):
        """Update alle Energy Sources"""
        logger.info("📊 Updating energy data...")
        await self.energy_manager.update_all_sources()
    
    def calculate_available_power(self, energy_data: Dict) -> float:
        """
        Berechne verfuegbare Power fuer optionale Devices
        
        Strategie:
        - PV-Ueberschuss = PV - House (wenn Grid negativ)
        - Verfuegbare Power = PV-Ueberschuss - Sicherheitspuffer
        """
        pv_power = energy_data.get('pv_power', 0)
        grid_power = energy_data.get('grid_power', 0)
        battery_power = energy_data.get('battery_power', 0)
        battery_soc = energy_data.get('battery_soc', 0)
        
        # Wenn Einspeisung (Grid negativ), haben wir Ueberschuss
        if grid_power < 0:
            available = abs(grid_power) - self.hysteresis
        else:
            available = 0
        
        # Batterie-SOC beruecksichtigen
        # Wenn Battery voll (>90%), mehr aggressiv optionale Devices zuschalten
        if battery_soc > 90:
            available += 200  # Bonus
        # Wenn Battery leer (<20%), konservativer sein
        elif battery_soc < 20:
            available = max(0, available - 300)  # Penalty
        
        logger.info(f"💡 Available Power: {available:.0f}W (Grid: {grid_power:.0f}W, Battery SOC: {battery_soc:.0f}%)")
        
        return max(0, available)
    
    async def make_control_decisions(self, energy_data: Dict, available_power: float) -> List[Dict]:
        """
        Entscheide welche Devices ein/aus geschaltet werden sollen
        
        Logik:
        1. CRITICAL Devices: Immer AN (ausser EVU-Sperre)
        2. HIGH Devices: AN wenn ausreichend PV/Battery
        3. MEDIUM Devices: AN bei gutem Ueberschuss
        4. LOW/OPTIONAL: Nur bei deutlichem Ueberschuss
        
        Returns:
            List of decisions: [{'device_id': '...', 'action': 'on/off', 'reason': '...'}]
        """
        decisions = []
        
        devices = self.device_manager.get_all_devices()
        controllable_devices = [d for d in devices if d.can_control and d.enabled]
        
        # Sortiere nach Prioritaet
        priority_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3, 'OPTIONAL': 4}
        controllable_devices.sort(key=lambda d: priority_order.get(d.priority, 99))
        
        remaining_power = available_power
        
        for device in controllable_devices:
            decision = await self.decide_device_action(device, remaining_power, energy_data)
            
            if decision:
                decisions.append(decision)
                
                # Subtract estimated power consumption
                if decision['action'] == 'on':
                    estimated_power = device.power_rating or 500  # Default 500W
                    remaining_power -= estimated_power
        
        return decisions
    
    async def decide_device_action(self, 
                                   device: DeviceConfig, 
                                   remaining_power: float,
                                   energy_data: Dict) -> Optional[Dict]:
        """
        Entscheide Aktion fuer ein einzelnes Device
        
        Returns:
            Decision dict oder None wenn keine Aenderung
        """
        device_id = device.id
        priority = device.priority
        estimated_power = device.power_rating or 500
        
        # Hole aktuellen Status (wenn moeglich)
        current_state = await self.get_device_current_state(device)
        
        # Entscheidungslogik basierend auf Prioritaet
        
        if priority == 'CRITICAL':
            # Critical Devices immer AN (ausser explizit deaktiviert)
            if current_state != 'on':
                return {
                    'device_id': device_id,
                    'device_name': device.name,
                    'action': 'on',
                    'reason': 'CRITICAL priority - always on',
                    'priority': priority
                }
        
        elif priority == 'HIGH':
            # High Priority: AN wenn mindestens etwas PV oder Battery
            if energy_data['pv_power'] > 500 or energy_data['battery_soc'] > 30:
                if current_state != 'on':
                    return {
                        'device_id': device_id,
                        'device_name': device.name,
                        'action': 'on',
                        'reason': 'HIGH priority - sufficient energy available',
                        'priority': priority
                    }
            else:
                if current_state == 'on':
                    return {
                        'device_id': device_id,
                        'device_name': device.name,
                        'action': 'off',
                        'reason': 'HIGH priority - insufficient energy',
                        'priority': priority
                    }
        
        elif priority == 'MEDIUM':
            # Medium: AN wenn guter Ueberschuss
            if remaining_power > estimated_power + self.min_surplus_threshold:
                if current_state != 'on':
                    return {
                        'device_id': device_id,
                        'device_name': device.name,
                        'action': 'on',
                        'reason': f'MEDIUM priority - surplus available ({remaining_power:.0f}W)',
                        'priority': priority
                    }
            else:
                if current_state == 'on':
                    return {
                        'device_id': device_id,
                        'device_name': device.name,
                        'action': 'off',
                        'reason': 'MEDIUM priority - insufficient surplus',
                        'priority': priority
                    }
        
        elif priority in ['LOW', 'OPTIONAL']:
            # Low/Optional: Nur bei deutlichem Ueberschuss
            required_surplus = estimated_power + self.min_surplus_threshold + 300
            
            if remaining_power > required_surplus:
                if current_state != 'on':
                    return {
                        'device_id': device_id,
                        'device_name': device.name,
                        'action': 'on',
                        'reason': f'{priority} priority - significant surplus ({remaining_power:.0f}W)',
                        'priority': priority
                    }
            else:
                if current_state == 'on':
                    return {
                        'device_id': device_id,
                        'device_name': device.name,
                        'action': 'off',
                        'reason': f'{priority} priority - insufficient surplus',
                        'priority': priority
                    }
        
        return None  # Keine Aenderung noetig
    
    async def get_device_current_state(self, device: DeviceConfig) -> Optional[str]:
        """Hole aktuellen Zustand eines Devices (on/off/unknown)"""
        try:
            if 'shelly' in device.type:
                ip = device.connection_params.get('ip')
                if ip:
                    controller = ShellyController(ip, device.type)
                    status = await controller.get_status()
                    if status:
                        return status.get('state', 'unknown')
        except Exception as e:
            logger.debug(f"Could not get state for {device.id}: {e}")
        
        return 'unknown'
    
    async def execute_decisions(self, decisions: List[Dict]):
        """Fuehre Control-Entscheidungen aus"""
        if not decisions:
            logger.info("✅ No control actions needed")
            return
        
        logger.info(f"🎯 Executing {len(decisions)} control actions...")
        
        for decision in decisions:
            device_id = decision['device_id']
            action = decision['action']
            reason = decision['reason']
            device_name = decision['device_name']
            
            try:
                device = self.device_manager.get_device(device_id)
                if not device:
                    logger.error(f"❌ Device {device_id} not found")
                    continue
                
                # Execute control command
                if 'shelly' in device.type:
                    ip = device.connection_params.get('ip')
                    if ip:
                        controller = ShellyController(ip, device.type)
                        
                        if action == 'on':
                            success = await controller.turn_on()
                        elif action == 'off':
                            success = await controller.turn_off()
                        else:
                            success = False
                        
                        if success:
                            logger.info(f"✅ {device_name} ({device_id}) -> {action.upper()} | Reason: {reason}")
                        else:
                            logger.error(f"❌ {device_name} ({device_id}) -> {action.upper()} FAILED")
                
            except Exception as e:
                logger.error(f"❌ Failed to control {device_name} ({device_id}): {e}")
    
    def log_cycle_summary(self, energy_data: Dict, available_power: float, decisions: List[Dict]):
        """Log Zusammenfassung des Optimierungs-Zyklus"""
        logger.info("")
        logger.info("📋 Cycle Summary:")
        logger.info(f"   PV: {energy_data['pv_power']:.0f}W | Grid: {energy_data['grid_power']:.0f}W | Battery: {energy_data['battery_power']:.0f}W ({energy_data['battery_soc']:.0f}%)")
        logger.info(f"   House: {energy_data['house_consumption']:.0f}W | Available: {available_power:.0f}W")
        logger.info(f"   Control Actions: {len(decisions)}")
        logger.info("")
    
    def stop(self):
        """Stoppe den Optimizer"""
        logger.info("🛑 Stopping optimizer...")
        self.running = False


async def main():
    """Main Entry Point"""
    logger.info("="*60)
    logger.info("🚀 EMS-Core v2.0 - Energy Management System")
    logger.info("="*60)
    
    # Initialize Components
    device_manager = DeviceManager()
    energy_manager = EnergySourcesManager()
    
    logger.info(f"✅ Loaded {len(device_manager.devices)} devices")
    logger.info(f"✅ Loaded {len(energy_manager.sources)} energy sources")
    
    # Create Optimizer
    optimizer = EMSOptimizer(
        device_manager=device_manager,
        energy_manager=energy_manager,
        cycle_interval=30  # 30 Sekunden zwischen Zyklen
    )
    
    # Run Optimizer Loop
    try:
        await optimizer.run()
    except KeyboardInterrupt:
        logger.info("⚠️ Interrupted by user")
    finally:
        optimizer.stop()
        logger.info("👋 EMS-Core stopped")


if __name__ == '__main__':
    asyncio.run(main())
