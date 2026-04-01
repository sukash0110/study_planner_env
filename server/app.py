import os

import uvicorn

from study_env.api import app


def main():
    port = int(os.getenv("PORT", "8501"))
    uvicorn.run("study_env.api:app", host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
