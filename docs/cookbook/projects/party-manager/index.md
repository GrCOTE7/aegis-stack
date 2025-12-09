# Party Manager

We're building a party management system for Rose of Eternity - a tactical RPG. Characters, stats, abilities, equipment. The kind of system that needs auth, background jobs, scheduled tasks, and eventually an AI advisor.

Each chapter adds a new Aegis component or service. By the end, you'll have a real system and understand how all the pieces fit together.

## What we're building

- **Party roster** with characters and their stats
- **User authentication** so each player owns their party
- **Combat resolution** via background jobs
- **Regeneration and rewards** via scheduled tasks
- **Illiana** - an AI tactical advisor

## Chapters

| Chapter | What You'll Add |
|---------|-----------------|
| [1. First Endpoint](./01-first-endpoint.md) | Party API with character data |
| [2. Protected Routes](./02-protected-routes.md) | Auth service, CLI user management |
| [3. Background Jobs](./03-background-jobs.md) | Combat as async work |
| [4. Scheduled Tasks](./04-scheduled-tasks.md) | HP regen, daily rewards |
| [5. AI Advisor](./05-ai-advisor.md) | Illiana gives tactical advice |

## Starting point

If you're jumping in mid-project, each chapter has the command to get caught up.

Start fresh:
```bash
uvx aegis-stack init party-manager --no-interactive
cd party-manager && make serve
```
