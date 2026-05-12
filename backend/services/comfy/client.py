"""
ComfyUI WebSocket + HTTP Client
Handles: queue prompt → wait for completion → download & save outputs.
"""

import json
import time
import uuid
import logging
import urllib.request
import urllib.parse
import urllib.error
import os
from pathlib import Path

import websocket

log = logging.getLogger("aimos.comfy_client")

# How long to wait between connection retries
_RETRY_DELAY = 3
_MAX_RETRIES = 5


class ComfyClient:
    def __init__(self, server_address: str = "127.0.0.1:8188"):
        self.server_address = server_address
        self.base_url = f"http://{server_address}"
        self.ws_url   = f"ws://{server_address}"
        self.client_id = str(uuid.uuid4())

    # ── Connection helpers ───────────────────────────────────

    def ping(self) -> bool:
        """Return True if ComfyUI is reachable."""
        try:
            urllib.request.urlopen(f"{self.base_url}/system_stats", timeout=3)
            return True
        except Exception:
            return False

    def _connect_ws(self) -> websocket.WebSocket:
        ws = websocket.WebSocket()
        ws.connect(
            f"{self.ws_url}/ws?clientId={self.client_id}",
            timeout=120,
        )
        return ws

    # ── API calls ────────────────────────────────────────────

    def queue_prompt(self, prompt: dict) -> str:
        """Submit a workflow prompt and return the prompt_id."""
        payload = json.dumps({"prompt": prompt, "client_id": self.client_id}).encode()
        req = urllib.request.Request(
            f"{self.base_url}/prompt",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read())
                return data["prompt_id"]
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            raise RuntimeError(f"ComfyUI queue_prompt failed ({e.code}): {body}") from e

    def get_history(self, prompt_id: str) -> dict:
        url = f"{self.base_url}/history/{prompt_id}"
        with urllib.request.urlopen(url, timeout=15) as resp:
            return json.loads(resp.read())

    def get_file(self, filename: str, subfolder: str, folder_type: str) -> bytes:
        params = urllib.parse.urlencode({
            "filename": filename,
            "subfolder": subfolder,
            "type": folder_type,
        })
        with urllib.request.urlopen(f"{self.base_url}/view?{params}", timeout=60) as resp:
            return resp.read()

    # ── Wait for completion ──────────────────────────────────

    def wait_for_completion(self, prompt_id: str) -> dict:
        """
        Opens a WebSocket and blocks until the queued prompt finishes.
        Returns the history entry for that prompt_id.
        """
        ws = self._connect_ws()
        try:
            while True:
                raw = ws.recv()
                if not isinstance(raw, str):
                    continue
                msg = json.loads(raw)
                if msg.get("type") == "executing":
                    data = msg.get("data", {})
                    if data.get("node") is None and data.get("prompt_id") == prompt_id:
                        log.info(f"Prompt {prompt_id} completed.")
                        break
                elif msg.get("type") == "execution_error":
                    data = msg.get("data", {})
                    raise RuntimeError(
                        f"ComfyUI execution error on node {data.get('node_id')}: "
                        f"{data.get('exception_message')}"
                    )
        finally:
            ws.close()

        history = self.get_history(prompt_id)
        return history.get(prompt_id, {})

    # ── High-level: submit + collect outputs ─────────────────

    def process_workflow(self, workflow: dict, output_dir: str) -> list[str]:
        """
        Submit workflow → wait → download all output files → save to output_dir.
        Returns list of absolute file paths.
        """
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Retry queue in case ComfyUI is momentarily busy
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                prompt_id = self.queue_prompt(workflow)
                log.info(f"Queued prompt {prompt_id} (attempt {attempt})")
                break
            except Exception as e:
                if attempt == _MAX_RETRIES:
                    raise
                log.warning(f"Queue failed ({e}), retrying in {_RETRY_DELAY}s…")
                time.sleep(_RETRY_DELAY)

        history = self.wait_for_completion(prompt_id)
        saved = []

        outputs = history.get("outputs", {})
        for node_id, node_output in outputs.items():
            # Images (PNG / JPEG)
            for img in node_output.get("images", []):
                data = self.get_file(img["filename"], img.get("subfolder", ""), img["type"])
                dest = os.path.join(output_dir, img["filename"])
                with open(dest, "wb") as f:
                    f.write(data)
                saved.append(dest)
                log.info(f"Saved image → {dest}")

            # Videos (MP4 via VHS_VideoCombine returns 'gifs' key with mp4 format)
            for vid in node_output.get("gifs", []):
                data = self.get_file(vid["filename"], vid.get("subfolder", ""), vid["type"])
                dest = os.path.join(output_dir, vid["filename"])
                with open(dest, "wb") as f:
                    f.write(data)
                saved.append(dest)
                log.info(f"Saved video → {dest}")

        if not saved:
            raise RuntimeError("ComfyUI returned no output files. Check ComfyUI logs.")

        return saved
