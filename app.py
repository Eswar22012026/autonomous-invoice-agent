
import subprocess
import sys
from pathlib import Path

import streamlit as st

PROJECT_DIR = Path(__file__).resolve().parent
AGENT_FILE = PROJECT_DIR / "agent.py"

st.set_page_config(
    page_title="Autonomous Invoice Agent",
    page_icon="📄",
    layout="centered",
)

st.title("📄 Autonomous Invoice Processing Agent")

st.write(
    "Enter a task and let the agent process a local invoice, "
    "validate its information, and report the result."
)

st.info(
    "This prototype uses local invoice files and a simulated "
    "company system. It does not connect to a real accounting platform."
)

task = st.text_input(
    "What should the agent do?",
    placeholder="Process the invoice from ABC Technologies",
)

approve = st.checkbox(
    "Approve saving the invoice if validation succeeds"
)

if st.button("Run Invoice Agent", type="primary"):
    if not task.strip():
        st.warning("Please enter a task.")

    elif not AGENT_FILE.exists():
        st.error("agent.py was not found.")

    else:
        approval = "yes" if approve else "no"
        agent_input = f"{task.strip()}\n{approval}\n"

        with st.spinner("Running the invoice agent..."):
            try:
                result = subprocess.run(
                    [sys.executable, str(AGENT_FILE)],
                    input=agent_input,
                    capture_output=True,
                    text=True,
                    cwd=str(PROJECT_DIR),
                    timeout=300,
                    check=False,
                )

                if result.stdout:
                    st.text_area(
                        "Agent execution output",
                        result.stdout,
                        height=400,
                    )

                if result.stderr:
                    with st.expander("Technical details"):
                        st.code(result.stderr)

                if result.returncode == 0:
                    st.success("Agent process finished.")
                else:
                    st.error(
                        f"Agent exited with code {result.returncode}."
                    )

            except subprocess.TimeoutExpired:
                st.error(
                    "The agent exceeded the 5-minute time limit. "
                    "Check the API connection and try again."
                )

            except Exception as error:
                st.error(
                    f"Could not run agent: {type(error).__name__}"
                )

st.divider()
st.caption("CentrAlign AI take-home project | Local prototype")
