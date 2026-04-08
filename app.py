"""
OpenEnv API Server for Emergency Medical Dispatch Environment
Provides /reset endpoint for the OpenEnv validator
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uuid

from environment import EmergencyMedicalDispatchEnvironment, Observation, Action

app = FastAPI(title="Emergency Medical Dispatch Environment")

# Store active environments
environments = {}


class ResetRequest(BaseModel):
    difficulty: Optional[str] = "easy"


class ResetResponse(BaseModel):
    task_id: str
    observation: Dict[str, Any]
    state: Dict[str, Any]


@app.post("/reset")
async def reset_endpoint(request: ResetRequest):
    """Reset the environment and return initial observation"""
    try:
        env = EmergencyMedicalDispatchEnvironment()
        obs = env.reset(difficulty=request.difficulty)
        
        task_id = str(uuid.uuid4())
        environments[task_id] = env
        
        return ResetResponse(
            task_id=task_id,
            observation=obs.model_dump(),
            state=env.state()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)