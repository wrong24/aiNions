#!/usr/bin/env python3
"""
Nion Orchestration Engine - Local Test Script
Tests the engine without running FastAPI server
"""

import sys
import os
import json
import logging
from datetime import datetime

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from schemas import InputMessage
from graph import NionGraph
from formatter import NionFormatter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Test Case 1: Customer demo feedback with feature request"""

    logger.info("=" * 90)
    logger.info("NION ORCHESTRATION ENGINE - LOCAL TEST")
    logger.info("=" * 90)

    # Test message
    test_input = {
        "message": "The customer demo went great! They loved it but asked if we could add real-time notifications. They're willing to pay 20% more.",
        "sender": "Sarah Chen",
        "project_id": "PRJ-ALPHA",
        "message_id": "MSG-20241206-001"
    }

    logger.info(f"\nInput Message:")
    logger.info(json.dumps(test_input, indent=2))

    try:
        # Create input message
        input_message = InputMessage(**test_input)
        logger.info("\n✓ Message validation passed")

        # Initialize graph
        logger.info("\nInitializing NionGraph...")
        graph = NionGraph()
        logger.info("✓ Graph initialized")

        # Invoke orchestration
        logger.info("\nInvoking orchestration...")
        result_state = graph.invoke(input_message)
        logger.info("✓ Orchestration completed")

        # Generate NION MAP
        logger.info("\nGenerating NION ORCHESTRATION MAP...")
        nion_map = NionFormatter.generate_nion_map(result_state)
        print("\n" + nion_map)

        # Generate JSON output
        logger.info("\nGenerating JSON output...")
        json_output = NionFormatter.generate_json_output(result_state)

        # Save to file
        output_file = "orchestration_result.json"
        with open(output_file, 'w') as f:
            json.dump(json_output, f, indent=2, default=str)
        logger.info(f"✓ Output saved to {output_file}")

        logger.info("\n" + "=" * 90)
        logger.info("TEST COMPLETED SUCCESSFULLY")
        logger.info("=" * 90)

    except Exception as e:
        logger.error(f"Error during orchestration: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
