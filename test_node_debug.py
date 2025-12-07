#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import json
from datetime import datetime
from app.schemas import OrchestrationState, InputMessage
from app.graph import NionGraph

# Create a test state
input_msg = InputMessage(
    message="Test message for demo",
    sender="Test User",
    project_id="PRJ-ALPHA",
    timestamp=datetime.now()
)

state = OrchestrationState(
    input_message=input_msg,
    state_id="test-id"
)

# Create graph instance
try:
    graph = NionGraph()
    print("Graph initialized successfully")
    
    # Test the L1 node directly
    print("\nCalling _node_l1_orchestrator...")
    result = graph._node_l1_orchestrator(state)
    
    print(f"Result type: {type(result)}")
    print(f"Result is dict: {isinstance(result, dict)}")
    print(f"Result keys: {result.keys() if isinstance(result, dict) else 'N/A'}")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
