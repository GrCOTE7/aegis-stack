# AI Advisor

Every great party needs a strategist. Meet Illiana.

## Add the AI service

```bash
aegis add-service ai
```

**Jumping in fresh?**
```bash
uvx aegis-stack init party-manager --services auth,ai --components worker,scheduler --no-interactive
cd party-manager && make serve
```

## Meet Illiana

In Rose of Eternity, Illiana is the wise advisor who helps guide the party through difficult decisions. Now she's an AI-powered endpoint that gives tactical advice based on your party's current state.

## Create the advisor endpoint

Add to `app/components/backend/api/party/router.py`:

```python
from app.services.ai.service import AIService

ILLIANA_SYSTEM_PROMPT = """You are Illiana, a wise tactical advisor for a party of heroes in Rose of Eternity.

You know the party members:
- Jonan: Knight of Dundalas, high strength (10) and defense (8), 17 HP. Best at frontline combat.
- Linard: Justice Prevails Recruit, high dexterity (14), 15 HP. Best at flanking and quick strikes.

Give tactical advice that's:
- Concise (2-3 sentences max)
- Based on character strengths
- Strategic and actionable

Speak with wisdom but stay practical."""


@router.post("/advisor")
async def ask_illiana(
    question: str,
    current_user: User = Depends(get_current_user),
):
    """Ask Illiana for tactical advice."""
    ai_service = AIService()
    response = await ai_service.chat(
        message=question,
        system_prompt=ILLIANA_SYSTEM_PROMPT,
    )
    return {"advisor": "Illiana", "advice": response}
```

The system prompt gives Illiana knowledge of your party. She'll reference character stats and abilities when giving advice.

## Test it

Get a token first (from Chapter 2):

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=jonan@dundalas.com&password=YOUR_PASSWORD"
```

Ask for tactical advice:

```bash
curl -X POST "http://localhost:8000/api/v1/party/advisor?question=We're facing three enemies. How should Jonan and Linard approach?" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Illiana responds:

```json
{
  "advisor": "Illiana",
  "advice": "Have Jonan engage two enemies directly - his high defense can absorb their attacks. Linard should flank the third enemy, using his dexterity advantage for a quick takedown before rejoining Jonan."
}
```

## What you've built

Over five chapters, you've created a complete party management system:

| Chapter | What You Added |
|---------|----------------|
| [1. First Endpoint](./01-first-endpoint.md) | Party API with character data |
| [2. Protected Routes](./02-protected-routes.md) | User authentication, CLI tools |
| [3. Background Jobs](./03-background-jobs.md) | Async combat resolution |
| [4. Scheduled Tasks](./04-scheduled-tasks.md) | HP regen, daily rewards |
| [5. AI Advisor](./05-ai-advisor.md) | Illiana gives tactical advice |

From a simple API to a fully-featured game backend. Auth protects your endpoints. Workers handle async operations. Schedulers run periodic tasks. AI provides intelligence.

That's the Aegis pattern - start simple, add what you need, everything works together.
