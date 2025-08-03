#!/usr/bin/env python3
"""
Test script for the enhanced scheduler
Run this to verify the scheduler is working properly
"""

import time
import json
from scheduler import background_scheduler

def test_scheduler():
    print("🧪 Testing Enhanced Scheduler")
    print("=" * 50)
    
    # Test 1: Initial status
    print("1. Initial Status:")
    status = background_scheduler.get_status()
    print(json.dumps(status, indent=2))
    print()
    
    # Test 2: Start scheduler
    print("2. Starting Scheduler...")
    background_scheduler.start()
    time.sleep(2)  # Give it time to initialize
    
    status = background_scheduler.get_status()
    print(f"   Running: {status['running']}")
    print(f"   Jobs: {status['jobs_count']}")
    print(f"   Next sync: {status['next_sync_time']}")
    print()
    
    # Test 3: Wait a bit to see heartbeat
    print("3. Waiting 30 seconds to observe scheduler activity...")
    print("   (Check console output for heartbeat messages)")
    time.sleep(30)
    
    # Test 4: Final status
    print("4. Final Status:")
    status = background_scheduler.get_status()
    print(json.dumps(status, indent=2))
    
    # Test 5: Stop scheduler
    print("\n5. Stopping Scheduler...")
    background_scheduler.stop()
    
    print("\n✅ Scheduler test completed!")
    print("\nKey things to verify:")
    print("  - Scheduler shows running=true when started")
    print("  - Jobs count shows 3 (5min sync, hourly sync, heartbeat)")
    print("  - Next sync time is populated")
    print("  - Heartbeat messages appear every 10 minutes")
    print("  - Sync attempts are logged every 5 minutes")

if __name__ == "__main__":
    test_scheduler()
