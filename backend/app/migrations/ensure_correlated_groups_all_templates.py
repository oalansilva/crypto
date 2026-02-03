"""
Migration: Ensure all combo templates use optimization_schema.correlated_groups.

Goal (user request):
- All templates should use the "correlated_groups" option (nested optimization_schema),
  similar to the newer multi_ma_crossoverV2 approach.
- Do NOT change multi_ma_crossover and multi_ma_crossoverV2 (they are working).

What this migration does (idempotent):
- For every template in combo_templates (prebuilt, examples, and custom),
  excluding the two protected templates:
  - Normalize optimization_schema to the nested format:
      {"parameters": <dict>, "correlated_groups": <list[list[str]]>}
  - If correlated_groups is missing/empty/invalid, it generates reasonable groups:
      - Groups for MACD/MA/BB/RSI/ATR parameters (when multiple exist)
      - Any remaining parameters are added as singleton groups
  - If correlated_groups exists, it is cleaned to:
      - remove unknown params
      - remove empty groups
      - prevent duplicates across groups
      - add missing params as singleton groups

Notes:
- This migration only updates optimization_schema JSON; it does not alter template_data.
- It avoids grid-explosion by defaulting to singleton groups for unknown params.
"""

import json
import re
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


PROTECTED_TEMPLATES = {"multi_ma_crossover", "multi_ma_crossoverV2"}


def _get_db_path(db_path: Optional[str] = None) -> str:
    if db_path:
        return db_path
    try:
        from app.database import DB_PATH
        return str(DB_PATH)
    except Exception:
        return str(Path(__file__).resolve().parent.parent.parent / "backtest.db")


def _flatten_parameters(schema: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Accept both flat and nested schema formats and return a dict of parameters only.
    """
    if not isinstance(schema, dict):
        return {}
    if isinstance(schema.get("parameters"), dict):
        return schema["parameters"]

    # Flat format: top-level keys are params (ignore metadata keys if present)
    out: Dict[str, Any] = {}
    for k, v in schema.items():
        if k in ("parameters", "correlated_groups"):
            continue
        out[k] = v
    return out


def _normalize_existing_groups(groups: Any, params: Dict[str, Any]) -> List[List[str]]:
    """
    Clean and normalize correlated_groups:
    - keep only param names that exist
    - remove empty groups
    - dedupe across groups
    - add missing params as singleton groups
    """
    if not isinstance(groups, list):
        groups = []

    used = set()
    cleaned: List[List[str]] = []
    for g in groups:
        if not isinstance(g, list):
            continue
        g2: List[str] = []
        for p in g:
            if not isinstance(p, str):
                continue
            if p not in params:
                continue
            if p in used:
                continue
            used.add(p)
            g2.append(p)
        if g2:
            cleaned.append(g2)

    # Add missing params as singleton groups (keeps behavior stable and avoids huge cartesian products)
    for p in params.keys():
        if p not in used:
            cleaned.append([p])
            used.add(p)

    return cleaned


def _auto_groups(params: Dict[str, Any]) -> List[List[str]]:
    """
    Generate correlated_groups heuristically from parameter names.
    We keep it conservative:
    - Group only when we find 2+ params of the same "family"
    - Remaining params become singleton groups
    """
    keys = list(params.keys())
    used = set()
    groups: List[List[str]] = []

    def take(match_fn) -> List[str]:
        picked = []
        for k in keys:
            if k in used:
                continue
            if match_fn(k):
                picked.append(k)
        for k in picked:
            used.add(k)
        return picked

    # Families
    macd = take(lambda k: k.lower().startswith("macd_"))
    bb = take(lambda k: k.lower().startswith("bb_") or k.lower().startswith("bollinger_") or "bband" in k.lower())
    ma = take(lambda k: bool(re.match(r"^(ema|sma|wma|hma|rma|ma)_", k.lower())) or "media" in k.lower())
    rsi = take(lambda k: k.lower().startswith("rsi_"))
    atr = take(lambda k: k.lower().startswith("atr_"))

    stop = None
    if "stop_loss" in params and "stop_loss" not in used:
        stop = "stop_loss"
        used.add(stop)

    # Build groups (only if meaningful)
    if macd and len(macd) >= 2:
        groups.append(macd)
    elif macd:
        # single MACD param -> keep singleton
        for k in macd:
            groups.append([k])

    if bb and len(bb) >= 2:
        groups.append(bb)
    elif bb:
        for k in bb:
            groups.append([k])

    if ma and len(ma) >= 2:
        groups.append(ma)
    elif ma:
        for k in ma:
            groups.append([k])

    if rsi and len(rsi) >= 2:
        groups.append(rsi)
    elif rsi:
        for k in rsi:
            groups.append([k])

    if atr and len(atr) >= 2:
        groups.append(atr)
    elif atr:
        for k in atr:
            groups.append([k])

    # Attach stop_loss to the most "structural" group if we have one; otherwise singleton.
    if stop is not None:
        if groups:
            groups[0].append(stop)
        else:
            groups.append([stop])

    # Remaining params as singleton groups
    for k in keys:
        if k in used:
            continue
        groups.append([k])
        used.add(k)

    # Ensure non-empty
    if not groups and keys:
        groups = [[keys[0]]]

    return groups


def _build_new_schema(schema: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    params = _flatten_parameters(schema)

    existing_groups = None
    if isinstance(schema, dict):
        existing_groups = schema.get("correlated_groups")

    if existing_groups:
        groups = _normalize_existing_groups(existing_groups, params)
    else:
        groups = _auto_groups(params)
        groups = _normalize_existing_groups(groups, params)

    return {"parameters": params, "correlated_groups": groups}


def _derive_parameters_from_template_data(template_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Build a parameters dict from legacy template_data structures, used mainly by example templates
    that store ranges inside indicators (optimization_range) instead of optimization_schema.
    """
    if not isinstance(template_data, dict):
        return {}

    out: Dict[str, Any] = {}

    # stop_loss range (legacy examples store it as dict with default + optimization_range)
    sl = template_data.get("stop_loss")
    if isinstance(sl, dict):
        default = sl.get("default")
        rng = sl.get("optimization_range")
        if isinstance(rng, dict) and ("min" in rng or "start" in rng):
            cfg = {k: rng.get(k) for k in ("min", "max", "step") if rng.get(k) is not None}
            if default is not None:
                cfg["default"] = default
            if cfg:
                out["stop_loss"] = cfg

    # indicator ranges
    indicators = template_data.get("indicators") or []
    if not isinstance(indicators, list):
        return out

    for ind in indicators:
        if not isinstance(ind, dict):
            continue
        ind_type = str(ind.get("type", "")).lower().strip()
        if not ind_type:
            continue
        alias = ind.get("alias")
        params = ind.get("params") or {}
        opt_range = ind.get("optimization_range")

        # If optimization_range is a direct range dict (min/max/step), assume it's for the main period param.
        if isinstance(opt_range, dict) and ("min" in opt_range or "start" in opt_range):
            # Find main period param key
            main_key = None
            if isinstance(params, dict):
                if "length" in params:
                    main_key = "length"
                elif "period" in params:
                    main_key = "period"
            if main_key is None:
                # Heuristic defaults by type
                if ind_type in ("ema", "sma", "rsi", "adx", "atr", "volume_sma"):
                    main_key = "length"

            if main_key:
                # Naming convention:
                # - if alias exists: use type_alias (e.g., ema_fast, sma_long)
                # - else: use type_param (e.g., ema_length, rsi_length)
                if alias:
                    p_name = f"{ind_type}_{alias}"
                else:
                    p_name = f"{ind_type}_{main_key}"
                cfg = {k: opt_range.get(k) for k in ("min", "max", "step") if opt_range.get(k) is not None}
                if isinstance(params, dict) and params.get(main_key) is not None:
                    cfg["default"] = params.get(main_key)
                if cfg:
                    out[p_name] = cfg

        # If optimization_range is a dict of param_name -> range, extract them as alias_param
        elif isinstance(opt_range, dict):
            if not isinstance(params, dict):
                continue
            for param_key, rng in opt_range.items():
                if not isinstance(rng, dict) or ("min" not in rng and "start" not in rng):
                    continue
                if alias:
                    p_name = f"{alias}_{param_key}"
                else:
                    p_name = f"{ind_type}_{param_key}"
                cfg = {k: rng.get(k) for k in ("min", "max", "step") if rng.get(k) is not None}
                if params.get(param_key) is not None:
                    cfg["default"] = params.get(param_key)
                if cfg:
                    out[p_name] = cfg

    return out


def ensure_correlated_groups_all_templates(db_path: Optional[str] = None) -> Tuple[int, int]:
    """
    Returns: (updated_count, skipped_count)
    """
    path = _get_db_path(db_path)
    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    cursor.execute("SELECT name, template_data, optimization_schema FROM combo_templates")
    rows = cursor.fetchall()

    updated = 0
    skipped = 0
    for name, template_json, schema_json in rows:
        if name in PROTECTED_TEMPLATES:
            skipped += 1
            continue

        old_schema = None
        if schema_json:
            try:
                old_schema = json.loads(schema_json)
            except Exception:
                old_schema = None

        # If schema is missing/empty, try to derive parameters from template_data (legacy examples).
        old_params = _flatten_parameters(old_schema)
        if not old_params:
            template_data = None
            if template_json:
                try:
                    template_data = json.loads(template_json)
                except Exception:
                    template_data = None
            derived = _derive_parameters_from_template_data(template_data)
            if derived:
                old_schema = {"parameters": derived, "correlated_groups": []}

        new_schema = _build_new_schema(old_schema)

        # Idempotency check: avoid rewriting when already normalized and equal.
        if isinstance(old_schema, dict) and old_schema.get("parameters") == new_schema.get("parameters") and old_schema.get("correlated_groups") == new_schema.get("correlated_groups"):
            skipped += 1
            continue

        cursor.execute(
            "UPDATE combo_templates SET optimization_schema = ?, updated_at = CURRENT_TIMESTAMP WHERE name = ?",
            (json.dumps(new_schema), name),
        )
        if cursor.rowcount > 0:
            updated += 1

    conn.commit()
    conn.close()
    return updated, skipped


def run_migration():
    print("Running migration: ensure correlated_groups on all templates (excluding protected ones)...")
    updated, skipped = ensure_correlated_groups_all_templates()
    print(f"Done. Updated={updated}, Skipped={skipped}")


if __name__ == "__main__":
    run_migration()

