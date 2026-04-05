TASKS = {
    "easy": {
        "name": "easy",
        "days": 5,
        "max_energy": 10,
        "daily_target": 4.0,
        "decay_rate": 0.01,
        "consolidation_rate": 0.03,
        "spacing_target": 1,
        "subject_weights": {"math": 1.0, "physics": 1.0, "chemistry": 1.0},
        "deadline_day": 5,
        "deadline_pressure": 0.0,
        "initial_mastery": {"math": 0.25, "physics": 0.2, "chemistry": 0.3},
    },
    "medium": {
        "name": "medium",
        "days": 10,
        "max_energy": 10,
        "daily_target": 5.0,
        "decay_rate": 0.014,
        "consolidation_rate": 0.028,
        "spacing_target": 2,
        "subject_weights": {"math": 1.05, "physics": 1.0, "chemistry": 0.95},
        "deadline_day": 9,
        "deadline_pressure": 0.08,
        "initial_mastery": {"math": 0.2, "physics": 0.15, "chemistry": 0.25},
    },
    "hard": {
        "name": "hard",
        "days": 15,
        "max_energy": 10,
        "daily_target": 6.0,
        "decay_rate": 0.024,
        "consolidation_rate": 0.02,
        "spacing_target": 3,
        "subject_weights": {"math": 1.2, "physics": 1.05, "chemistry": 0.9},
        "deadline_day": 12,
        "deadline_pressure": 0.22,
        "initial_mastery": {"math": 0.1, "physics": 0.08, "chemistry": 0.12},
    },
}


def get_task_config(name):
    if name not in TASKS:
        available = ", ".join(sorted(TASKS))
        raise ValueError(f"Unknown task '{name}'. Available tasks: {available}")
    config = TASKS[name].copy()
    config["initial_mastery"] = TASKS[name]["initial_mastery"].copy()
    return config
