import pytest
import os
from app.data.db_store import db_store

def test_db_defaults_seeded():
    # Verify self profile
    profile_self = db_store.get_profile("self")
    assert profile_self["name"] == "Alex"
    assert "black color" in profile_self["likes"]
    assert "Cantabil brand" in profile_self["likes"]
    assert "high print" in profile_self["dislikes"]
    assert len(profile_self["purchases"]) > 0
    assert profile_self["sizing"]["top"] == "M"
    assert "grey jacket" in profile_self["wardrobe"]
    assert profile_self["shopping_goals"]["pieces_needed"] == 4
    assert profile_self["occupation"] == "developer"

    # Verify melisa profile
    profile_melisa = db_store.get_profile("melisa")
    assert profile_melisa["name"] == "Melisa"
    assert "linen material" in profile_melisa["likes"]
    assert "dark colors" in profile_melisa["dislikes"]
    assert "yellow sundress" in profile_melisa["wardrobe"]

def test_db_update_profiles():
    # Update size and preferences for a new recipient
    db_store.update_sizing("bob", {"top": "L", "bottom": "34"})
    db_store.add_preference("bob", "likes", "red color")
    db_store.add_preference("bob", "dislikes", "stripes")
    db_store.add_wardrobe_item("bob", "green hoodie")
    db_store.update_shopping_goals("bob", {"pieces_needed": 3, "vibe": "sporty"})
    db_store.update_occupation("bob", "teacher")

    profile_bob = db_store.get_profile("bob")
    assert profile_bob["sizing"]["top"] == "L"
    assert "red color" in profile_bob["likes"]
    assert "stripes" in profile_bob["dislikes"]
    assert "green hoodie" in profile_bob["wardrobe"]
    assert profile_bob["shopping_goals"]["pieces_needed"] == 3
    assert profile_bob["occupation"] == "teacher"
