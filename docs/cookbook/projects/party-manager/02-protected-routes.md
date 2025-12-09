# Protected Routes

Right now anyone can hit the party API. Let's fix that.

## Add auth to your project

Aegis lets you add services to existing projects. No need to start over:

```bash
aegis add-service auth
```

This adds the auth service files, database migrations, and CLI commands to your project.

**Jumping in fresh?**
```bash
uvx aegis-stack init party-manager --services auth --no-interactive
cd party-manager && make serve
```

## Create test users with the CLI

Auth service comes with CLI commands. Create some users:

```bash
source .venv/bin/activate

# Create users for our heroes
party-manager auth create-test-user --email jonan@dundalas.com --full-name "Jonan"
party-manager auth create-test-user --email linard@justiceprevails.com --full-name "Linard Janson"

# See what we have
party-manager auth list-users
```

You'll see a nice table with user IDs, emails, and auto-generated passwords. Save those passwords.

## Protect the party routes

Update `app/components/backend/api/party/router.py`:

```python
from fastapi import APIRouter, Depends, HTTPException

from app.models.character import Character, CharacterStats
from app.models.user import User
from app.services.auth.dependencies import get_current_user

router = APIRouter(prefix="/party", tags=["party"])

PARTY = {
    "jonan": Character(
        id="jonan",
        name="Jonan",
        title="Knight of Dundalas",
        stats=CharacterStats(
            hit_points=17, ability_points=10, movement=5,
            speed=4, dexterity=4, magic=3, strength=10, defense=8,
        ),
    ),
}


@router.get("/")
async def list_party(current_user: User = Depends(get_current_user)) -> list[Character]:
    return list(PARTY.values())


@router.get("/{character_id}")
async def get_character(
    character_id: str,
    current_user: User = Depends(get_current_user),
) -> Character:
    if character_id not in PARTY:
        raise HTTPException(status_code=404, detail="Character not found")
    return PARTY[character_id]
```

The `get_current_user` dependency handles everything - token validation, user lookup, 401 if not authenticated.

## Test it

Without auth:
```bash
curl http://localhost:8000/api/v1/party/
# 401 Unauthorized
```

Get a token:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=jonan@dundalas.com&password=YOUR_PASSWORD"
```

Use the token:
```bash
curl http://localhost:8000/api/v1/party/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Now you're in.

## What you have now

- Protected API endpoints
- JWT authentication
- CLI tools for user management
- The pattern for securing any route

## Next

**[Chapter 3: Background Jobs →](./03-background-jobs.md)**
