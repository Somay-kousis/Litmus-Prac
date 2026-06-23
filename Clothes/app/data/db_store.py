import json
import os
from pathlib import Path
from typing import Dict, Any, List

DB_PATH = Path(__file__).resolve().parent / "db.json"

# Rich seed data matching standard commercial e-commerce customer profiles
DEFAULT_DB = {
    "profiles": {
        "self": {
            "name": "Alex",
            "relationship": "self",
            "sizing": {
                "top": "M",
                "bottom": "32",
                "shoes": "10",
                "height": "5'10\"",
                "fit_preference": "Slim"
            },
            "likes": [
                "black color", 
                "Cantabil brand", 
                "minimalist designs", 
                "cotton material",
                "oversized tees"
            ],
            "dislikes": [
                "high print", 
                "neon colors", 
                "polyester material"
            ],
            "clicks": ["c3", "c5"],
            "cart_history": [
                {"item_id": "c3", "name": "White Linen Shirt", "timestamp": "2026-06-23T10:00:00"}
            ],
            "purchases": [
                {"order_id": "ord_101", "item_id": "c1", "name": "Classic Denim Jacket", "category": "jacket"}
            ],
            "wardrobe": ["grey jacket", "black crewneck tee", "white sneakers"],
            "shopping_goals": {
                "pieces_needed": 4,
                "vibe": "minimalist"
            },
            "occupation": "developer"
        },
        "melisa": {
            "name": "Melisa",
            "relationship": "girlfriend",
            "sizing": {
                "top": "S",
                "bottom": "28",
                "shoes": "7",
                "height": "5'5\"",
                "fit_preference": "Regular"
            },
            "likes": [
                "linen material", 
                "white color", 
                "pastel tones", 
                "floral designs",
                "dresses"
            ],
            "dislikes": [
                "dark colors", 
                "heavy leather", 
                "baggy pants"
            ],
            "clicks": ["c3"],
            "cart_history": [],
            "purchases": [],
            "wardrobe": ["denim shorts", "yellow sundress"],
            "shopping_goals": {
                "pieces_needed": 3,
                "vibe": "romantic/pastel"
            },
            "occupation": "designer"
        }
    }
}

class DBStore:
    def __init__(self):
        self.db_dir = DB_PATH.parent
        self.db_dir.mkdir(parents=True, exist_ok=True)
        self.data = {}
        self.load()

    def load(self):
        if not DB_PATH.exists():
            self.data = DEFAULT_DB.copy()
            self.save()
        else:
            try:
                with open(DB_PATH, "r") as f:
                    self.data = json.load(f)
            except Exception:
                self.data = DEFAULT_DB.copy()
                self.save()

    def save(self):
        with open(DB_PATH, "w") as f:
            json.dump(self.data, f, indent=4)

    def get_profile(self, recipient: str) -> Dict[str, Any]:
        """Gets profile for the recipient. If it does not exist, initializes it."""
        recipient_key = recipient.lower().strip()
        
        # Normalize common relations
        if recipient_key in ["me", "myself", "self"]:
            recipient_key = "self"
            
        profiles = self.data.setdefault("profiles", {})
        if recipient_key not in profiles:
            profiles[recipient_key] = {
                "name": recipient.capitalize(),
                "relationship": recipient_key,
                "sizing": {},
                "likes": [],
                "dislikes": [],
                "clicks": [],
                "cart_history": [],
                "purchases": [],
                "wardrobe": [],
                "shopping_goals": {"pieces_needed": 0, "vibe": "unknown"},
                "occupation": "unknown"
            }
            self.save()
        return profiles[recipient_key]

    def add_preference(self, recipient: str, pref_type: str, item: str) -> None:
        """Appends a style item to 'likes' or 'dislikes' if not already present."""
        profile = self.get_profile(recipient)
        key = pref_type.lower().strip()  # 'likes' or 'dislikes'
        
        if key not in ["likes", "dislikes"]:
            return
            
        items_list = profile.setdefault(key, [])
        normalized_item = item.lower().strip()
        
        if normalized_item not in items_list:
            items_list.append(normalized_item)
            self.save()

    def add_click(self, recipient: str, item_id: str) -> None:
        """Logs click history."""
        profile = self.get_profile(recipient)
        clicks = profile.setdefault("clicks", [])
        if item_id not in clicks:
            clicks.append(item_id)
            self.save()
            
    def update_sizing(self, recipient: str, sizing_data: Dict[str, str]) -> None:
        """Updates sizing fields."""
        profile = self.get_profile(recipient)
        sizing = profile.setdefault("sizing", {})
        sizing.update(sizing_data)
        self.save()

    def add_wardrobe_item(self, recipient: str, item: str) -> None:
        """Adds a clothing item description the user already owns to their database wardrobe."""
        profile = self.get_profile(recipient)
        wardrobe = profile.setdefault("wardrobe", [])
        normalized_item = item.lower().strip()
        if normalized_item not in wardrobe:
            wardrobe.append(normalized_item)
            self.save()

    def update_shopping_goals(self, recipient: str, goals: Dict[str, Any]) -> None:
        """Updates shopping goals details."""
        profile = self.get_profile(recipient)
        goals_data = profile.setdefault("shopping_goals", {})
        goals_data.update(goals)
        self.save()

    def update_occupation(self, recipient: str, occupation: str) -> None:
        """Updates the user's occupation in database."""
        profile = self.get_profile(recipient)
        profile["occupation"] = occupation.lower().strip()
        self.save()

    def clear(self) -> None:
        """Reset database to default seed state (used for clean testing)."""
        import copy
        self.data = copy.deepcopy(DEFAULT_DB)
        self.save()

db_store = DBStore()
