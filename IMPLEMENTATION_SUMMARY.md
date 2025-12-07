# IMPLEMENTATION_SUMMARY.md --- Implementation Summary

## Modules

-   app.main --- FastAPI entry
-   app.orchestrator --- L1 planning
-   app.coordinators --- L2 domain logic
-   app.workers --- L3 extraction tasks
-   app.cache --- Redis/in-memory
-   app.adapters --- LLM connectors

## LLM Integration

-   LangChain ChatGoogleGenerativeAI
-   Default model: gemini-2.0-flash

## Testing

-   test_api.py --- end-to-end
-   test\_\* --- unit tests
