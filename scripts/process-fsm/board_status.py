"""Project 1 Status field ids and Shell classification. Not secrets."""

from __future__ import annotations

import re

STATUS_FIELD_ID = "PVTSSF_lAHOAAHtBM4BV8b2zhRUdMM"

STATUS_OPTIONS: dict[str, str] = {
    "Em Refinamento": "fed46e78",
    "Todo": "4c26ac72",
    "Design": "bd47fbe8",
    "Aprovação de Design": "b45bf4aa",
    "Pronto para Dev": "0257f58c",
    "Em desenvolvimento": "fe1ad960",
    "Code Review": "b1858de0",
    "QA": "9220bf8c",
    "Done": "e02597eb",
    "Homologado": "dfcb47b5",
    "Pronto": "8ca47888",
    "Cancelado": "ce5cd459",
}

STATUS_OPTION_IDS = frozenset(STATUS_OPTIONS.values())
PROCESS_EVENT_RE = re.compile(r"process-fsm/process_event\.py|\bprocess_event\.py\b")


def is_sidecar_path(path: str | None) -> bool:
    if not path:
        return False
    posix = path.replace("\\", "/").split("?")[0].rstrip("/")
    return posix.endswith(".design-digest")


def sidecar_mutation_in_command(command: str | None) -> bool:
    """True only when the shell command mutates a `.design-digest` path (card #631).

    Mere citation (`git add`/`commit`/`status`/`reset`, `ls`, `cat`) MUST be False.
    """
    if not command or ".design-digest" not in command:
        return False
    if re.search(r"(?:\d*)?(?:>>|>)\s*[^\s|;<>&]*\.design-digest\b", command):
        return True
    if re.search(r"\btee(?:\s+-a)?\s+[^\s|;<>&]*\.design-digest\b", command):
        return True
    if re.search(r"\b(?:rm|unlink|shred)\b[^\n]*\.design-digest\b", command):
        return True
    if re.search(r"\b(?:cp|mv|install)\b[^\n]*\.design-digest\b", command):
        return True
    if re.search(r"(?:sed\s+-i|perl\s+-i)[^\n]*\.design-digest\b", command):
        return True
    if re.search(r"\bpython3?\s+-c\b", command):
        if re.search(
            r"open\s*\([^)]*\.design-digest[^)]*['\"][wax+]+",
            command,
        ):
            return True
        if re.search(
            r"Path\s*\([^)]*\.design-digest[^)]*\)\s*\.\s*write_(?:text|bytes)\s*\(",
            command,
        ):
            return True
        if re.search(r"\.design-digest[^;]*\.write\s*\(", command):
            return True
    return False


def sidecar_in_command(command: str | None) -> bool:
    """Compat alias: sidecar deny only on mutation (#631)."""
    return sidecar_mutation_in_command(command)


def is_status_edit_command(command: str | None) -> bool:
    if not command:
        return False
    if "updateProjectV2ItemFieldValue" in command and STATUS_FIELD_ID in command:
        return True
    if "item-edit" not in command:
        return False
    if STATUS_FIELD_ID in command:
        return True
    return any(option_id in command for option_id in STATUS_OPTION_IDS)
