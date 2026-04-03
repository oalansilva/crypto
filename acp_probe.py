import json
import os
import subprocess
import threading
import queue
import time

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


def wait_for_json(q, timeout=15):
    deadline = time.time() + timeout
    stderr_lines = []
    while time.time() < deadline:
        remaining = max(0.1, deadline - time.time())
        try:
            label, line = q.get(timeout=remaining)
        except queue.Empty:
            continue

        if line is None:
            continue

        if label == "stderr":
            stderr_lines.append(line)
            print(f"[stderr] {line}")
            continue

        print(f"<<< {line}")
        try:
            return json.loads(line), stderr_lines
        except json.JSONDecodeError:
            print("Saída stdout não era JSON válido.")
            return {"_raw": line}, stderr_lines

    return None, stderr_lines


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
                    "name": "local-acp-probe",
                    "version": "0.1.0"
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

        resp1, _ = wait_for_json(q, timeout=20)
        print("\n=== RESULTADO initialize ===")
        print(json.dumps(resp1, indent=2, ensure_ascii=False))

        send(proc, {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "session/new",
            "params": {
                "cwd": os.getcwd(),
                "mcpServers": []
            }
        })

        resp2, _ = wait_for_json(q, timeout=30)
        print("\n=== RESULTADO session/new ===")
        print(json.dumps(resp2, indent=2, ensure_ascii=False))

        print("\n=== LEITURA RÁPIDA ===")
        if resp2 and "result" in resp2 and resp2["result"].get("sessionId"):
            print("OK: sessão criada. O agente aceitou a conexão sem pedir autenticação nesse ponto.")
        elif resp2 and "error" in resp2:
            code = resp2["error"].get("code")
            msg = resp2["error"].get("message")
            print(f"ERRO: code={code} message={msg}")
            if code == -32000:
                print("Interpretação: authentication required.")
        else:
            print("Sem resposta conclusiva.")

    finally:
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            proc.kill()


if __name__ == "__main__":
    main()
