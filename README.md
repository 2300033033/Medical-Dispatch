---
title: Emergency Medical Dispatch
emoji: 🚑
colorFrom: red
colorTo: blue
sdk: docker
pinned: false
---

# 🚑 Emergency Medical Dispatch Environment

An AI training environment for 911 emergency medical dispatch. The agent learns to prioritize emergencies, dispatch ambulances, and provide life-saving instructions.

## Real-World Impact

Every year, 350,000 Americans have cardiac arrest outside hospitals. Only 10% survive because ambulances take too long. This AI could save thousands of lives by optimizing dispatch decisions.

## Three Difficulty Levels

| Level | Emergencies | Ambulances | Challenge |
|-------|-------------|------------|-----------|
| 🟢 Easy | 2 | 2 | Send closest ambulance to highest priority |
| 🟡 Medium | 4 | 3 | Balance resources, prioritize correctly |
| 🔴 Hard | 6 | 4 (1 busy) | Maximize survival under pressure |

## Emergency Types

- **Cardiac Arrest** - Dies in 6 minutes, needs CPR
- **Stroke** - 60-minute window
- **Choking** - Dies in 5 minutes
- **Breathing Difficulty** - 15-minute window
- **Seizure** - 20-minute window
- **Broken Bone** - Can wait 2 hours

## Run Locally

```bash
pip install -r requirements.txt
python inference.py