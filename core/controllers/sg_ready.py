#!/usr/bin/env python3
"""
EMS-Core v2.0 - SG-Ready Controller
Steuerung von SG-Ready Waermepumpen ueber 2 Relais
"""
import asyncio
import logging
from typing import Optional
from enum import Enum

logger = logging.getLogger(__name__)


class SGReadyMode(Enum):
    """SG-Ready Betriebsmodi"""
    OFF = "off"                    # Beide Relais AUS (EVU-Sperre)
    NORMAL = "normal"              # Relay1=AUS, Relay2=AUS (Normalbetrieb)
    RECOMMENDED = "recommended"    # Relay1=EIN, Relay2=AUS (Empfohlener Betrieb)
    FORCED = "forced"              # Relay1=EIN, Relay2=EIN (Forcierter Betrieb)


class SGReadyController:
    """
    Controller fuer SG-Ready Waermepumpen
    
    SG-Ready nutzt 2 Eingaenge (gesteuert durch 2 Relais):
    - Eingang 1 (Relay1): Einschaltsignal
    - Eingang 2 (Relay2): Zwangseinschaltung
    
    Modi:
    - OFF:         E1=0, E2=0 (EVU-Sperre, WP aus)
    - NORMAL:      E1=0, E2=0 (Normalbetrieb nach eigenem Regelverhalten)
    - RECOMMENDED: E1=1, E2=0 (Empfohlener Betrieb, z.B. bei PV-Ueberschuss)
    - FORCED:      E1=1, E2=1 (Zwangseinschaltung, WP laeuft definitiv)
    """
    
    def __init__(self, relay1_controller, relay2_controller):
        """
        Args:
            relay1_controller: Controller fuer Relais 1 (Einschaltsignal)
            relay2_controller: Controller fuer Relais 2 (Zwangseinschaltung)
        """
        self.relay1 = relay1_controller
        self.relay2 = relay2_controller
        self.current_mode = SGReadyMode.NORMAL
    
    async def set_mode(self, mode: SGReadyMode) -> bool:
        """Setze SG-Ready Modus"""
        try:
            logger.info(f"Setting SG-Ready mode to: {mode.value}")
            
            if mode == SGReadyMode.OFF:
                # EVU-Sperre: Beide AUS
                success1 = await self.relay1.turn_off()
                success2 = await self.relay2.turn_off()
                
            elif mode == SGReadyMode.NORMAL:
                # Normalbetrieb: Beide AUS
                success1 = await self.relay1.turn_off()
                success2 = await self.relay2.turn_off()
                
            elif mode == SGReadyMode.RECOMMENDED:
                # Empfohlener Betrieb: Relay1 EIN, Relay2 AUS
                success1 = await self.relay1.turn_on()
                success2 = await self.relay2.turn_off()
                
            elif mode == SGReadyMode.FORCED:
                # Zwangsbetrieb: Beide EIN
                success1 = await self.relay1.turn_on()
                success2 = await self.relay2.turn_on()
            
            else:
                logger.error(f"Unknown SG-Ready mode: {mode}")
                return False
            
            if success1 and success2:
                self.current_mode = mode
                logger.info(f"✓ SG-Ready mode set to: {mode.value}")
                return True
            else:
                logger.error(f"✗ Failed to set SG-Ready mode to: {mode.value}")
                return False
                
        except Exception as e:
            logger.error(f"✗ SG-Ready set_mode failed: {e}")
            return False
    
    async def get_current_mode(self) -> SGReadyMode:
        """Hole aktuellen Modus (liest Relay-Status)"""
        try:
            status1 = await self.relay1.get_status()
            status2 = await self.relay2.get_status()
            
            if not status1 or not status2:
                logger.warning("Could not read relay status, returning cached mode")
                return self.current_mode
            
            relay1_on = status1.get('state') == 'on'
            relay2_on = status2.get('state') == 'on'
            
            # Dekodiere Modus basierend auf Relay-Zustaenden
            if not relay1_on and not relay2_on:
                return SGReadyMode.NORMAL  # oder OFF - sind identisch
            elif relay1_on and not relay2_on:
                return SGReadyMode.RECOMMENDED
            elif relay1_on and relay2_on:
                return SGReadyMode.FORCED
            else:
                # relay1_off und relay2_on - sollte nicht vorkommen
                logger.warning("Invalid SG-Ready state detected")
                return self.current_mode
                
        except Exception as e:
            logger.error(f"✗ SG-Ready get_current_mode failed: {e}")
            return self.current_mode
    
    async def enable_pv_mode(self) -> bool:
        """Aktiviere PV-Ueberschuss-Modus (RECOMMENDED)"""
        return await self.set_mode(SGReadyMode.RECOMMENDED)
    
    async def disable_pv_mode(self) -> bool:
        """Deaktiviere PV-Ueberschuss-Modus (zurueck zu NORMAL)"""
        return await self.set_mode(SGReadyMode.NORMAL)
    
    async def force_on(self) -> bool:
        """Erzwinge Betrieb (FORCED)"""
        return await self.set_mode(SGReadyMode.FORCED)
    
    async def evu_lock(self) -> bool:
        """Aktiviere EVU-Sperre (OFF)"""
        return await self.set_mode(SGReadyMode.OFF)
    
    async def test_connection(self) -> bool:
        """Test ob beide Relais erreichbar sind"""
        try:
            test1 = await self.relay1.test_connection()
            test2 = await self.relay2.test_connection()
            return test1 and test2
            
        except Exception as e:
            logger.error(f"✗ SG-Ready connection test failed: {e}")
            return False


# Synchrone Wrapper fuer Flask
def set_mode_sync(relay1_controller, relay2_controller, mode: str) -> bool:
    """Synchrone Version von set_mode"""
    sg = SGReadyController(relay1_controller, relay2_controller)
    mode_enum = SGReadyMode(mode)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(sg.set_mode(mode_enum))
    loop.close()
    return result
