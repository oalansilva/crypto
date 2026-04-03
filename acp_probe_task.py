import json
import os
import subprocess
import threading
import queue
import time
import sys

from acp_runtime import prepare_local_codex_home

CMD = ["codex-acp"]


def reader_thread(pipe, q, label):
    try:
        for line in iter(pipe.readline, ''):
            q.put((label, line.rstrip("\n")))
    finally:
        q.put((label, None))


def send(proc, obj):
    line = json.dumps(obj, ensure_ascii=False)
    print(f">>> {line}")
    proc.stdin.write(line + "\n")
    proc.stdin.flush()


def wait_for_response(q, expected_id, timeout=20):
    deadline = time.time() + timeout
    buffered = []
    while time.time() < deadline:
        remaining = max(0.1, deadline - time.time())
        try:
            label, line = q.get(timeout=remaining)
        except queue.Empty:
            continue

        if line is None:
            continue

        prefix = "<<<" if label == "stdout" else "[stderr]"
        print(f"{prefix} {line}")

        if label != "stdout":
            continue

        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            buffered.append({"_raw": line})
            continue

        buffered.append(obj)
        if obj.get("id") == expected_id:
            return obj, buffered

    return None, buffered


def collect_updates(q, seconds=20):
    deadline = time.time() + seconds
    messages = []
    while time.time() < deadline:
        remaining = max(0.1, deadline - time.time())
        try:
            label, line = q.get(timeout=remaining)
        except queue.Empty:
            continue

        if line is None:
            continue

        prefix = "<<<" if label == "stdout" else "[stderr]"
        print(f"{prefix} {line}")

        if label != "stdout":
            continue

        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            messages.append({"_raw": line})
            continue

        messages.append(obj)
    return messages


def main():
    env = os.environ.copy()
    env.pop("OPENAI_API_KEY", None)
    env.pop("CODEX_API_KEY", None)
    env.setdefault("RUST_LOG", "info")
    env["HOME"] = prepare_local_codex_home(os.getcwd())

    proc = subprocess.Popen(
        CMD,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        env=env,
    )

    q = queue.Queue()
    threading.Thread(target=reader_thread, args=(proc.stdout, q, "stdout"), daemon=True).start()
    threading.Thread(target=reader_thread, args=(proc.stderr, q, "stderr"), daemon=True).start()

    try:
        send(proc, {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": 1,
                "clientInfo": {
                    "name": "local-acp-task-probe",
                    "version": "0.2.0"
                },
                "clientCapabilities": {
                    "fs": {
                        "readTextFile": False,
                        "writeTextFile": False
                    },
                    "terminal": False
                }
            }
        })

        init_resp, _ = wait_for_response(q, expected_id=1, timeout=20)
        if not init_resp or "result" not in init_resp:
            print("Falha no initialize.")
            sys.exit(1)

        send(proc, {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "session/new",
            "params": {
                "cwd": os.getcwd(),
                "mcpServers": []
            }
        })

        session_resp, _ = wait_for_response(q, expected_id=2, timeout=30)
        if not session_resp or "result" not in session_resp:
            print("Falha no session/new.")
            sys.exit(1)

        session_id = session_resp["result"].get("sessionId")
        if not session_id:
            print("sessionId não encontrado.")
            print(json.dumps(session_resp, indent=2, ensure_ascii=False))
            sys.exit(1)

        print(f"\n=== SESSION ID: {session_id} ===\n")

        send(proc, {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "session/prompt",
            "params": {
                "sessionId": session_id,
                "prompt": [
                    {
                        "type": "text",
                        "text": "Liste os arquivos do diretório atual e resuma em 5 linhas o que parece ser este projeto."
                    }
                ]
            }
        })

        messages = collect_updates(q, seconds=20)

        final_text = ""
        errors = []

        for msg in messages:
            if msg.get("method") == "session/update":
                update = msg.get("params", {}).get("update", {})
                if update.get("sessionUpdate") == "agent_message_chunk":
                    content = update.get("content", {})
                    if content.get("type") == "text":
                        final_text += content.get("text", "")
            if msg.get("id") == 3 and "error" in msg:
                errors.append(msg["error"])

        print("\n=== TEXTO FINAL DO AGENTE ===")
        print(final_text if final_text else "(sem texto final)")

        if errors:
            print("\n=== ERROS ===")
            print(json.dumps(errors, indent=2, ensure_ascii=False))

    finally:
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            proc.kill()


if __name__ == "__main__":
    main()
