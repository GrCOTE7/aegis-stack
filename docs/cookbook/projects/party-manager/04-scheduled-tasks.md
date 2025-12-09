# Scheduled Tasks

HP doesn't stay low forever. Let's add regeneration and daily rewards.

## Add the scheduler component

```bash
aegis add scheduler
```

**Jumping in fresh?**
```bash
uvx aegis-stack init party-manager --services auth --components worker,scheduler --no-interactive
cd party-manager && make serve
```

## How schedulers work

Aegis uses [APScheduler](https://apscheduler.readthedocs.io/) - a battle-tested Python scheduler. You define jobs in `app/components/scheduler/main.py` and they run automatically.

Two trigger types:

1. **Interval** - runs every X minutes/hours (HP regen)
2. **Cron** - runs at specific times (daily rewards at midnight)

## Create the task functions

Add `app/services/party_tasks.py`:

```python
from app.core.log import logger


async def regenerate_party_hp() -> None:
    """Restore HP to all party members over time."""
    logger.info("Regenerating party HP...")

    # In a real app, you'd update the database here
    # For now, just log it
    logger.info("Party HP regenerated (+5 HP to all members)")


async def grant_daily_rewards() -> None:
    """Grant daily login rewards."""
    logger.info("Granting daily rewards...")

    # Award gold, items, etc.
    logger.info("Daily rewards granted (100 gold)")
```

Simple async functions. In production, these would update your database.

## Wire them into the scheduler

Edit `app/components/scheduler/main.py`. Find `create_scheduler()` and add your jobs:

```python
from app.services.party_tasks import regenerate_party_hp, grant_daily_rewards


def create_scheduler() -> AsyncIOScheduler:
    """Create and configure the scheduler with all jobs."""
    scheduler = AsyncIOScheduler()

    # HP regeneration every 30 minutes
    scheduler.add_job(
        regenerate_party_hp,
        trigger="interval",
        minutes=30,
        id="hp_regen",
        name="Party HP Regeneration",
    )

    # Daily rewards at midnight
    scheduler.add_job(
        grant_daily_rewards,
        trigger="cron",
        hour=0,
        minute=0,
        id="daily_rewards",
        name="Daily Rewards",
    )

    return scheduler
```

The scheduler container runs these automatically.

## Test it

Check scheduler logs to see jobs register and run:

```bash
docker compose logs -f scheduler
```

You'll see output like:

```
Scheduler started successfully
2 jobs scheduled:
   • Party HP Regeneration - interval[0:30:00]
   • Daily Rewards - cron[0 0 * * *]
```

For faster testing, temporarily change the interval to 1 minute:

```python
scheduler.add_job(
    regenerate_party_hp,
    trigger="interval",
    minutes=1,  # Quick test
    ...
)
```

Watch the logs and you'll see it fire.

## What you have now

- Interval-based tasks (HP regen every 30 min)
- Cron-based tasks (daily rewards at midnight)
- APScheduler integration
- The pattern for any scheduled operation

## Next

**[Chapter 5: AI Advisor →](./05-ai-advisor.md)**
