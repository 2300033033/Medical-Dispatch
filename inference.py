#!/usr/bin/env python3
"""
Emergency Medical Dispatch AI - FREE RULE-BASED VERSION
No API key required - uses smart priority logic
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, Any

from environment import EmergencyMedicalDispatchEnvironment, Action


def get_rule_based_action(observation: Dict, difficulty: str) -> Action:
    """Smart rule-based dispatch (no API needed)"""
    
    emergencies = observation.get('emergencies', [])
    ambulances = observation.get('ambulances', [])
    
    available_ambulances = [a for a in ambulances if a.get('status') == 'available']
    
    if not emergencies or not available_ambulances:
        return Action(emergency_id="unknown", ambulance_id="unknown")
    
    # Priority order (highest first)
    priority_order = {
        "cardiac_arrest": 100,
        "choking": 90,
        "stroke": 80,
        "breathing_difficulty": 70,
        "seizure": 60,
        "broken_bone": 40
    }
    
    # Sort by priority
    sorted_emergencies = sorted(
        emergencies, 
        key=lambda e: priority_order.get(e.get("type", ""), 0), 
        reverse=True
    )
    
    # Dispatch highest priority to closest ambulance
    for emergency in sorted_emergencies:
        if available_ambulances:
            # Find closest ambulance
            closest = min(
                available_ambulances,
                key=lambda a: abs(a["location"][0] - emergency["location"][0]) + 
                             abs(a["location"][1] - emergency["location"][1])
            )
            
            # Give CPR instructions for cardiac arrest
            instructions = None
            if emergency.get("type") == "cardiac_arrest":
                instructions = "CPR: Push hard and fast in center of chest at 100-120 beats per minute. Call for AED."
            elif emergency.get("type") == "choking":
                instructions = "Heimlich maneuver: Stand behind, arms around waist, quick upward thrusts."
            
            return Action(
                emergency_id=emergency["id"],
                ambulance_id=closest["id"],
                instructions=instructions
            )
    
    return Action(emergency_id="unknown", ambulance_id="unknown")


def run_episode(difficulty: str) -> Dict[str, Any]:
    """Run one complete dispatch episode"""
    env = EmergencyMedicalDispatchEnvironment()
    obs = env.reset(difficulty=difficulty)
    done = False
    total_reward = 0.0
    step_count = 0
    
    print(f"\n{'='*60}")
    print(f"🚑 [START] Emergency Dispatch - {difficulty.upper()}")
    print(f"   Patients waiting: {len(obs.emergencies)}")
    print(f"   Ambulances available: {len([a for a in obs.ambulances if a['status'] == 'available'])}")
    print(f"{'='*60}\n")
    
    while not done:
        action = get_rule_based_action(obs.dict(), difficulty)
        
        obs, reward, done, info = env.step(action)
        total_reward += reward
        step_count += 1
        
        outcome = info['reward_breakdown'].get('outcome', 'unknown')
        symbol = "✅" if outcome == 'survived' else "❌" if outcome == 'died' else "🟡"
        print(f"[STEP {step_count}] {symbol} Sent {action.ambulance_id} to {action.emergency_id}")
        print(f"   Reward: {reward:.3f} | Lives saved: {info['lives_saved']}/{info['total_patients']}")
        if action.instructions:
            instr_short = action.instructions[:50] + "..." if len(action.instructions) > 50 else action.instructions
            print(f"   📞 Instructions: {instr_short}")
        print()
        
        if step_count >= 15:
            break
    
    survival_rate = env.lives_saved / max(env.total_patients, 1)
    task_score = env.tasks[difficulty](env.action_history)
    
    print(f"{'='*60}")
    print(f"🏥 [END] {difficulty.upper()} - Mission Complete")
    print(f"   Lives saved: {env.lives_saved}/{env.total_patients}")
    print(f"   Survival rate: {survival_rate:.1%}")
    print(f"   Task score: {task_score:.3f}")
    print(f"   Total reward: {total_reward:.3f}")
    print(f"{'='*60}\n")
    
    return {
        "difficulty": difficulty,
        "lives_saved": env.lives_saved,
        "total_patients": env.total_patients,
        "survival_rate": survival_rate,
        "task_score": task_score,
        "total_reward": total_reward,
        "steps": step_count
    }


def main():
    """Run evaluation"""
    print("=" * 60)
    print("🚑 EMERGENCY MEDICAL DISPATCH AI - RULE-BASED AGENT")
    print("=" * 60)
    print("(No API key required - using smart priority rules)")
    print("=" * 60)
    
    results = []
    
    for difficulty in ["easy", "medium", "hard"]:
        result = run_episode(difficulty)
        results.append(result)
        time.sleep(1)
    
    print("\n" + "=" * 60)
    print("📊 FINAL REPORT")
    print("=" * 60)
    
    total_lives = sum(r["lives_saved"] for r in results)
    total_patients = sum(r["total_patients"] for r in results)
    overall_survival = total_lives / max(total_patients, 1)
    avg_score = sum(r["task_score"] for r in results) / len(results)
    
    for r in results:
        print(f"\n{r['difficulty'].upper()}:")
        print(f"   🟢 Survival: {r['survival_rate']:.1%}")
        print(f"   🟢 Task score: {r['task_score']:.3f}")
        print(f"   🟢 Lives saved: {r['lives_saved']}/{r['total_patients']}")
    
    print(f"\n{'='*60}")
    print(f"🎯 OVERALL PERFORMANCE")
    print(f"   Total lives saved: {total_lives}/{total_patients}")
    print(f"   Overall survival rate: {overall_survival:.1%}")
    print(f"   Average task score: {avg_score:.3f}")
    print(f"{'='*60}")
    
    with open("dispatch_results.json", "w") as f:
        json.dump({
            "report": results, 
            "total_lives_saved": total_lives,
            "overall_survival_rate": overall_survival,
            "average_task_score": avg_score
        }, f, indent=2)
    
    print("\n✅ Results saved to dispatch_results.json")
    print("\n🎉 Environment ready for submission!")


if __name__ == "__main__":
    main()