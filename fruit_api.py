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

class MeshAssignment(BaseModel):
    meshId: str

def simulate_fruit_generation(fruit_id: str):
    time.sleep(3)  # Simulate Meshy.ai latency
    fruit_db[fruit_id]["mesh_file"] = f"{fruit_id}.obj"

@app.post("/assignMesh")
async def assign_mesh(assignment: MeshAssignment):
    fruit = fruit_db.get(assignment.fruitId)
    if not fruit:
        raise HTTPException(status_code=404, detail="Fruit not found")

    fruit["meshId"] = assignment.meshId
    fruit["status"] = "ready"  # ✅ Mark ready only when meshId is set

    return {"message": "Mesh ID assigned", "fruitId": assignment.fruitId}


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

    response = {
        "fruitId": fruit_id,
        "status": fruit["status"],
        "prompt": fruit["prompt"],
        "mesh_file": fruit["mesh_file"],
    }

    if fruit["status"] == "ready" and fruit.get("meshId"):
        response["meshId"] = fruit["meshId"]

    return response

@app.post("/assignMesh/{fruit_id}")
async def assign_mesh_id(fruit_id: str, assignment: MeshAssignment):
    fruit = fruit_db.get(fruit_id)
    if not fruit:
        return {"error": "Fruit not found"}

    if fruit["status"] != "ready":
        return {"error": "Fruit not ready yet"}

    fruit["meshId"] = assignment.meshId
    return {
        "message": "Mesh ID assigned",
        "fruitId": fruit_id,
        "meshId": assignment.meshId
    }


