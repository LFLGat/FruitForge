from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import Dict
import uuid
import time

app = FastAPI()

# In-memory storage for demo purposes (use a DB in production)
fruit_db: Dict[str, Dict] = {}

class FruitPrompt(BaseModel):
    userId: int
    prompt: str

def simulate_fruit_generation(fruit_id: str):
    time.sleep(3)  # Simulate time delay (e.g., generating mesh)
    fruit_db[fruit_id]["status"] = "ready"
    fruit_db[fruit_id]["mesh_file"] = f"{fruit_id}.glb"

@app.post("/submitFruit")
async def submit_fruit(prompt: FruitPrompt, background_tasks: BackgroundTasks):
    fruit_id = f"fruit_{uuid.uuid4().hex[:8]}"
    fruit_db[fruit_id] = {
        "userId": prompt.userId,
        "prompt": prompt.prompt,
        "status": "growing",
        "mesh_file": None,
        "timestamp": time.time()
    }
    background_tasks.add_task(simulate_fruit_generation, fruit_id)
    return {"fruitId": fruit_id, "status": "growing"}

@app.get("/fruitStatus/{fruit_id}")
async def get_fruit_status(fruit_id: str):
    fruit = fruit_db.get(fruit_id)
    if not fruit:
        return {"error": "Fruit not found"}
    return {
        "fruitId": fruit_id,
        "status": fruit["status"],
        "mesh_file": fruit["mesh_file"]
    }
