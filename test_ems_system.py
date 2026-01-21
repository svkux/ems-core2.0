#!/usr/bin/env python3
"""
EMS-Core v2.0 - System Test
"""
import logging
from datetime import datetime

from core.optimizer.scheduler import Scheduler
from core.optimizer.prioritizer import Prioritizer, Device, Priority

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_scheduler():
    """Test Scheduler"""
    scheduler = Scheduler("config/schedules.json")
    
    schedule = {
        "monday": [[10, 14]]
    }
    scheduler.add_schedule("test_device", schedule)
    
    # Test Montag 12:00
    test_time = datetime(2025, 1, 20, 12, 0)
    result = scheduler.is_in_schedule("test_device", test_time)
    
    logger.info(f"✓ Scheduler Test: {result}")
    return result


def test_prioritizer():
    """Test Prioritizer"""
    prioritizer = Prioritizer()
    
    devices = [
        Device("critical", "Critical", 150, Priority.CRITICAL),
        Device("high", "High", 2000, Priority.HIGH),
        Device("low", "Low", 2000, Priority.LOW),
    ]
    
    for device in devices:
        prioritizer.add_device(device)
    
    plan = prioritizer.calculate_switching_plan(5000)
    
    logger.info(f"✓ Prioritizer Test: {sum(plan.values())}/{len(plan)} devices ON")
    return len(plan) == 3


if __name__ == "__main__":
    logger.info("="*70)
    logger.info("EMS-Core v2.0 - Quick Test")
    logger.info("="*70)
    
    test1 = test_scheduler()
    test2 = test_prioritizer()
    
    if test1 and test2:
        logger.info("\n✓ ALL TESTS PASSED!")
    else:
        logger.warning("\n✗ SOME TESTS FAILED!")
