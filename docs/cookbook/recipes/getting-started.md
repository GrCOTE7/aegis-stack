# Getting Started

Let's spin up a project and see what you get out of the box.

## Create the project

```bash
uvx aegis-stack init my-project --no-interactive
cd my-project
```

That's it. You now have a FastAPI backend, a Flet dashboard, Docker setup, health monitoring, CLI tools, and a test suite. No configuration required.

## Start it up

```bash
make serve
```

First run pulls images and builds containers. Give it a minute. When you see the health checks passing in the logs, you're ready.

## What you're looking at

Open your browser:

- **[http://localhost:8000/health/](http://localhost:8000/health/)** - Quick health check. Load balancers love this endpoint.
- **[http://localhost:8000/health/detailed](http://localhost:8000/health/detailed)** - The full picture. Component status, system metrics, everything.
- **[http://localhost:8000/dashboard](http://localhost:8000/dashboard)** - [Overseer](../../overseer/index.md), the built-in health monitoring dashboard.

Hit the health endpoint from the terminal:

```bash
curl http://localhost:8000/health/detailed | jq
```

You'll see something like:

```json
{
  "healthy": true,
  "status": "healthy",
  "components": {
    "fastapi": {"healthy": true, "status": "running"},
    "flet": {"healthy": true, "status": "running"}
  },
  "system": {
    "cpu_percent": 12.5,
    "memory_percent": 45.2,
    "disk_percent": 68.0
  }
}
```

Every component you add later shows up here automatically.

## Your project's CLI

Every Aegis project gets its own CLI. The command matches your project name:

```bash
source .venv/bin/activate
my-project health status
my-project health status --detailed
my-project health status --json
```

As you add components, the CLI grows. Add auth? You get `my-project auth` commands. Add the scheduler? You get `my-project tasks`. The CLI is how you interact with your running system.

## Project structure

Here's what matters:

```
my-project/
├── app/
│   ├── components/
│   │   ├── backend/     # FastAPI lives here
│   │   └── frontend/    # Flet dashboard
│   ├── services/        # Your business logic goes here
│   └── models/          # Data models
├── tests/               # Pytest suite ready to go
├── docker-compose.yml   # One command to run everything
└── Makefile            # Developer workflow shortcuts
```

The `components/` split is intentional. Backend and frontend are independent but wired together. Add more components later, they slot right in.

## The Makefile

Every project includes a Makefile with common workflows. It's just convenience - everything it does you could do manually with docker compose or the CLI. But it saves typing.

```bash
make serve      # Start everything
make stop       # Graceful shutdown
make logs       # Follow all logs
make test       # Run the test suite
make check      # Lint + typecheck + test
```

Run `make` with no arguments to see all available commands.

## What you have now

- A FastAPI server with health endpoints
- A Flet dashboard showing system health
- Docker Compose orchestration
- CLI tools for management
- A test framework ready to use
- Structured logging
- CORS configured

This is the foundation. Every recipe builds on this.

## Next

**[Your First Endpoint →](./your-first-endpoint.md)** - Add a custom route and see how it fits in the project structure.
