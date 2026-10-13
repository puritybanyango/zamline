# Owner: Jesca Amondi
# Feature: AI-assisted Cost Decision Support

import json
from datetime import datetime, timezone
from pathlib import Path

from config import (
    GEMINI_API_KEY,
    GEMINI_FILE_STATE_PATH,
    GEMINI_MODEL,
    GEMINI_REFERENCE_DIR,
)


class GeminiReferenceError(RuntimeError):
    pass


class GeminiReferenceManager:
    def __init__(self, client):
        self.client = client
        self.reference_dir = Path(GEMINI_REFERENCE_DIR)
        self.state_path = Path(GEMINI_FILE_STATE_PATH)

    def get_active_files(self) -> list:
        if not self.reference_dir.exists():
            return []

        state = self._load_state()
        active_files = []

        for path in sorted(self.reference_dir.glob("*.md")):
            key = path.name
            record = state.get(key)
            remote_file = None

            if record and record.get("name"):
                try:
                    remote_file = self.client.files.get(name=record["name"])
                except Exception:
                    remote_file = None

            if remote_file is None:
                try:
                    remote_file = self.client.files.upload(file=str(path))
                except Exception as error:
                    raise GeminiReferenceError(
                        f"Reference file refresh failed for {path.name}"
                    ) from error

                state[key] = {
                    "name": remote_file.name,
                    "uri": remote_file.uri,
                    "mime_type": remote_file.mime_type,
                    "uploaded_at": datetime.now(timezone.utc).isoformat(),
                }

            active_files.append(remote_file)

        self._save_state(state)
        return active_files

    def _load_state(self) -> dict:
        if not self.state_path.exists():
            return {}

        try:
            return json.loads(self.state_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}

    def _save_state(self, state: dict) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(
            json.dumps(state, indent=2, sort_keys=True),
            encoding="utf-8",
        )


def explain_cost_assessment(context: dict) -> str | None:
    if not GEMINI_API_KEY or not GEMINI_MODEL:
        return None

    from google import genai

    client = genai.Client(api_key=GEMINI_API_KEY)
    references = GeminiReferenceManager(client).get_active_files()

    prompt = (
        "Explain this freight cost assessment briefly for a fleet manager. "
        "Do not make an acceptance decision. Do not invent costs. "
        f"Assessment data: {json.dumps(context, default=str)}"
    )

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[prompt, *references],
        )
    except GeminiReferenceError:
        raise
    except Exception as error:
        raise RuntimeError("AI explanation could not be generated") from error

    return response.text
