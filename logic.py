"""
logic.py
=============================================================================
Core business logic and data persistence helper for Dwellio (Python Flask).
Uses Python's built-in `json` module to read and write to `data.json`.
Beginner-friendly and easy to explain during college lab viva!
=============================================================================
"""

import json
import os
import time
from datetime import datetime

# Path to our local JSON database file
DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")


def load_data():
    """
    Reads data from data.json.
    Returns a dictionary with 'users' and 'listings' lists.
    """
    if not os.path.exists(DATA_FILE):
        # Default empty structure if file does not exist
        return {"users": [], "listings": []}

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Could not load {DATA_FILE}: {e}")
        return {"users": [], "listings": []}


def save_data(data):
    """
    Writes the Python dictionary back to data.json with indentation.
    """
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"[ERROR] Could not save to {DATA_FILE}: {e}")
        return False


# =============================================================================
# LISTINGS LOGIC (CRUD operations)
# =============================================================================

def get_all_listings(search_query=None):
    """
    Returns all listings.
    If search_query is provided, filters by title, location, country, or description.
    """
    data = load_data()
    listings = data.get("listings", [])

    if not search_query:
        return listings

    q = search_query.strip().lower()
    filtered = []
    for item in listings:
        title = item.get("title", "").lower()
        location = item.get("location", "").lower()
        country = item.get("country", "").lower()
        description = item.get("description", "").lower()

        if q in title or q in location or q in country or q in description:
            filtered.append(item)

    return filtered


def get_listing_by_id(listing_id):
    """
    Finds and returns a single listing by its string ID.
    Returns None if not found.
    """
    data = load_data()
    for item in data.get("listings", []):
        if str(item.get("_id")) == str(listing_id):
            return item
    return None


def create_listing(title, description, image, price, location, country, owner_user):
    """
    Creates a new listing, appends it to data.json, and returns the new listing object.
    """
    data = load_data()

    # Generate a unique ID using current timestamp
    new_id = str(int(time.time() * 1000))

    # Fallback image if user leaves it blank
    default_img = "https://images.unsplash.com/photo-1540555700478-4be289fbecef?auto=format&fit=crop&w=1200&q=80"
    clean_image = image.strip() if image and image.strip() else default_img

    try:
        clean_price = int(float(price))
    except (ValueError, TypeError):
        clean_price = 15000

    new_listing = {
        "_id": new_id,
        "title": title.strip(),
        "description": description.strip(),
        "image": clean_image,
        "price": clean_price,
        "location": location.strip(),
        "country": country.strip(),
        "owner": {
            "_id": owner_user.get("_id"),
            "username": owner_user.get("username"),
            "email": owner_user.get("email", "")
        },
        "reviews": []
    }

    data.setdefault("listings", []).append(new_listing)
    save_data(data)
    return new_listing


def update_listing(listing_id, title, description, image, price, location, country):
    """
    Updates an existing listing's fields in data.json.
    Returns updated listing dict or None if not found.
    """
    data = load_data()
    for item in data.get("listings", []):
        if str(item.get("_id")) == str(listing_id):
            if title:
                item["title"] = title.strip()
            if description:
                item["description"] = description.strip()
            if image and image.strip():
                item["image"] = image.strip()
            if price is not None:
                try:
                    item["price"] = int(float(price))
                except (ValueError, TypeError):
                    pass
            if location:
                item["location"] = location.strip()
            if country:
                item["country"] = country.strip()

            save_data(data)
            return item
    return None


def delete_listing(listing_id):
    """
    Deletes a listing by ID. Returns True if deleted, False if not found.
    """
    data = load_data()
    initial_len = len(data.get("listings", []))
    data["listings"] = [
        item for item in data.get("listings", [])
        if str(item.get("_id")) != str(listing_id)
    ]
    if len(data["listings"]) < initial_len:
        save_data(data)
        return True
    return False


# =============================================================================
# REVIEWS LOGIC
# =============================================================================

def add_review(listing_id, name, rating, description):
    """
    Appends a new review to the specified listing.
    """
    data = load_data()
    for item in data.get("listings", []):
        if str(item.get("_id")) == str(listing_id):
            rev_id = f"rev_{int(time.time() * 1000)}"
            try:
                r_num = int(rating)
                r_num = max(1, min(5, r_num))
            except (ValueError, TypeError):
                r_num = 5

            new_review = {
                "_id": rev_id,
                "name": name.strip(),
                "rating": r_num,
                "description": description.strip(),
                "createdAt": datetime.now().strftime("%b %d, %Y")
            }

            if "reviews" not in item or not isinstance(item["reviews"], list):
                item["reviews"] = []

            item["reviews"].append(new_review)
            save_data(data)
            return new_review
    return None


def delete_review(listing_id, review_id):
    """
    Removes a review from the specified listing.
    """
    data = load_data()
    for item in data.get("listings", []):
        if str(item.get("_id")) == str(listing_id):
            initial_count = len(item.get("reviews", []))
            item["reviews"] = [
                r for r in item.get("reviews", [])
                if str(r.get("_id")) != str(review_id)
            ]
            if len(item["reviews"]) < initial_count:
                save_data(data)
                return True
    return False


# =============================================================================
# USERS & AUTHENTICATION LOGIC
# =============================================================================

def find_user_by_username(username):
    """
    Finds a user by username (case-insensitive).
    """
    data = load_data()
    for u in data.get("users", []):
        if u.get("username", "").lower() == username.strip().lower():
            return u
    return None


def find_user_by_id(user_id):
    """
    Finds a user by ID.
    """
    data = load_data()
    for u in data.get("users", []):
        if str(u.get("_id")) == str(user_id):
            return u
    return None


def create_user(username, email, password):
    """
    Registers a new user in data.json.
    Returns (user_dict, None) on success, or (None, error_message) on failure.
    """
    data = load_data()
    clean_user = username.strip()
    clean_email = email.strip()

    # Check if username already exists
    if find_user_by_username(clean_user):
        return None, "Username already taken! Please choose another."

    # Check if email already exists
    for u in data.get("users", []):
        if u.get("email", "").lower() == clean_email.lower():
            return None, "An account with this email already exists!"

    user_id = f"user_{int(time.time() * 1000)}"
    new_user = {
        "_id": user_id,
        "username": clean_user,
        "email": clean_email,
        "password": password  # Simple plain-text or hashed password for student mini-project
    }

    data.setdefault("users", []).append(new_user)
    save_data(data)
    return new_user, None


def authenticate_user(username, password):
    """
    Validates username and password.
    Returns user dictionary if valid, otherwise None.
    """
    user = find_user_by_username(username)
    if user and user.get("password") == password:
        return user
    return None
