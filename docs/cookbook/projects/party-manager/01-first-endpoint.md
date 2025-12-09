# Your First Endpoint

You've got a running project. Now let's add something to it.

We're building a party management API - characters from Rose of Eternity.

## Create the model

`app/models/character.py`:

```python
from pydantic import BaseModel


class CharacterStats(BaseModel):
    hit_points: int
    ability_points: int
    movement: int
    speed: int
    dexterity: int
    magic: int
    strength: int
    defense: int


class Character(BaseModel):
    id: str
    name: str
    title: str
    stats: CharacterStats
```

## Create the router

`app/components/backend/api/party/router.py`:

```python
from fastapi import APIRouter, HTTPException

from app.models.character import Character, CharacterStats

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
async def list_party() -> list[Character]:
    return list(PARTY.values())


@router.get("/{character_id}")
async def get_character(character_id: str) -> Character:
    if character_id not in PARTY:
        raise HTTPException(status_code=404, detail="Character not found")
    return PARTY[character_id]
```

## Wire it up

In `app/components/backend/api/routing.py`:

```python
from app.components.backend.api.party.router import router as party_router

# In include_routers():
app.include_router(party_router, prefix="/api/v1")
```

## Test it

```bash
curl http://localhost:8000/api/v1/party/ | jq
curl http://localhost:8000/api/v1/party/jonan | jq
```

## Next

**[Chapter 2: Protected Routes →](./02-protected-routes.md)**
