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
MUTATION_RE = re.compile(r"(?:>>|>|\btee\s+|sed\s+-i|perl\s+-i|\bcp\s+|\bmv\s+|\binstall\s+)")


def is_sidecar_path(path: str | None) -> bool:
    if not path:
        return False
    posix = path.replace("\\", "/").split("?")[0].rstrip("/")
    return posix.endswith(".design-digest")


def sidecar_in_command(command: str | None) -> bool:
    if not command or ".design-digest" not in command:
        return False
    return bool(MUTATION_RE.search(command)) or "Write" in command


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
