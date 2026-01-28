#!/usr/bin/env python3
"""
EMS-Core v2.0 - Main Optimizer Loop (Final Version)
Mit: PV-Optimierung + Scheduler + Manual Override
"""
import asyncio
import logging
from typing import List, Dict, Optional
from datetime import datetime

from core.device_manager import DeviceManager, DeviceConfig
from core.energy_sources import EnergySourcesManager
from core.controllers.shelly import ShellyController
from core.optimizer.scheduler import Scheduler
from core.optimizer.schedule_manager import ScheduleManager
from core.device_override import OverrideManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EMSOptimizer:
    """
    Energy Management System Optimizer (Final)
    
    Entscheidungs-Hierarchie:
    1. Manual Override (höchste Priorität)
    2. Schedule (force_off/force_on)
    3. PV-Optimierung (normale Logik)
    """
    
    def __init__(self, 
                 device_manager: DeviceManager,
                 energy_manager: EnergySourcesManager,
                 schedule_manager: Optional[ScheduleManager] = None,
                 override_manager: Optional[OverrideManager] = None,
                 cycle_interval: int = 30):
        """
        Args:
            device_manager: Verwaltet alle steuerbaren Devices
            energy_manager: Liefert Energie-Daten
            schedule_manager: Optional - Verwaltet Zeitpläne
            override_manager: Optional - Verwaltet manuelle Overrides
            cycle_interval: Sekunden zwischen Optimierungs-Zyklen
        """
        self.device_manager = device_manager
        self.energy_manager = energy_manager
        self.cycle_interval = cycle_interval
        
        # Scheduler (optional)
        self.schedule_manager = schedule_manager
        if self.schedule_manager:
            self.scheduler = Scheduler(self.schedule_manager)
            logger.info("✅ Scheduler enabled")
        else:
            self.scheduler = None
            logger.info("ℹ️ Scheduler disabled")
        
        # Override Manager (optional)
        self.override_manager = override_manager
        if self.override_manager:
            logger.info("✅ Manual Override enabled")
        else:
            logger.info("ℹ️ Manual Override disabled")
        
        self.running = False
        self.current_state = {}
        
        # Strategien
        self.min_surplus_threshold = 200
        self.hysteresis = 100
        
        logger.info("EMS Optimizer initialized (Final Version)")
    
    async def run(self):
        """Hauptschleife"""
        self.running = True
        logger.info("🚀 EMS Optimizer started")
        
        cycle_count = 0
        
        while self.running:
            try:
                cycle_count += 1
                logger.info(f"{'='*60}")
                logger.info(f"🔄 Optimization Cycle #{cycle_count}")
                logger.info(f"{'='*60}")
                
                # 1. Cleanup abgelaufene Overrides (alle 10 Zyklen)
                if self.override_manager and cycle_count % 10 == 0:
                    self.override_manager.cleanup_expired()
                
                # 2. Update Energy Data
                await self.update_energy_data()
                
                # 3. Get Current Energy Situation
                energy_data = self.energy_manager.get_current_data()
                
                # 4. Update Scheduler with current energy data
                if self.scheduler:
                    self.scheduler.update_energy_data(energy_data)
                
                # 5. Calculate Available Power
                available_power = self.calculate_available_power(energy_data)
                
                # 6. Make Control Decisions (mit Override + Scheduler)
                decisions = await self.make_control_decisions(energy_data, available_power)
                
                # 7. Execute Control Commands
                await self.execute_decisions(decisions)
                
                # 8. Log Summary
                self.log_cycle_summary(energy_data, available_power, decisions)
                
                # 9. Wait for next cycle
                logger.info(f"⏳ Waiting {self.cycle_interval}s for next cycle...")
                await asyncio.sleep(self.cycle_interval)
                
            except KeyboardInterrupt:
                logger.info("⚠️ Received interrupt signal")
                break
            except Exception as e:
                logger.error(f"❌ Error in optimization cycle: {e}", exc_info=True)
                await asyncio.sleep(5)
        
        logger.info("🛑 EMS Optimizer stopped")
    
    async def update_energy_data(self):
        """Update alle Energy Sources"""
        logger.info("📊 Updating energy data...")
        await self.energy_manager.update_all_sources()
    
    def calculate_available_power(self, energy_data: Dict) -> float:
        """Berechne verfuegbare Power fuer optionale Devices"""
        pv_power = energy_data.get('pv_power', 0)
        grid_power = energy_data.get('grid_power', 0)
        battery_power = energy_data.get('battery_power', 0)
        battery_soc = energy_data.get('battery_soc', 0)
        
        if grid_power < 0:
            available = abs(grid_power) - self.hysteresis
        else:
            available = 0
        
        if battery_soc > 90:
            available += 200
        elif battery_soc < 20:
            available = max(0, available - 300)
        
        logger.info(f"💡 Available Power: {available:.0f}W (Grid: {grid_power:.0f}W, Battery SOC: {battery_soc:.0f}%)")
        
        return max(0, available)
    
    async def make_control_decisions(self, energy_data: Dict, available_power: float) -> List[Dict]:
        """
        Entscheide welche Devices ein/aus
        
        Hierarchie:
        1. Manual Override (überschreibt ALLES)
        2. Schedule (force_off/force_on)
        3. PV-Optimierung
        """
        decisions = []
        
        devices = self.device_manager.get_all_devices()
        controllable_devices = [d for d in devices if d.can_control and d.enabled]
        
        priority_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3, 'OPTIONAL': 4}
        controllable_devices.sort(key=lambda d: priority_order.get(d.priority, 99))
        
        remaining_power = available_power
        
        for device in controllable_devices:
            decision = await self.decide_device_action(device, remaining_power, energy_data)
            
            if decision:
                decisions.append(decision)
                
                if decision['action'] == 'on':
                    estimated_power = device.power or 500
                    remaining_power -= estimated_power
        
        return decisions
    
    async def decide_device_action(self, 
                                   device: DeviceConfig, 
                                   remaining_power: float,
                                   energy_data: Dict) -> Optional[Dict]:
        """
        Entscheide Aktion fuer ein einzelnes Device
        
        Priorität:
        1. Manual Override
        2. Schedule
        3. PV-Optimierung
        """
        device_id = device.id
        priority = device.priority
        estimated_power = device.power or 500
        
        # === 1. MANUAL OVERRIDE (höchste Priorität) ===
        if self.override_manager:
            override_decision = self.override_manager.check_override_decision(device_id)
            
            if override_decision:
                # Override aktiv - überschreibt ALLES
                current_state = await self.get_device_current_state(device)
                
                if override_decision['action'] == 'force_on':
                    if current_state != 'on':
                        return {
                            'device_id': device_id,
                            'device_name': device.name,
                            'action': 'on',
                            'reason': f"👤 {override_decision['reason']}",
                            'priority': priority,
                            'manual_override': True
                        }
                    return None  # Bereits an
                
                elif override_decision['action'] == 'force_off':
                    if current_state == 'on':
                        return {
                            'device_id': device_id,
                            'device_name': device.name,
                            'action': 'off',
                            'reason': f"👤 {override_decision['reason']}",
                            'priority': priority,
                            'manual_override': True
                        }
                    return None  # Bereits aus
        
        # === 2. SCHEDULE (zweithöchste Priorität) ===
        if self.scheduler:
            schedule_decision = self.scheduler.check_device_schedule(device_id)
            
            if schedule_decision['action'] == 'force_off':
                current_state = await self.get_device_current_state(device)
                if current_state == 'on':
                    return {
                        'device_id': device_id,
                        'device_name': device.name,
                        'action': 'off',
                        'reason': f"🕐 Schedule: {schedule_decision['reason']}",
                        'priority': priority,
                        'schedule_override': True
                    }
                return None
            
            if schedule_decision['action'] == 'force_on':
                current_state = await self.get_device_current_state(device)
                if current_state != 'on':
                    return {
                        'device_id': device_id,
                        'device_name': device.name,
                        'action': 'on',
                        'reason': f"🕐 Schedule: {schedule_decision['reason']}",
                        'priority': priority,
                        'schedule_override': True
                    }
                return None
            
            # Priority Override durch Schedule?
            if schedule_decision.get('override_priority') and schedule_decision.get('priority'):
                priority = schedule_decision['priority']
        
        # === 3. PV-OPTIMIERUNG (normale Logik) ===
        current_state = await self.get_device_current_state(device)
        
        if priority == 'CRITICAL':
            if current_state != 'on':
                return {
                    'device_id': device_id,
                    'device_name': device.name,
                    'action': 'on',
                    'reason': 'CRITICAL priority - always on',
                    'priority': priority
                }
        
        elif priority == 'HIGH':
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
        
        return None
    
    async def get_device_current_state(self, device: DeviceConfig) -> Optional[str]:
        """Hole aktuellen Zustand eines Devices"""
        try:
            if 'shelly' in device.type:
                ip = device.ip
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
            manual_override = decision.get('manual_override', False)
            schedule_override = decision.get('schedule_override', False)
            
            try:
                device = self.device_manager.get_device(device_id)
                if not device:
                    logger.error(f"❌ Device {device_id} not found")
                    continue
                
                if 'shelly' in device.type:
                    ip = device.ip
                    if ip:
                        controller = ShellyController(ip, device.type)
                        
                        if action == 'on':
                            success = await controller.turn_on()
                        elif action == 'off':
                            success = await controller.turn_off()
                        else:
                            success = False
                        
                        # Marker für Override
                        marker = ""
                        if manual_override:
                            marker = "👤 "
                        elif schedule_override:
                            marker = "🕐 "
                        
                        if success:
                            logger.info(f"✅ {marker}{device_name} ({device_id}) -> {action.upper()} | Reason: {reason}")
                        else:
                            logger.error(f"❌ {device_name} ({device_id}) -> {action.upper()} FAILED")
                
            except Exception as e:
                logger.error(f"❌ Failed to control {device_name} ({device_id}): {e}")
    
    def log_cycle_summary(self, energy_data: Dict, available_power: float, decisions: List[Dict]):
        """Log Zusammenfassung"""
        logger.info("")
        logger.info("📋 Cycle Summary:")
        logger.info(f"   PV: {energy_data['pv_power']:.0f}W | Grid: {energy_data['grid_power']:.0f}W | Battery: {energy_data['battery_power']:.0f}W ({energy_data['battery_soc']:.0f}%)")
        logger.info(f"   House: {energy_data['house_consumption']:.0f}W | Available: {available_power:.0f}W")
        logger.info(f"   Control Actions: {len(decisions)}")
        
        if self.scheduler:
            active_schedules = len(self.schedule_manager.get_enabled_schedules())
            logger.info(f"   Active Schedules: {active_schedules}")
        
        if self.override_manager:
            override_stats = self.override_manager.get_statistics()
            active_overrides = override_stats['total_overrides']
            logger.info(f"   Active Overrides: {active_overrides} (ON: {override_stats['manual_on']}, OFF: {override_stats['manual_off']})")
        
        logger.info("")
    
    def stop(self):
        """Stoppe den Optimizer"""
        logger.info("🛑 Stopping optimizer...")
        self.running = False


async def main():
    """Main Entry Point"""
    logger.info("="*60)
    logger.info("🚀 EMS-Core v2.0 - Energy Management System (Final)")
    logger.info("="*60)
    
    # Initialize Components
    device_manager = DeviceManager()
    energy_manager = EnergySourcesManager()
    
    # Initialize Scheduler (optional)
    try:
        schedule_manager = ScheduleManager()
        logger.info(f"✅ Loaded {len(schedule_manager.schedules)} schedules")
    except Exception as e:
        logger.warning(f"⚠️ Failed to load schedules: {e}")
        schedule_manager = None
    
    # Initialize Override Manager (optional)
    try:
        override_manager = OverrideManager()
        logger.info(f"✅ Loaded {len(override_manager.overrides)} overrides")
    except Exception as e:
        logger.warning(f"⚠️ Failed to load overrides: {e}")
        override_manager = None
    
    logger.info(f"✅ Loaded {len(device_manager.devices)} devices")
    logger.info(f"✅ Loaded {len(energy_manager.sources)} energy sources")
    
    # Create Optimizer
    optimizer = EMSOptimizer(
        device_manager=device_manager,
        energy_manager=energy_manager,
        schedule_manager=schedule_manager,
        override_manager=override_manager,
        cycle_interval=30
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
