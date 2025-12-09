# Background Jobs

Combat takes time to resolve. Let's offload it to a worker.

## Add the worker component

```bash
aegis add worker
```

**Jumping in fresh?**
```bash
uvx aegis-stack init party-manager --services auth --components worker --no-interactive
cd party-manager && make serve
```

## How workers work

Aegis uses [arq](https://arq-docs.helpmanual.io/) - a fast async job queue built on Redis. You get a `system` queue out of the box with a worker already running.

The pattern:

1. **Tasks** - async functions that do the work
2. **WorkerSettings** - registers tasks with a queue
3. **Pools** - Redis connections for enqueueing jobs

## Create the combat task

Add `app/components/worker/tasks/combat_tasks.py`:

```python
from datetime import UTC, datetime
from typing import Any
import random

from app.core.log import logger


async def resolve_attack(
    ctx: dict[str, Any],
    attacker_id: str,
    target_id: str,
    ability_id: int,
) -> dict[str, Any]:
    """Resolve a combat action."""
    logger.info(f"Resolving: {attacker_id} -> {target_id}")

    # Simplified combat math
    hit_roll = random.randint(1, 100)
    damage = random.randint(5, 15) if hit_roll <= 90 else 0

    return {
        "attacker": attacker_id,
        "target": target_id,
        "hit": hit_roll <= 90,
        "damage": damage,
        "timestamp": datetime.now(UTC).isoformat(),
    }
```

The `ctx` dict is arq's context - it has job metadata and can be used for dependency injection.

## Register it with the system queue

Add to `app/components/worker/queues/system.py`:

```python
from app.components.worker.tasks.combat_tasks import resolve_attack

class WorkerSettings:
    functions = [
        system_health_check,
        cleanup_temp_files,
        resolve_attack,  # Add this
    ]
```

The `system` queue already has a worker running via docker compose. Your task is now available.

## Queue from the API

Add to `app/components/backend/api/party/router.py`:

```python
from app.components.worker.pools import get_queue_pool


@router.post("/attack")
async def queue_attack(
    attacker_id: str,
    target_id: str,
    ability_id: int,
    current_user: User = Depends(get_current_user),
):
    """Queue a combat action for async resolution."""
    pool, queue_name = await get_queue_pool("system")

    job = await pool.enqueue_job(
        "resolve_attack",
        attacker_id,
        target_id,
        ability_id,
        _queue_name=queue_name,
    )

    return {"job_id": job.job_id, "status": "queued"}
```

The endpoint returns immediately with a job ID. The worker processes it in the background.

## Test it

```bash
curl -X POST "http://localhost:8000/api/v1/party/attack?attacker_id=jonan&target_id=enemy1&ability_id=1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Check `worker-system` logs to see it process:

```bash
docker compose logs -f worker-system
```

## See it in Overseer

Open [http://localhost:8000/dashboard](http://localhost:8000/dashboard). The Worker card shows:

- Queue status (system, load_test)
- Jobs queued, active, completed, failed
- Failure rates per queue
- Worker health indicators

Queue a few attacks and watch the numbers update in real-time.

## What you have now

- Async job processing with arq
- Redis-backed job queue
- Combat resolution as background work
- Real-time worker monitoring in Overseer
- The pattern for any async operation

## Next

**[Chapter 4: Scheduled Tasks →](./04-scheduled-tasks.md)**
