---
title: Student Study Planner
emoji: 📚
colorFrom: blue
colorTo: green
sdk: docker
app_port: 8501
pinned: false
license: mit
short_description: Streamlit study planner with energy-aware optimization.
---

# Student Study Planner with Energy, Balance, and Performance Optimization

An OpenEnv-style reinforcement learning environment where an agent must plan study actions across math, physics, and chemistry while managing fatigue, subject imbalance, and long-horizon performance.

## Preview

### Dashboard Screenshot

![Student Study Planner dashboard](assets/dashboard-preview.svg)

### Walkthrough GIF

![Student Study Planner walkthrough](assets/planner-walkthrough.svg)

## Why This Environment Matters

Real students do not just maximize raw study hours. They must:

- allocate time across competing subjects
- manage limited daily energy
- decide when to learn, reinforce, or recover
- avoid over-optimizing one subject while neglecting others

This makes study planning a strong real-world sequential decision problem. Short-term gains can hurt long-term performance if the policy ignores balance or recovery.

## What The Agent Controls

At every step, the agent chooses one of seven actions:

- `0`: study math
- `1`: study physics
- `2`: study chemistry
- `3`: revise math
- `4`: revise physics
- `5`: revise chemistry
- `6`: rest

Each episode spans multiple days, and each day contains three decision slots.

## Environment Design

The environment implements:

- `reset()`
- `step(action)` returning `(state, reward, done, info)`
- `state()`

Core simulation elements:

- three subjects with independent mastery values
- finite energy budget
- multi-day progression
- separate effects for studying, revising, and resting
- deterministic and stochastic execution modes

## Reward Design

The reward is intentionally multi-objective rather than a simple score delta.

It combines:

- average performance improvement
- balance across subjects
- energy efficiency
- targeted support for the weakest subject
- penalties for subject imbalance
- penalties for poor low-energy decisions
- mild penalties for wasteful rest actions

This encourages policies that make consistent progress without collapsing into one-subject optimization.

## Tasks

- `easy`: 5 days, lower mastery targets
- `medium`: 10 days, moderate planning horizon
- `hard`: 15 days, longer horizon with stronger balance demands

## Baseline Agent

The included baseline policy is deterministic by default and adapts to:

- current energy level
- weakest subject
- mastery imbalance

Behavior summary:

- rests when energy is critically low
- revises the weakest subject when imbalance becomes large
- studies the weakest subject when mastery is still behind
- stays reproducible for grading

## Grading Strategy

The grader evaluates the deterministic baseline on all three tasks and reports:

- total reward
- average mastery
- balance gap
- remaining energy
- step count
- pass/fail checks against explicit thresholds

This makes the benchmark easier to interpret in a hackathon review setting.

## Project Structure

```text
study_planner_env/
├── study_env/
│   ├── __init__.py
│   ├── env.py
│   ├── tasks.py
├── app.py
├── inference.py
├── grader.py
├── openenv.yaml
├── README.md
├── Dockerfile
└── requirements.txt
```

## Run Locally

CLI baseline:

```bash
python inference.py
```

Seeded stochastic run:

```bash
python inference.py --stochastic --seed 42
```

Different result every run:

```bash
python inference.py --randomize
```

Grader:

```bash
python grader.py
```

Streamlit UI:

```bash
streamlit run app.py
```

## Hugging Face Demo

Live Space:

[https://huggingface.co/spaces/sukash0110/study_planner_env](https://huggingface.co/spaces/sukash0110/study_planner_env)

This repo is configured as a Docker-based Hugging Face Space and serves the Streamlit dashboard on port `8501`.

## Environment Notes

- studying gives larger gains but consumes more energy
- revision improves one subject and lightly reinforces the others
- rest restores energy and supports sustainable planning
- deterministic mode is intended for reproducible evaluation
- stochastic and randomize modes are intended for exploratory analysis
