"""
Emergency Medical Dispatch Environment
911 dispatch simulation for training AI agents
Based on real emergency medical dispatch protocols
"""

import random
import math
import uuid
from typing import Dict, Any, Optional, Tuple, List
from enum import Enum
from dataclasses import dataclass

from pydantic import BaseModel, Field


class EmergencyType(str, Enum):
    CARDIAC_ARREST = "cardiac_arrest"  # Fixed: CARDIAC not CARDIAL
    STROKE = "stroke"
    CHOKING = "choking"
    SEIZURE = "seizure"
    BROKEN_BONE = "broken_bone"
    BREATHING_DIFFICULTY = "breathing_difficulty"


class Observation(BaseModel):
    """Current state of the dispatch center"""
    emergencies: List[Dict[str, Any]] = Field(..., description="Active emergencies")
    ambulances: List[Dict[str, Any]] = Field(..., description="Available ambulances")
    hospitals: List[Dict[str, Any]] = Field(..., description="Nearby hospitals")
    time_elapsed: int = Field(..., description="Minutes since first call")


class Action(BaseModel):
    """Dispatch action"""
    emergency_id: str
    ambulance_id: str
    instructions: Optional[str] = None


class EmergencyMedicalDispatchEnvironment:
    """
    911 Emergency Medical Dispatch Simulator
    
    The AI agent acts as a dispatcher who must:
    1. Prioritize emergencies by severity
    2. Dispatch closest appropriate ambulances
    3. Provide life-saving instructions to callers
    4. Balance resources across multiple incidents
    """
    
    def __init__(self):
        self.emergency_types = {
            EmergencyType.CARDIAC_ARREST: {  # Fixed: CARDIAC not CARDIAL
                "name": "Cardiac Arrest",
                "base_severity": 10,
                "critical_window": 6,  # minutes to survive
                "needs_cpr": True,
                "survival_rate_per_minute": 0.10  # 10% drop per minute
            },
            EmergencyType.STROKE: {
                "name": "Stroke",
                "base_severity": 9,
                "critical_window": 60,
                "needs_cpr": False,
                "survival_rate_per_minute": 0.02
            },
            EmergencyType.CHOKING: {
                "name": "Choking",
                "base_severity": 9,
                "critical_window": 5,
                "needs_cpr": False,
                "survival_rate_per_minute": 0.15
            },
            EmergencyType.BREATHING_DIFFICULTY: {
                "name": "Breathing Difficulty",
                "base_severity": 7,
                "critical_window": 15,
                "needs_cpr": False,
                "survival_rate_per_minute": 0.05
            },
            EmergencyType.SEIZURE: {
                "name": "Seizure",
                "base_severity": 6,
                "critical_window": 20,
                "needs_cpr": False,
                "survival_rate_per_minute": 0.03
            },
            EmergencyType.BROKEN_BONE: {
                "name": "Broken Bone",
                "base_severity": 4,
                "critical_window": 120,
                "needs_cpr": False,
                "survival_rate_per_minute": 0.00
            }
        }
        
        self.current_task_id = None
        self.active_emergencies = []
        self.ambulances = []
        self.hospitals = []
        self.step_count = 0
        self.total_reward = 0.0
        self.difficulty = "easy"
        self.done = False
        self.action_history = []
        self.lives_saved = 0
        self.total_patients = 0
        
        # Task graders
        self.tasks = {
            "easy": self._grade_basic_dispatch,
            "medium": self._grade_priority_management,
            "hard": self._grade_full_crisis
        }
    
    def _calculate_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        """Calculate Manhattan distance between two points"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def _generate_scenario(self, difficulty: str) -> Tuple[List, List, List]:
        """Generate emergencies, ambulances, hospitals based on difficulty"""
        
        # Hospital locations (always available)
        hospitals = [
            {"id": "H1", "location": (3, 8), "capacity": 5, "trauma_level": 1},
            {"id": "H2", "location": (7, 2), "capacity": 3, "trauma_level": 2},
            {"id": "H3", "location": (5, 5), "capacity": 4, "trauma_level": 1}
        ]
        
        if difficulty == "easy":
            # 2 emergencies, 2 ambulances
            emergencies = [
                {
                    "id": "E001",
                    "type": EmergencyType.BROKEN_BONE,
                    "severity": 4,
                    "location": (2, 3),
                    "critical_time": 120,
                    "time_elapsed": 0
                },
                {
                    "id": "E002",
                    "type": EmergencyType.CARDIAC_ARREST,  # Fixed
                    "severity": 10,
                    "location": (7, 7),
                    "critical_time": 6,
                    "time_elapsed": 0
                }
            ]
            ambulances = [
                {"id": "A1", "location": (4, 4), "status": "available", "eta": 0},
                {"id": "A2", "location": (8, 3), "status": "available", "eta": 0}
            ]
            
        elif difficulty == "medium":
            # 4 emergencies, 3 ambulances
            emergencies = [
                {
                    "id": "E001",
                    "type": EmergencyType.CARDIAC_ARREST,  # Fixed
                    "severity": 10,
                    "location": (2, 8),
                    "critical_time": 6,
                    "time_elapsed": 0
                },
                {
                    "id": "E002",
                    "type": EmergencyType.STROKE,
                    "severity": 9,
                    "location": (8, 2),
                    "critical_time": 60,
                    "time_elapsed": 0
                },
                {
                    "id": "E003",
                    "type": EmergencyType.BROKEN_BONE,
                    "severity": 4,
                    "location": (5, 5),
                    "critical_time": 120,
                    "time_elapsed": 0
                },
                {
                    "id": "E004",
                    "type": EmergencyType.BREATHING_DIFFICULTY,
                    "severity": 7,
                    "location": (3, 1),
                    "critical_time": 15,
                    "time_elapsed": 0
                }
            ]
            ambulances = [
                {"id": "A1", "location": (4, 4), "status": "available", "eta": 0},
                {"id": "A2", "location": (6, 6), "status": "available", "eta": 0},
                {"id": "A3", "location": (2, 2), "status": "available", "eta": 0}
            ]
            
        else:  # hard
            # 6 emergencies, 4 ambulances (one already busy)
            emergencies = [
                {
                    "id": "E001",
                    "type": EmergencyType.CARDIAC_ARREST,  # Fixed
                    "severity": 10,
                    "location": (9, 1),
                    "critical_time": 6,
                    "time_elapsed": 0
                },
                {
                    "id": "E002",
                    "type": EmergencyType.CHOKING,
                    "severity": 9,
                    "location": (1, 9),
                    "critical_time": 5,
                    "time_elapsed": 0
                },
                {
                    "id": "E003",
                    "type": EmergencyType.STROKE,
                    "severity": 9,
                    "location": (4, 4),
                    "critical_time": 60,
                    "time_elapsed": 0
                },
                {
                    "id": "E004",
                    "type": EmergencyType.BREATHING_DIFFICULTY,
                    "severity": 7,
                    "location": (7, 3),
                    "critical_time": 15,
                    "time_elapsed": 0
                },
                {
                    "id": "E005",
                    "type": EmergencyType.SEIZURE,
                    "severity": 6,
                    "location": (2, 6),
                    "critical_time": 20,
                    "time_elapsed": 0
                },
                {
                    "id": "E006",
                    "type": EmergencyType.BROKEN_BONE,
                    "severity": 4,
                    "location": (8, 8),
                    "critical_time": 120,
                    "time_elapsed": 0
                }
            ]
            ambulances = [
                {"id": "A1", "location": (5, 5), "status": "available", "eta": 0},
                {"id": "A2", "location": (3, 3), "status": "available", "eta": 0},
                {"id": "A3", "location": (7, 7), "status": "en_route", "eta": 8},
                {"id": "A4", "location": (1, 1), "status": "available", "eta": 0}
            ]
        
        return emergencies, ambulances, hospitals
    
    def _grade_basic_dispatch(self, history: List[Action]) -> float:
        """Easy task: Send closest ambulance to highest priority"""
        if not history or len(self.active_emergencies) == 0:
            return 0.0
        
        score = 0.0
        
        # Check if cardiac arrest got fastest response
        cardiac_calls = [e for e in self.active_emergencies if e["type"] == EmergencyType.CARDIAC_ARREST]
        if cardiac_calls:
            cardiac = cardiac_calls[0]
            # Find which ambulance was sent to cardiac
            for action in history:
                if action.emergency_id == cardiac["id"]:
                    # Check response time
                    ambulance = next((a for a in self.ambulances if a["id"] == action.ambulance_id), None)
                    if ambulance:
                        distance = self._calculate_distance(
                            tuple(cardiac["location"]),
                            tuple(ambulance["location"])
                        )
                        if distance <= 3:  # Close ambulance
                            score += 0.5
        
        # Check if all emergencies got response
        responded_emergencies = set(a.emergency_id for a in history)
        response_rate = len(responded_emergencies) / len(self.active_emergencies)
        score += 0.5 * response_rate
        
        return min(1.0, score)
    
    def _grade_priority_management(self, history: List[Action]) -> float:
        """Medium task: Correct prioritization and resource allocation"""
        if not history:
            return 0.0
        
        score = 0.0
        
        # Prioritization correctness (0-0.5)
        # Higher severity should get faster response
        response_times = {}
        for action in history:
            if action.emergency_id not in response_times:
                response_times[action.emergency_id] = self.step_count
        
        severity_order = sorted(self.active_emergencies, key=lambda e: e["severity"], reverse=True)
        for i, emergency in enumerate(severity_order):
            if emergency["id"] in response_times:
                response_order = list(response_times.keys()).index(emergency["id"])
                if response_order <= i:
                    score += 0.1
        
        score = min(0.5, score)
        
        # Resource efficiency (0-0.5)
        # Don't send far ambulance when close one is available
        for action in history:
            emergency = next((e for e in self.active_emergencies if e["id"] == action.emergency_id), None)
            ambulance = next((a for a in self.ambulances if a["id"] == action.ambulance_id), None)
            if emergency and ambulance:
                distance = self._calculate_distance(
                    tuple(emergency["location"]),
                    tuple(ambulance["location"])
                )
                # Penalty for long distances when closer available
                closer_exists = any(
                    self._calculate_distance(tuple(emergency["location"]), tuple(a["location"])) < distance
                    for a in self.ambulances if a["status"] == "available"
                )
                if not closer_exists:
                    score += 0.1
        
        return min(1.0, score)
    
    def _grade_full_crisis(self, history: List[Action]) -> float:
        """Hard task: Survival rates, CPR instructions, hospital capacity"""
        if not history:
            return 0.0
        
        # Survival rate is the primary metric (0-0.7)
        survival_rate = self.lives_saved / max(self.total_patients, 1)
        score = 0.7 * survival_rate
        
        # CPR instruction quality (0-0.3)
        cpr_instructions_given = False
        for action in history:
            if action.instructions and ("cpr" in action.instructions.lower() or "chest" in action.instructions.lower()):
                cpr_instructions_given = True
                break
        
        if cpr_instructions_given:
            score += 0.3
        
        return min(1.0, score)
    
    def reset(self, difficulty: str = "easy") -> Observation:
        """Reset the environment for a new episode"""
        self.current_task_id = str(uuid.uuid4())
        self.difficulty = difficulty
        self.step_count = 0
        self.total_reward = 0.0
        self.done = False
        self.action_history = []
        self.lives_saved = 0
        
        # Generate scenario based on difficulty
        self.active_emergencies, self.ambulances, self.hospitals = self._generate_scenario(difficulty)
        
        self.total_patients = len(self.active_emergencies)
        
        return self._get_observation()
    
    def _get_observation(self) -> Observation:
        """Get current observation"""
        return Observation(
            emergencies=self.active_emergencies,
            ambulances=self.ambulances,
            hospitals=self.hospitals,
            time_elapsed=self.step_count * 2  # 2 minutes per step
        )
    
    def step(self, action: Action) -> Tuple[Observation, float, bool, Dict]:
        """Execute a dispatch action"""
        if self.done:
            raise RuntimeError("Episode already done. Call reset() first.")
        
        self.action_history.append(action)
        
        # Find the emergency and ambulance
        emergency = next((e for e in self.active_emergencies if e["id"] == action.emergency_id), None)
        ambulance = next((a for a in self.ambulances if a["id"] == action.ambulance_id), None)
        
        reward = 0.0
        reward_details = {}
        
        if not emergency:
            reward -= 0.2
            reward_details["error"] = "Invalid emergency ID"
        elif not ambulance:
            reward -= 0.2
            reward_details["error"] = "Invalid ambulance ID"
        elif ambulance["status"] != "available":
            reward -= 0.3
            reward_details["error"] = "Ambulance not available"
        else:
            # Calculate travel time
            distance = self._calculate_distance(
                tuple(emergency["location"]),
                tuple(ambulance["location"])
            )
            travel_time = distance * 2  # 2 minutes per grid unit
            
            # Check if patient survives
            survival_probability = self._calculate_survival(emergency, travel_time)
            
            if random.random() < survival_probability:
                # Patient survived!
                self.lives_saved += 1
                reward = 0.8 * survival_probability
                reward_details["outcome"] = "survived"
                reward_details["travel_time"] = travel_time
            else:
                # Patient died
                reward = 0.0
                reward_details["outcome"] = "died"
                reward_details["travel_time"] = travel_time
            
            # Bonus for good instructions
            if emergency["type"] == EmergencyType.CARDIAC_ARREST and action.instructions:
                if "cpr" in action.instructions.lower():
                    reward += 0.2
                    reward_details["cpr_bonus"] = 0.2
            
            # Mark ambulance as busy
            ambulance["status"] = "en_route"
            ambulance["eta"] = travel_time
            
            # Remove emergency from active list
            self.active_emergencies = [e for e in self.active_emergencies if e["id"] != action.emergency_id]
        
        self.step_count += 1
        self.total_reward += reward
        
        # Update ambulance ETAs
        for amb in self.ambulances:
            if amb["status"] == "en_route" and amb["eta"] > 0:
                amb["eta"] -= 2
                if amb["eta"] <= 0:
                    amb["status"] = "available"
                    amb["eta"] = 0
        
        # Check if episode is done
        if len(self.active_emergencies) == 0 or self.step_count >= 15:
            self.done = True
            # Add task completion bonus
            task_score = self.tasks[self.difficulty](self.action_history)
            reward += task_score * 0.5
            reward = min(1.0, reward)
            reward_details["task_score"] = task_score
        
        info = {
            "total_reward": self.total_reward,
            "reward_breakdown": reward_details,
            "lives_saved": self.lives_saved,
            "total_patients": self.total_patients,
            "survival_rate": self.lives_saved / max(self.total_patients, 1),
            "remaining_emergencies": len(self.active_emergencies),
            "step": self.step_count
        }
        
        return self._get_observation(), reward, self.done, info
    
    def _calculate_survival(self, emergency: Dict, travel_time: int) -> float:
        """Calculate survival probability based on emergency type and response time"""
        emergency_type = emergency["type"]
        critical_time = emergency["critical_time"]
        
        if travel_time <= critical_time:
            # Within critical window
            base_survival = 0.95
            decay = (travel_time / critical_time) * 0.3
            return max(0.65, base_survival - decay)
        else:
            # Beyond critical window
            overtime = travel_time - critical_time
            decay = min(0.95, overtime * 0.1)
            return max(0.05, 0.95 - decay)
    
    def state(self) -> Dict[str, Any]:
        """Return current environment state"""
        return {
            "task_id": self.current_task_id,
            "difficulty": self.difficulty,
            "step_count": self.step_count,
            "total_reward": self.total_reward,
            "lives_saved": self.lives_saved,
            "total_patients": self.total_patients,
            "survival_rate": self.lives_saved / max(self.total_patients, 1),
            "remaining_emergencies": len(self.active_emergencies),
            "done": self.done
        }


def make_env():
    """Factory function for OpenEnv compliance"""
    return EmergencyMedicalDispatchEnvironment()