from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import Dict
import uuid
import time
import random

app = FastAPI()

RARITY_TIERS = [
    ("Wilted", 0.30),
    ("Sprout", 0.25),
    ("Juicy", 0.15),
    ("Ripe", 0.10),
    ("Vibrant", 0.07),
    ("Mystic", 0.05),
    ("Blazing", 0.035),
    ("Celestial", 0.024),
    ("Enchanted", 0.01),
    ("Divine Bloom", 0.001),
]

def assign_rarity(prompt: str) -> str:
    word_count = len(prompt.split())
    bias = min(word_count / 50, 1.0) * 0.15
    roll = random.random() + bias

    cumulative = 0
    total_weight = sum(w for _, w in RARITY_TIERS)
    for name, weight in RARITY_TIERS:
        cumulative += weight / total_weight
        if roll <= cumulative:
            return name
    return "Wilted"


# In-memory storage for demo purposes (use a DB in production)
fruit_db: Dict[str, Dict] = {}

class FruitPrompt(BaseModel):
    userId: int
    prompt: str

class MeshAssignment(BaseModel):
    meshId: str

def simulate_fruit_generation(fruit_id: str):
    time.sleep(3)  # Simulate Meshy.ai latency
    fruit_db[fruit_id]["mesh_file"] = f"{fruit_id}.obj"

@app.post("/submitFruit")
async def submit_fruit(prompt: FruitPrompt, background_tasks: BackgroundTasks):
    fruit_id = f"fruit_{uuid.uuid4().hex[:8]}"
    rarity = assign_rarity(prompt.prompt)

    fruit_db[fruit_id] = {
        "userId": prompt.userId,
        "prompt": prompt.prompt,
        "status": "growing",
        "rarity": rarity,
        "mesh_file": None,
        "meshId": None,
        "timestamp": time.time()
    }

    background_tasks.add_task(simulate_fruit_generation, fruit_id)
    return {"fruitId": fruit_id, "status": "growing", "rarity": rarity}


@app.get("/fruitStatus/{fruit_id}")
async def get_fruit_status(fruit_id: str):
    fruit = fruit_db.get(fruit_id)
    if not fruit:
        return {"error": "Fruit not found"}

    response = {
        "fruitId": fruit_id,
        "status": fruit["status"],
        "mesh_file": fruit["mesh_file"],
        "meshId": fruit["meshId"],
        "rarity": fruit["rarity"]
    }

    if fruit["status"] == "ready" and fruit.get("meshId"):
        response["meshId"] = fruit["meshId"]

    return response

@app.post("/assignMesh/{fruit_id}")
async def assign_mesh_id(fruit_id: str, assignment: MeshAssignment):
    fruit = fruit_db.get(fruit_id)
    if not fruit:
        return {"error": "Fruit not found"}

    if fruit["status"] != "growing":
        return {"error": "Fruit not ready yet"}

    fruit["meshId"] = assignment.meshId
    fruit["status"] = "ready"
    return {
        "message": "Mesh ID assigned",
        "fruitId": fruit_id,
        "meshId": assignment.meshId
    }


