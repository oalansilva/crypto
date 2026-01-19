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
    
    def list_templates(self) -> Dict[str, List[Dict[str, str]]]:
        """
        List all available combo templates from database.
        
        Returns:
            Dict with prebuilt, examples, and custom templates
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get pre-built templates from database
        cursor.execute("""
            SELECT name, description
            FROM combo_templates
            WHERE is_prebuilt = 1
        """)
        prebuilt = [
            {"name": row[0], "description": row[1] or ""}
            for row in cursor.fetchall()
        ]
        
        # Get example templates from database
        cursor.execute("""
            SELECT name, description
            FROM combo_templates
            WHERE is_example = 1
        """)
        examples = [
            {"name": row[0], "description": row[1] or ""}
            for row in cursor.fetchall()
        ]
        
        # Get custom templates from database
        cursor.execute("""
            SELECT name, description
            FROM combo_templates
            WHERE is_example = 0 AND is_prebuilt = 0
        """)
        custom = [
            {"name": row[0], "description": row[1] or ""}
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
            SELECT name, description, is_example, is_prebuilt, template_data, optimization_schema
            FROM combo_templates
            WHERE name = ?
        """, (template_name,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            template_data = json.loads(row[4])
            optimization_schema = json.loads(row[5]) if row[5] else None
            
            return {
                "name": row[0],
                "description": row[1] or "",
                "is_example": bool(row[2]),
                "is_prebuilt": bool(row[3]),
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
            for indicator in indicators:
                param_name = indicator.get("alias") or indicator["type"]
                if param_name in parameters:
                    indicator["params"].update(parameters[param_name])
            
            # Update stop_loss if provided
            if "stop_loss" in parameters:
                stop_loss = parameters["stop_loss"]
        
        # Create ComboStrategy from metadata
        return ComboStrategy(
            indicators=indicators,
            entry_logic=entry_logic,
            exit_logic=exit_logic,
            stop_loss=stop_loss
        )
    
    def save_custom_template(
        self,
        name: str,
        description: str,
        indicators: List[Dict[str, Any]],
        entry_logic: str,
        exit_logic: str,
        stop_loss: Dict[str, Any]
    ) -> int:
        """
        Save a custom template to the database.
        
        Args:
            name: Template name
            description: Template description
            indicators: List of indicator configs
            entry_logic: Entry logic expression
            exit_logic: Exit logic expression
            stop_loss: Stop loss configuration
        
        Returns:
            Template ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        template_data = {
            "indicators": indicators,
            "entry_logic": entry_logic,
            "exit_logic": exit_logic,
            "stop_loss": stop_loss
        }
        
        cursor.execute("""
            INSERT INTO combo_templates (name, description, is_example, is_prebuilt, template_data)
            VALUES (?, ?, 0, 0, ?)
        """, (name, description, json.dumps(template_data)))
        
        template_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return template_id
    
    def delete_custom_template(self, template_id: int) -> bool:
        """
        Delete a custom template.
        
        Args:
            template_id: Template ID
        
        Returns:
            True if deleted, False otherwise
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
