# EXECUTION_GUIDE.md --- Execution Guide

## Execution Flow

1.  Receive message.
2.  L1 Orchestrator creates task plan.
3.  L2 Coordinators execute extraction routes.
4.  L3 Workers run fast extraction tasks.
5.  Results aggregated + returned.

## Troubleshooting

-   Missing GOOGLE_API_KEY → set env variable.
-   Redis errors → run redis-server or disable caching.
-   Rate limits → reduce request frequency.

## Logs

-   Docker: `docker-compose logs -f`
-   Local: uvicorn console logs
