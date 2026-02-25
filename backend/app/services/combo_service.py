"""
Combo Strategy Service

Handles combo strategy instantiation, backtesting, and optimization.
All strategies are now loaded from database - no hard-coded Python classes.
"""

import sqlite3
import json
import re
from typing import Dict, List, Any, Optional
from pathlib import Path

from app.strategies.combos import ComboStrategy


class ComboService:
    """Service for managing combo strategies (database-driven)."""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Use the canonical DB path from app.database
            from app.database import DB_PATH
            db_path = str(DB_PATH)
        self.db_path = db_path
    
    def list_templates(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        List all available combo templates from database.
        
        Returns:
            Dict with prebuilt, examples, and custom templates
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get pre-built templates from database
        cursor.execute("""
            SELECT name, description, is_readonly
            FROM combo_templates
            WHERE is_prebuilt = 1
        """)
        prebuilt = [
            {"name": row[0], "description": row[1] or "", "is_readonly": bool(row[2])}
            for row in cursor.fetchall()
        ]
        
        # Get example templates from database
        cursor.execute("""
            SELECT name, description, is_readonly
            FROM combo_templates
            WHERE is_example = 1
        """)
        examples = [
            {"name": row[0], "description": row[1] or "", "is_readonly": bool(row[2])}
            for row in cursor.fetchall()
        ]
        
        # Get custom templates from database
        cursor.execute("""
            SELECT name, description, is_readonly
            FROM combo_templates
            WHERE is_example = 0 AND is_prebuilt = 0
        """)
        custom = [
            {"name": row[0], "description": row[1] or "", "is_readonly": bool(row[2])}
            for row in cursor.fetchall()
        ]
        
        conn.close()
        
        return {
            "prebuilt": prebuilt,
            "examples": examples,
            "custom": custom
        }
    
    def get_template_metadata(self, template_name: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a specific template from database.
        
        Args:
            template_name: Name of the template
        
        Returns:
            Template metadata or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
           SELECT name, description, is_example, is_prebuilt, template_data, optimization_schema, is_readonly
            FROM combo_templates
            WHERE name = ?
        """, (template_name,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            template_data = json.loads(row[4])
            optimization_schema = json.loads(row[5]) if row[5] else None
            
            # Normalize stop_loss to always be a dict for Pydantic validation
            stop_loss = template_data.get("stop_loss", 0.015)
            if not isinstance(stop_loss, dict):
                template_data["stop_loss"] = {"default": stop_loss}
            
            return {
                "name": row[0],
                "description": row[1] or "",
                "is_example": bool(row[2]),
                "is_prebuilt": bool(row[3]),
                "is_readonly": bool(row[6]),
                "optimization_schema": optimization_schema,
                **template_data
            }
        
        return None
    
    def create_strategy(
        self,
        template_name: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> ComboStrategy:
        """
        Create a combo strategy instance from database configuration.
        
        Args:
            template_name: Name of the template
            parameters: Optional parameter overrides
        
        Returns:
            ComboStrategy instance
        """
        # Load template metadata from database
        metadata = self.get_template_metadata(template_name)
        if not metadata:
            raise ValueError(f"Template '{template_name}' not found")
        
        # Extract template data
        indicators = metadata["indicators"]
        entry_logic = metadata["entry_logic"]
        exit_logic = metadata["exit_logic"]
        stop_loss = metadata.get("stop_loss", 0.015)
        derived_features = metadata.get("derived_features")
        
        # Handle stop_loss if it's a dict with 'default' key
        if isinstance(stop_loss, dict):
            stop_loss = stop_loss.get("default", 0.015)
        
        # Apply parameter overrides if provided
        if parameters:
            # Update indicator parameters
            for ind in indicators:
                alias = ind.get("alias") or ind["type"]
                ind_type = ind.get("type", "").lower()
                
                for key in list(ind["params"].keys()):
                    # 1. Standard "alias_key" format (e.g. "short_length")
                    param_name_std = f"{alias}_{key}"
                    
                    # 2. Optimization "type_alias" format (e.g. "sma_short" implies length/period)
                    # This is how strategies like multi_ma_crossover are defined in seed
                    param_name_opt = f"{ind_type}_{alias}"
                    
                    if param_name_std in parameters:
                        ind["params"][key] = parameters[param_name_std]
                    
                    # Special handling for common main parameters (length, period) keys matching optimization schema keys
                    elif key in ["length", "period"] and param_name_opt in parameters:
                         ind["params"][key] = parameters[param_name_opt]
            
            # Override stop_loss if provided
            if "stop_loss" in parameters:
                stop_loss = parameters["stop_loss"]
        
        # Create and return strategy instance
        return ComboStrategy(
            indicators=indicators,
            entry_logic=entry_logic,
            exit_logic=exit_logic,
            stop_loss=stop_loss,
            derived_features=derived_features
        )
    
    def save_template(
        self,
        name: str,
        description: str,
        indicators: List[Dict[str, Any]],
        entry_logic: str,
        exit_logic: str,
        stop_loss: float = 0.015,
        is_example: bool = False,
        is_prebuilt: bool = False,
        optimization_schema: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Save a new combo template to database.
        
        Args:
            name: Template name
            description: Template description
            indicators: List of indicator configurations
            entry_logic: Entry condition logic string
            exit_logic: Exit condition logic string
            stop_loss: Default stop loss percentage
            is_example: Whether this is an example template
            is_prebuilt: Whether this is a pre-built template
            optimization_schema: Optional optimization ranges
        
        Returns:
            ID of the saved template
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build template data JSON
        template_data = {
            "indicators": indicators,
            "entry_logic": entry_logic,
            "exit_logic": exit_logic,
            "stop_loss": stop_loss
        }
        
        # Insert template
        cursor.execute("""
            INSERT INTO combo_templates (
                name, description, is_example, is_prebuilt,
                template_data, optimization_schema
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            name,
            description,
            is_example,
            is_prebuilt,
            json.dumps(template_data),
            json.dumps(optimization_schema) if optimization_schema else None
        ))
        
        template_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return template_id

    def _normalize_stop_loss_value(self, stop_loss: Any) -> float:
        """Normalize stop loss into a positive decimal float."""
        if isinstance(stop_loss, dict):
            stop_loss = stop_loss.get("default")

        if isinstance(stop_loss, str):
            raw = stop_loss.strip()
            if not raw:
                return 0.03
            has_percent = raw.endswith("%")
            raw = raw.rstrip("%").strip()
            try:
                value = float(raw)
            except ValueError:
                return 0.03
            if has_percent or value >= 1:
                value = value / 100.0
            return float(value) if value > 0 else 0.03

        if isinstance(stop_loss, (int, float)):
            value = float(stop_loss)
            if value >= 1:
                value = value / 100.0
            return float(value) if value > 0 else 0.03

        return 0.03

    def _normalize_indicator(self, indicator: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Normalize indicator payload from either template_data or strategy_draft formats."""
        if not isinstance(indicator, dict):
            return None

        indicator_type = indicator.get("type") or indicator.get("name")
        if not indicator_type:
            return None

        alias = indicator.get("alias") or indicator_type
        params = indicator.get("params")
        if not isinstance(params, dict):
            params = {}

        return {
            "type": str(indicator_type).lower(),
            "alias": str(alias).lower(),
            "params": params,
        }

    def _normalize_template_data(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize template data for persistence."""
        if not isinstance(template_data, dict):
            raise ValueError("Invalid template data: expected object.")

        normalized_indicators: List[Dict[str, Any]] = []
        raw_indicators = template_data.get("indicators")
        if isinstance(raw_indicators, list):
            for indicator in raw_indicators:
                normalized = self._normalize_indicator(indicator)
                if normalized is not None:
                    normalized_indicators.append(normalized)

        entry_logic = str(template_data.get("entry_logic") or "").strip()
        exit_logic = str(template_data.get("exit_logic") or "").strip()
        stop_loss = self._normalize_stop_loss_value(template_data.get("stop_loss"))

        missing_fields: List[str] = []
        if not normalized_indicators:
            missing_fields.append("indicators")
        if not entry_logic:
            missing_fields.append("entry_logic")
        if not exit_logic:
            missing_fields.append("exit_logic")

        if missing_fields:
            fields = ", ".join(missing_fields)
            raise ValueError(f"Invalid template data: missing required field(s): {fields}.")

        return {
            "indicators": normalized_indicators,
            "entry_logic": entry_logic,
            "exit_logic": exit_logic,
            "stop_loss": stop_loss,
        }

    def _build_template_data_from_strategy_draft(self, strategy_draft: Dict[str, Any]) -> Dict[str, Any]:
        """Map strategy draft format into normalized template_data."""
        if not isinstance(strategy_draft, dict):
            raise ValueError("Invalid strategy draft: expected object.")

        indicators = strategy_draft.get("indicators")
        entry_logic = strategy_draft.get("entry_logic") or strategy_draft.get("entry_idea") or ""
        exit_logic = strategy_draft.get("exit_logic") or strategy_draft.get("exit_idea") or ""

        stop_loss = strategy_draft.get("stop_loss")
        if stop_loss is None:
            risk_plan = strategy_draft.get("risk_plan")
            if isinstance(risk_plan, str):
                match = re.search(r"stop[_\-\s]*loss[:\s]*(\d+(?:\.\d+)?)\s*%?", risk_plan, re.IGNORECASE)
                if match:
                    stop_loss = float(match.group(1))

        return self._normalize_template_data(
            {
                "indicators": indicators if isinstance(indicators, list) else [],
                "entry_logic": entry_logic,
                "exit_logic": exit_logic,
                "stop_loss": stop_loss,
            }
        )

    def create_template(
        self,
        *,
        name: str,
        template_data: Optional[Dict[str, Any]] = None,
        category: str = "custom",
        metadata: Optional[Dict[str, Any]] = None,
        strategy_draft: Optional[Dict[str, Any]] = None,
        description: str = "",
    ) -> Dict[str, Any]:
        """
        Create and persist a combo template.

        Supports both:
        - direct template_data payload
        - strategy_draft payload (mapped to template_data)
        """
        template_name = str(name or "").strip()
        if not template_name:
            raise ValueError("Invalid template data: missing required field(s): name.")

        normalized_template_data = (
            self._normalize_template_data(template_data)
            if template_data is not None
            else self._build_template_data_from_strategy_draft(strategy_draft)
        )

        category_norm = str(category or "custom").strip().lower()
        is_example = category_norm == "example"
        is_prebuilt = category_norm == "prebuilt"

        template_description = str(description or "").strip()
        if not template_description and isinstance(metadata, dict):
            one_liner = metadata.get("one_liner")
            if isinstance(one_liner, str):
                template_description = one_liner.strip()

        try:
            template_id = self.save_template(
                name=template_name,
                description=template_description,
                indicators=normalized_template_data["indicators"],
                entry_logic=normalized_template_data["entry_logic"],
                exit_logic=normalized_template_data["exit_logic"],
                stop_loss=normalized_template_data["stop_loss"],
                is_example=is_example,
                is_prebuilt=is_prebuilt,
                optimization_schema=None,
            )
        except sqlite3.IntegrityError as exc:
            raise ValueError(f"Template '{template_name}' already exists.") from exc

        saved = self.get_template_metadata(template_name) or {
            "name": template_name,
            "description": template_description,
            **normalized_template_data,
        }
        saved["id"] = template_id
        saved["category"] = category_norm
        if isinstance(metadata, dict):
            saved["metadata"] = metadata

        return saved

    def create_template(
        self,
        name: str,
        template_data: Dict[str, Any],
        category: str = "custom",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create and persist a combo template from normalized template data.

        Args:
            name: Template name
            template_data: Dict with indicators, entry_logic, exit_logic, stop_loss
            category: custom | example | prebuilt
            metadata: Optional metadata used for description/response

        Returns:
            Saved template metadata

        Raises:
            ValueError: If required fields are missing or invalid
        """
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Template creation failed: missing required field 'name'")
        template_name = name.strip()

        if not isinstance(template_data, dict):
            raise ValueError("Template creation failed: 'template_data' must be an object")

        if self.get_template_metadata(template_name):
            raise ValueError(f"Template creation failed: template '{template_name}' already exists")

        raw_indicators = template_data.get("indicators")
        entry_logic = template_data.get("entry_logic")
        exit_logic = template_data.get("exit_logic")
        stop_loss_raw = template_data.get("stop_loss", 0.03)

        if not isinstance(raw_indicators, list) or not raw_indicators:
            raise ValueError("Template creation failed: missing required field 'indicators'")
        if not isinstance(entry_logic, str) or not entry_logic.strip():
            raise ValueError("Template creation failed: missing required field 'entry_logic'")
        if not isinstance(exit_logic, str) or not exit_logic.strip():
            raise ValueError("Template creation failed: missing required field 'exit_logic'")

        indicators: List[Dict[str, Any]] = []
        for idx, ind in enumerate(raw_indicators):
            if not isinstance(ind, dict):
                raise ValueError(f"Template creation failed: indicator at index {idx} must be an object")

            ind_type = ind.get("type") or ind.get("name")
            if not ind_type:
                raise ValueError(f"Template creation failed: indicator at index {idx} missing 'type'")

            params = ind.get("params")
            if params is None:
                params = {}
            if not isinstance(params, dict):
                raise ValueError(f"Template creation failed: indicator params at index {idx} must be an object")

            alias = ind.get("alias") or ind_type
            indicators.append(
                {
                    "type": str(ind_type).lower(),
                    "alias": str(alias).lower(),
                    "params": params,
                }
            )

        if isinstance(stop_loss_raw, dict):
            stop_loss_raw = stop_loss_raw.get("default", 0.03)
        if stop_loss_raw is None:
            stop_loss_raw = 0.03
        try:
            stop_loss = float(stop_loss_raw)
        except (TypeError, ValueError) as exc:
            raise ValueError("Template creation failed: 'stop_loss' must be numeric") from exc

        normalized_category = (category or "custom").strip().lower()
        if normalized_category not in {"custom", "example", "prebuilt"}:
            raise ValueError(
                f"Template creation failed: unsupported category '{category}'. "
                "Use custom, example, or prebuilt."
            )

        metadata_dict = metadata if isinstance(metadata, dict) else {}
        description = (
            metadata_dict.get("description")
            or metadata_dict.get("one_liner")
            or template_data.get("description")
            or ""
        )
        if not isinstance(description, str):
            description = str(description)

        self.save_template(
            name=template_name,
            description=description.strip(),
            indicators=indicators,
            entry_logic=entry_logic.strip(),
            exit_logic=exit_logic.strip(),
            stop_loss=stop_loss,
            is_example=(normalized_category == "example"),
            is_prebuilt=(normalized_category == "prebuilt"),
        )

        saved = self.get_template_metadata(template_name)
        if not saved:
            raise RuntimeError(f"Template creation failed: unable to load saved template '{template_name}'")

        saved["category"] = normalized_category
        saved["metadata"] = metadata_dict
        return saved
    
    def update_template_schema(
        self,
        template_name: str,
        optimization_schema: Dict[str, Any]
    ) -> bool:
        """
        Update the optimization schema for a template.
        
        Args:
            template_name: Name of the template
            optimization_schema: New optimization schema
        
        Returns:
            True if update was successful
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE combo_templates
            SET optimization_schema = ?, updated_at = CURRENT_TIMESTAMP
            WHERE name = ?
        """, (json.dumps(optimization_schema), template_name))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def delete_template(self, template_id: int) -> bool:
        """
        Delete a custom template from database.
        
        Args:
            template_id: ID of the template to delete
        
        Returns:
            True if deletion was successful
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Only allow deleting custom templates (not prebuilt or examples)
        cursor.execute("""
            DELETE FROM combo_templates
            WHERE id = ? AND is_example = 0 AND is_prebuilt = 0
        """, (template_id,))
        
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return deleted
    
    def delete_template_by_name(self, template_name: str) -> bool:
        """
        Delete a custom template from database by name.
        
        Args:
            template_name: Name of the template to delete
        
        Returns:
            True if deletion was successful
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Only allow deleting custom templates (not prebuilt or examples)
        cursor.execute("""
            DELETE FROM combo_templates
            WHERE name = ? AND is_example = 0 AND is_prebuilt = 0
        """, (template_name,))
        
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return deleted
    
    def update_template(
        self,
        template_name: str,
        description: Optional[str] = None,
        optimization_schema: Optional[Dict[str, Any]] = None,
        template_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update a combo template's metadata and optimization schema.
        
        Args:
            template_name: Name of the template to update
            description: New description (optional)
            optimization_schema: New optimization schema (optional)
            template_data: Full template data for advanced editing (optional)
        
        Returns:
            True if update was successful, False otherwise
        
        Raises:
            ValueError: If template is read-only or doesn't exist
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if template exists and is not read-only
        cursor.execute("""
            SELECT is_readonly, template_data, optimization_schema
            FROM combo_templates
            WHERE name = ?
        """, (template_name,))
        
        row = cursor.fetchone()
        if not row:
            conn.close()
            raise ValueError(f"Template '{template_name}' not found")
        
        if row[0]:  # is_readonly
            conn.close()
            raise ValueError(f"Template '{template_name}' is read-only. Clone it to make changes.")
        
        # Build update query dynamically based on what's provided
        updates = []
        params = []
        
        if description is not None:
            updates.append("description = ?")
            params.append(description)
        
        if optimization_schema is not None:
            # Validate optimization schema
            self._validate_optimization_schema(optimization_schema)
            updates.append("optimization_schema = ?")
            params.append(json.dumps(optimization_schema))
        
        if template_data is not None:
            # Merge with existing template_data if only partial update
            existing_data = json.loads(row[1])
            merged_data = {**existing_data, **template_data}
            updates.append("template_data = ?")
            params.append(json.dumps(merged_data))
        
        if not updates:
            conn.close()
            return True  # Nothing to update
        
        # Add updated_at timestamp
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(template_name)
        
        query = f"UPDATE combo_templates SET {', '.join(updates)} WHERE name = ?"
        cursor.execute(query, params)
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def clone_template(self, template_name: str, new_name: str) -> Optional[Dict[str, Any]]:
        """
        Clone an existing template with a new name.
        
        Args:
            template_name: Name of the template to clone
            new_name: Name for the cloned template
        
        Returns:
            Metadata of the cloned template, or None if failed
        
        Raises:
            ValueError: If source template doesn't exist or new name already exists
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if source template exists
        cursor.execute("""
            SELECT description, template_data, optimization_schema
            FROM combo_templates
            WHERE name = ?
        """, (template_name,))
        
        source = cursor.fetchone()
        if not source:
            conn.close()
            raise ValueError(f"Source template '{template_name}' not found")
        
        # Check if new name already exists
        cursor.execute("SELECT 1 FROM combo_templates WHERE name = ?", (new_name,))
        if cursor.fetchone():
            conn.close()
            raise ValueError(f"Template '{new_name}' already exists")
        
        # Insert cloned template (always as custom, editable template)
        cursor.execute("""
            INSERT INTO combo_templates (
                name, description, is_example, is_prebuilt, is_readonly,
                template_data, optimization_schema
            ) VALUES (?, ?, 0, 0, 0, ?, ?)
        """, (new_name, source[0], source[1], source[2]))
        
        conn.commit()
        conn.close()
        
        # Return metadata of cloned template
        return self.get_template_metadata(new_name)
    
    def _validate_optimization_schema(self, schema: Dict[str, Any]) -> None:
        """
        Validate optimization schema structure and values.
        
        Args:
            schema: Optimization schema to validate
        
        Raises:
            ValueError: If schema is invalid
        """
        # Handle both flat and nested schema formats
        params = schema.get('parameters', schema)
        
        for param_name, config in params.items():
            if param_name in ['parameters', 'correlated_groups']:
                continue  # Skip metadata keys
            
            if not isinstance(config, dict):
                continue
            
            min_val = config.get('min')
            max_val = config.get('max')
            step_val = config.get('step')
            
            # Validate min < max
            if min_val is not None and max_val is not None:
                if min_val >= max_val:
                    raise ValueError(f"Parameter '{param_name}': min ({min_val}) must be less than max ({max_val})")
            
            # Validate step > 0
            if step_val is not None:
                if step_val <= 0:
                    raise ValueError(f"Parameter '{param_name}': step ({step_val}) must be greater than 0")
                
                # Validate step <= (max - min)
                if min_val is not None and max_val is not None:
                    if step_val > (max_val - min_val):
                        raise ValueError(f"Parameter '{param_name}': step ({step_val}) must be <= (max - min) = {max_val - min_val}")
