def get_tools_schema():
    return [
        {
            "type": "function",
            "function": {
                "name": "create_menu_item",
                "description": "Create a new menu item in the database.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "The name of the item."},
                        "description": {"type": "string"},
                        "base_price": {"type": "number"},
                        "category_name": {"type": "string"}
                    },
                    "required": ["name", "base_price"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_menu_item",
                "description": "Update an existing menu item.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "item_id": {"type": "integer", "description": "The exact ID of the item in the database."},
                        "base_price": {"type": "number"},
                        "description": {"type": "string"},
                        "is_active": {"type": "boolean"}
                    },
                    "required": ["item_id"]
                }
            }
        }
    ]
