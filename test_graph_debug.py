#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import json
from datetime import datetime
from app.schemas import OrchestrationState, InputMessage

# Create a test state
input_msg = InputMessage(
    message="Test message",
    sender="Test User",
    project_id="PRJ-TEST",
    timestamp=datetime.utcnow()
)

state = OrchestrationState(
    input_message=input_msg,
    state_id="test-id"
)

print("Initial state:")
print(f"  Type: {type(state)}")
print(f"  state.plan: {state.plan}")
print(f"  state.logs: {state.logs}")

# Test dict return
result_dict = {
    "plan": [],
    "logs": state.logs + ["[L1] Test log"]
}

print("\nReturned dict:")
print(f"  Type: {type(result_dict)}")
print(f"  Content: {result_dict}")

# Simulate what the graph does
print("\nSimulating graph behavior...")
print(f"Result is dict: {isinstance(result_dict, dict)}")
print(f"Result keys: {result_dict.keys()}")
