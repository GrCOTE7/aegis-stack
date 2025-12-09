# Cookbook

I've spent too many hours of my life wiring up the same patterns. Auth endpoints. Background jobs. Health checks. Scheduled tasks. Every project needs them, and every project reinvents them.

The cookbook is my attempt to shortcut that pain. They're recipes, the patterns I've used, the way I wire things up, with enough context to understand why.

## What's Here

Each recipe walks through building something real with Aegis Stack. Some are quick, like spinning up a project, see it work. Others go deeper... add a route, customize something, see how the pieces fit together.

I'll share my thoughts along the way. Why I chose certain patterns. What I've seen go wrong. The stuff that's hard to find in docs but obvious once you've lived through it.

## Recipes

| Recipe | What You'll Build |
|--------|-------------------|
| **[Getting Started](./recipes/getting-started.md)** | Create a project, explore what you get |

## Projects

Multi-chapter builds where you create something real.

| Project | What You'll Build |
|---------|-------------------|
| **[Party Manager](./projects/party-manager/index.md)** | Rose of Eternity party system - auth, background jobs, scheduled tasks, AI advisor |

## How These Work

Most recipes start the same way:

```bash
uvx aegis-stack init my-project --services X --components Y
cd my-project && docker compose up -d
```

Then we explore what you got. Maybe add something small to show how it extends. See it work.

No 50-step tutorials. No "first, let's understand the theory." Just building.

---

If you want the philosophy behind all this, check out **[About](../about.md)** and **[How I Build](../process.md)**.

If you want to dive into specific components, **[Components](../components/index.md)** and **[Services](../services/index.md)** have the details.

Otherwise, pick a recipe and let's build something.
