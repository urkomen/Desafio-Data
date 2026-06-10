from flask import Flask
import subprocess

app = Flask(__name__)


def run_script(question: str) -> str:
    result = subprocess.run(
        ["python3", "API_LLM_original.py", question],
        capture_output=True,
        text=True
    )

    # If script fails, return error output
    if result.returncode != 0:
        return f"ERROR:\n{result.stderr}"

    return result.stdout


@app.route("/")
def home():
    return {
        "status": "ok",
        "message": "API is running",
        "usage": "http://127.0.0.1:5000/<question>"
    }


@app.route("/<path:question>")
def ask(question):
    output = run_script(question)
    return output, 200, {"Content-Type": "text/plain; charset=utf-8"}


if __name__ == "__main__":
    print("🚀 Flask API running at http://127.0.0.1:5000/")
    app.run(host="0.0.0.0", port=5000, debug=True)