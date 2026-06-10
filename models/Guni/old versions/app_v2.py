import streamlit as st
import subprocess

st.title("Euskadi Events Assistant")

question = st.text_input("Ask a question")

if st.button("Send") and question:

    result = subprocess.run(
        ["python3", "API_LLM_original_v2.py", question],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        st.markdown(result.stdout)
    else:
        st.error(result.stderr)
