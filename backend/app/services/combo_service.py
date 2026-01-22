"""
Combo Strategy Service

Handles combo strategy instantiation, backtesting, and optimization.
All strategies are now loaded from database - no hard-coded Python classes.
"""

import sqlite3
import json
from typing import Dict, List, Any, Optional
from pathlib import Path

from app.strategies.combos import ComboStrategy


class ComboService:
    """Service for managing combo strategies (database-driven)."""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Get absolute path to database
            from pathlib import Path
            project_root = Path(__file__).parent.parent.parent
            db_path = str(project_root / "data" / "crypto_backtest.db")
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
        
        # Handle stop_loss if it's a dict with 'default' key
        if isinstance(stop_loss, dict):
            stop_loss = stop_loss.get("default", 0.015)
        
        # Apply parameter overrides if provided
        if parameters:
            # Update indicator parameters
            for ind in indicators:
                alias = ind.get("alias") or ind["type"]
                for key in list(ind["params"].keys()):
                    param_name = f"{alias}_{key}"
                    if param_name in parameters:
                        ind["params"][key] = parameters[param_name]
            
            # Override stop_loss if provided
            if "stop_loss" in parameters:
                stop_loss = parameters["stop_loss"]
        
        # Create and return strategy instance
        return ComboStrategy(
            indicators=indicators,
            entry_logic=entry_logic,
            exit_logic=exit_logic,
            stop_loss=stop_loss
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
