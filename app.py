import base64
from pathlib import Path

import streamlit as st

from inference import run_episode
from study_env.env import StudyPlannerEnv
from study_env.tasks import TASKS


LOGO_PATH = "assets/edudynamics-logo.svg"
SUBJECT_COLORS = {
    "math": "#0f766e",
    "physics": "#1d4ed8",
    "chemistry": "#c2410c",
}
ACTION_LABELS = {
    0: "Study Math",
    1: "Study Physics",
    2: "Study Chemistry",
    3: "Revise Math",
    4: "Revise Physics",
    5: "Revise Chemistry",
    6: "Rest",
}


def inject_styles():
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(13, 148, 136, 0.18), transparent 28%),
                radial-gradient(circle at top right, rgba(29, 78, 216, 0.18), transparent 30%),
                linear-gradient(180deg, #f4f7f4 0%, #eef4ff 100%);
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        .hero {
            border: 1px solid rgba(15, 23, 42, 0.08);
            background: linear-gradient(135deg, rgba(255,255,255,0.96), rgba(239,246,255,0.92));
            border-radius: 24px;
            padding: 1.5rem 1.6rem;
            box-shadow: 0 16px 40px rgba(15, 23, 42, 0.08);
            margin-bottom: 1rem;
        }
        .hero-kicker {
            color: #0f766e;
            font-size: 0.84rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 0.4rem;
        }
        .hero-title {
            color: #0f172a;
            font-size: 2.2rem;
            line-height: 1.05;
            font-weight: 800;
            margin-bottom: 0.5rem;
        }
        .hero-copy {
            color: #334155;
            font-size: 1rem;
            line-height: 1.55;
            max-width: 48rem;
        }
        .panel {
            border: 1px solid rgba(15, 23, 42, 0.08);
            background: rgba(255, 255, 255, 0.82);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 1.1rem 1.2rem;
            box-shadow: 0 10px 28px rgba(15, 23, 42, 0.06);
        }
        .mini-label {
            color: #64748b;
            font-size: 0.8rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }
        .big-number {
            color: #0f172a;
            font-size: 2rem;
            font-weight: 800;
            line-height: 1.1;
            margin-top: 0.35rem;
        }
        .support-text {
            color: #475569;
            font-size: 0.92rem;
            margin-top: 0.25rem;
        }
        .subject-card {
            border-radius: 18px;
            padding: 1rem;
            color: white;
            min-height: 112px;
            box-shadow: 0 12px 24px rgba(15, 23, 42, 0.12);
        }
        .subject-name {
            font-size: 0.82rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            font-weight: 700;
            opacity: 0.9;
        }
        .subject-value {
            font-size: 2rem;
            font-weight: 800;
            margin-top: 0.25rem;
        }
        .subject-caption {
            font-size: 0.92rem;
            opacity: 0.9;
            margin-top: 0.35rem;
        }
        .logo-shell {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 14px;
            border-radius: 24px;
            background: linear-gradient(160deg, rgba(255, 255, 255, 0.96), rgba(232, 241, 255, 0.92));
            box-shadow: 0 14px 36px rgba(15, 23, 42, 0.22);
            border: 1px solid rgba(148, 163, 184, 0.26);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def build_trace_rows(trace):
    rows = []
    for item in trace:
        action = item["action"]
        rows.append(
            {
                "step": item["step"],
                "day": item["day"],
                "energy": item["energy"],
                "avg_mastery": item["avg_mastery"],
                "imbalance": item["imbalance"],
                "reward": item["reward"],
                "action_type": action["type"],
                "subject": action["subject"] or "all",
            }
        )
    return rows


def build_reward_rows(trace):
    rows = []
    for item in trace:
        row = {"step": item["step"]}
        row.update(item.get("reward_breakdown", {}))
        rows.append(row)
    return rows


def build_subject_rows(trace):
    rows = []
    for item in trace:
        row = {"step": item["step"]}
        row.update(item.get("mastery", {}))
        rows.append(row)
    return rows


def render_logo(width_px, framed=False):
    svg_text = Path(LOGO_PATH).read_text(encoding="utf-8")
    encoded = base64.b64encode(svg_text.encode("utf-8")).decode("utf-8")
    wrapper_class = "logo-shell" if framed else ""
    st.markdown(
        f"""
        <div style="display:flex; justify-content:center;">
            <div class="{wrapper_class}">
                <img src="data:image/svg+xml;base64,{encoded}" width="{width_px}" alt="EduDynamics logo" />
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_hero():
    logo_col, copy_col = st.columns([0.95, 3.05], vertical_alignment="center")
    with logo_col:
        render_logo(260)
    with copy_col:
        st.markdown(
            """
            <div class="hero">
                <div class="hero-kicker">EduDynamics 1.0.1</div>
                <div class="hero-title">Build sustainable study momentum across math, physics, and chemistry.</div>
                <div class="hero-copy">
                    Explore manual interventions, compare planning styles, and inspect how reward components evolve as the student balances progress, recovery, and subject coverage.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_metric_panels(summary):
    episode = summary["episode_summary"]
    cards = [
        ("Total Reward", summary["total_reward"], "Composite score across performance, balance, and energy use."),
        ("Average Mastery", episode.get("average_mastery"), "Final mastery averaged across all three subjects."),
        ("Balance Gap", episode.get("balance_gap"), "Lower is better. Zero means perfectly balanced learning."),
        ("Energy Left", episode.get("energy_left"), "Remaining energy at the end of the episode."),
    ]
    columns = st.columns(4)
    for column, (label, value, copy) in zip(columns, cards):
        column.markdown(
            f"""
            <div class="panel">
                <div class="mini-label">{label}</div>
                <div class="big-number">{value}</div>
                <div class="support-text">{copy}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_subject_cards(summary):
    mastery = summary["final_state"]["mastery"]
    avg_mastery = summary["episode_summary"]["average_mastery"]
    cols = st.columns(3)
    for col, subject in zip(cols, ("math", "physics", "chemistry")):
        value = mastery[subject]
        color = SUBJECT_COLORS[subject]
        delta = round(value - avg_mastery, 4)
        caption = "Above plan average" if delta >= 0 else "Below plan average"
        col.markdown(
            f"""
            <div class="subject-card" style="background: linear-gradient(160deg, {color}, rgba(15, 23, 42, 0.92));">
                <div class="subject-name">{subject}</div>
                <div class="subject-value">{value:.4f}</div>
                <div class="subject-caption">{caption}: {delta:+.4f}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_plan_snapshot(summary):
    final_state = summary["final_state"]
    mode_label = "randomized" if final_state["seed"] is None else ("stochastic" if summary["stochastic"] else "deterministic")
    seed_label = "auto-generated" if final_state["seed"] is None else final_state["seed"]

    left, right = st.columns([1.05, 1.2])
    with left:
        st.markdown("### Run Snapshot")
        st.markdown(
            f"""
            <div class="panel">
                <div class="mini-label">Scenario</div>
                <div class="support-text">
                    Task: <strong>{summary["task"]}</strong><br>
                    Agent: <strong>{summary.get("agent_mode", "heuristic")}</strong><br>
                    Mode: <strong>{mode_label}</strong><br>
                    Seed: <strong>{seed_label}</strong><br>
                    Steps executed: <strong>{summary["steps"]}</strong>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("")
        st.progress(min(final_state["energy_ratio"], 1.0), text=f"Final energy ratio: {final_state['energy_ratio']:.0%}")
        st.progress(
            min(summary["episode_summary"]["average_mastery"], 1.0),
            text=f"Average mastery reached: {summary['episode_summary']['average_mastery']:.0%}",
        )
    with right:
        st.markdown("### Reward Design")
        st.markdown(
            """
            <div class="panel">
                <div class="support-text">
                    EduDynamics 1.0.1 exposes the reward composition more clearly:
                    <br><br>
                    <strong>Performance</strong> rewards mastery gains.
                    <br>
                    <strong>Balance</strong> favors even subject coverage.
                    <br>
                    <strong>Energy efficiency</strong> rewards progress per unit of effort.
                    <br>
                    <strong>Penalties</strong> discourage imbalance and poor recovery choices.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_analytics(summary):
    rows = build_trace_rows(summary["trace"])
    reward_rows = build_reward_rows(summary["trace"])
    subject_rows = build_subject_rows(summary["trace"])

    st.markdown("### Analytics")
    chart_cols = st.columns(3)
    with chart_cols[0]:
        st.markdown("**Energy trajectory**")
        st.line_chart([{"step": row["step"], "energy": row["energy"]} for row in rows], x="step", y="energy")
    with chart_cols[1]:
        st.markdown("**Average mastery**")
        st.line_chart([{"step": row["step"], "avg_mastery": row["avg_mastery"]} for row in rows], x="step", y="avg_mastery")
    with chart_cols[2]:
        st.markdown("**Reward by step**")
        st.bar_chart([{"step": row["step"], "reward": row["reward"]} for row in rows], x="step", y="reward")

    lower_cols = st.columns(2)
    with lower_cols[0]:
        st.markdown("**Reward component breakdown**")
        if reward_rows:
            st.area_chart(reward_rows, x="step")
    with lower_cols[1]:
        st.markdown("**Subject mastery over time**")
        if subject_rows:
            st.line_chart(subject_rows, x="step")

    view = st.segmented_control("Trace view", options=["Recent", "Full"], default="Recent", selection_mode="single")
    if view == "Recent":
        st.dataframe(rows[-8:], use_container_width=True, hide_index=True)
    else:
        st.dataframe(rows, use_container_width=True, hide_index=True, height=360)


def ensure_manual_state(task_name, stochastic, seed):
    config = {"task_name": task_name, "stochastic": stochastic, "seed": seed}
    if st.session_state.get("manual_config") != config:
        env = StudyPlannerEnv(task_name=task_name, stochastic=stochastic, seed=seed)
        observation = env.reset()
        st.session_state.manual_env = env
        st.session_state.manual_obs = observation
        st.session_state.manual_done = False
        st.session_state.manual_history = []
        st.session_state.manual_config = config


def render_manual_lab(task_name, stochastic, seed):
    ensure_manual_state(task_name, stochastic, seed)
    env = st.session_state.manual_env
    observation = st.session_state.manual_obs
    done = st.session_state.manual_done

    st.markdown("### Manual Simulation Lab")
    control_cols = st.columns([1.2, 1, 1])
    with control_cols[0]:
        chosen_action = st.selectbox("Choose next action", options=list(ACTION_LABELS.keys()), format_func=lambda x: ACTION_LABELS[x])
    with control_cols[1]:
        step_clicked = st.button("Apply Action", use_container_width=True, disabled=done)
    with control_cols[2]:
        reset_clicked = st.button("Reset Manual Lab", use_container_width=True)

    if reset_clicked:
        st.session_state.manual_config = None
        ensure_manual_state(task_name, stochastic, seed)
        env = st.session_state.manual_env
        observation = st.session_state.manual_obs
        done = st.session_state.manual_done

    if step_clicked and not done:
        next_obs, reward, done, info = env.step(chosen_action)
        st.session_state.manual_obs = next_obs
        st.session_state.manual_done = done
        st.session_state.manual_history.append(
            {
                "step": len(st.session_state.manual_history) + 1,
                "action": ACTION_LABELS[chosen_action],
                "reward": reward,
                "day": next_obs["day"],
                "energy": next_obs["energy"],
                "avg_mastery": next_obs["avg_mastery"],
                "imbalance": next_obs["imbalance"],
                "reward_breakdown": info.get("reward_breakdown", {}),
            }
        )
        observation = next_obs

    top_cols = st.columns(4)
    top_cols[0].metric("Day", observation["day"])
    top_cols[1].metric("Energy", observation["energy"])
    top_cols[2].metric("Average Mastery", observation["avg_mastery"])
    top_cols[3].metric("Imbalance", observation["imbalance"])

    mastery_cols = st.columns(3)
    for col, subject in zip(mastery_cols, ("math", "physics", "chemistry")):
        col.metric(subject.title(), observation["mastery"][subject])

    if st.session_state.manual_history:
        last = st.session_state.manual_history[-1]
        st.markdown("**Latest reward breakdown**")
        component_rows = [{"component": key, "value": value} for key, value in last["reward_breakdown"].items()]
        st.bar_chart(component_rows, x="component", y="value")
        st.dataframe(st.session_state.manual_history, use_container_width=True, hide_index=True, height=240)
    else:
        st.info("Step through the environment manually to inspect reward components and state transitions.")


def render_compare(task_name):
    st.markdown("### Agent Comparison")
    compare_col1, compare_col2 = st.columns(2)
    heuristic_summary = run_episode(task_name, stochastic=False, seed=123, agent_mode="heuristic")

    with compare_col1:
        st.markdown("**Heuristic baseline**")
        st.metric("Total Reward", heuristic_summary["total_reward"])
        st.metric("Average Mastery", heuristic_summary["episode_summary"]["average_mastery"])
        st.metric("Balance Gap", heuristic_summary["episode_summary"]["balance_gap"])

    with compare_col2:
        st.markdown("**OpenAI-ready baseline**")
        if st.secrets.get("OPENAI_API_KEY", None) or st.session_state.get("has_openai_key") or st.session_state.get("openai_key_hint"):
            st.info("OpenAI baseline can be executed when OPENAI_API_KEY is configured in the environment.")
        else:
            st.info("Set OPENAI_API_KEY to run the OpenAI baseline. The app keeps the deterministic baseline available for offline usage.")

    comparison_rows = [
        {
            "agent": "heuristic",
            "total_reward": heuristic_summary["total_reward"],
            "average_mastery": heuristic_summary["episode_summary"]["average_mastery"],
            "balance_gap": heuristic_summary["episode_summary"]["balance_gap"],
            "energy_left": heuristic_summary["episode_summary"]["energy_left"],
            "steps": heuristic_summary["steps"],
        }
    ]
    st.dataframe(comparison_rows, use_container_width=True, hide_index=True)


def main():
    st.set_page_config(page_title="EduDynamics", page_icon="📚", layout="wide")
    inject_styles()
    render_hero()

    with st.sidebar:
        render_logo(132, framed=True)
        st.markdown("### EduDynamics")
        st.caption("Energy-aware student planning simulator")
        st.markdown("---")
        st.markdown("## Simulation Controls")
        st.caption("Configure the planner, then run a full episode.")
        task_name = st.selectbox("Task difficulty", options=list(TASKS.keys()), index=1)
        mode = st.radio("Execution mode", options=["deterministic", "stochastic", "randomize"], index=0)
        seed = st.number_input("Seed", min_value=0, value=123, step=1, disabled=(mode == "randomize"))
        st.markdown("---")
        task = TASKS[task_name]
        st.markdown(
            f"""
            **Task profile**

            - Days: `{task['days']}`
            - Daily target: `{task['daily_target']}`
            - Max energy: `{task['max_energy']}`
            """
        )
        run_clicked = st.button("Run Simulation", type="primary", use_container_width=True)

    if "summary" not in st.session_state:
        st.session_state.summary = None
    if "manual_config" not in st.session_state:
        st.session_state.manual_config = None

    stochastic = mode in {"stochastic", "randomize"}
    actual_seed = None if mode == "randomize" else int(seed)

    if run_clicked:
        st.session_state.summary = run_episode(task_name, stochastic=stochastic, seed=actual_seed, agent_mode="heuristic")

    summary = st.session_state.summary
    if summary is None:
        st.info("Pick a task profile and run the planner to open the 1.0.1 analytics workspace.")
        return

    render_metric_panels(summary)
    st.markdown("")
    render_subject_cards(summary)
    st.markdown("")
    render_plan_snapshot(summary)

    overview_tab, manual_tab, compare_tab = st.tabs(["Overview", "Manual Lab", "Compare"])
    with overview_tab:
        render_analytics(summary)
    with manual_tab:
        render_manual_lab(task_name, stochastic, actual_seed)
    with compare_tab:
        render_compare(task_name)


if __name__ == "__main__":
    main()
