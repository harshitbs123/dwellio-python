"""
=============================================================================
Dwellio - Luxury Stays & Architecture
Backend: Python Flask (Migrated from Express/Node.js)
Database: Local JSON Storage via logic.py (Zero Database Setup Required)
=============================================================================
This backend is written cleanly and straightforwardly without complex ORMs
or decorators so it can be easily understood and explained during college viva!
"""

import os
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    jsonify,
    send_from_directory,
    get_flashed_messages
)

# Import our simple helper functions from logic.py
import logic

# 1. Initialize Flask Application
app = Flask(__name__, static_folder="static", template_folder="templates")

# Secret key required for Flask session management & flash messages
app.secret_key = "dwellio_college_mini_project_secret_key"


# =============================================================================
# TEMPLATE HELPERS & CONTEXT PROCESSORS
# =============================================================================

@app.template_filter("inr")
def format_inr(value):
    """
    Custom Jinja filter to format numbers in Indian currency style (e.g. 18,500).
    Usage in templates: {{ listing.price|inr }}
    """
    try:
        val = int(float(value))
        return f"{val:,}"
    except (ValueError, TypeError):
        return str(value)


@app.context_processor
def inject_global_template_data():
    """
    Injects global variables into all Jinja templates automatically.
    - currUser: Current logged-in user dictionary or None
    - success: Array of success flash messages (e.g., success[0])
    - error: Array of error flash messages (e.g., error[0])
    """
    curr_user = None
    if "user_id" in session:
        curr_user = {
            "_id": session.get("user_id"),
            "username": session.get("username"),
            "email": session.get("email", "")
        }

    # Fetch flash messages categorized as 'success' and 'error'
    messages = get_flashed_messages(with_categories=True)
    success_msgs = [msg for cat, msg in messages if cat == "success"]
    error_msgs = [msg for cat, msg in messages if cat in ("error", "danger")]

    return {
        "currUser": curr_user,
        "success": success_msgs,
        "error": error_msgs
    }


# =============================================================================
# STATIC ASSETS FALLBACK ROUTES
# (Ensures all images, css, js, fonts load smoothly under any relative path)
# =============================================================================

@app.route("/assets/<path:filename>")
def serve_assets(filename):
    return send_from_directory(app.static_folder, filename)


@app.route("/css/<path:filename>")
def serve_css(filename):
    return send_from_directory(os.path.join(app.static_folder, "css"), filename)


@app.route("/js/<path:filename>")
def serve_js(filename):
    return send_from_directory(os.path.join(app.static_folder, "js"), filename)


@app.route("/fonts/<path:filename>")
def serve_fonts(filename):
    return send_from_directory(os.path.join(app.static_folder, "fonts"), filename)


@app.route("/logo.png")
def serve_logo():
    return send_from_directory(app.static_folder, "logo.png")


# =============================================================================
# AUTHENTICATION HELPER FUNCTIONS (Simple checks without complex decorators)
# =============================================================================

def get_current_user():
    """Returns current user dict from session or None."""
    if "user_id" in session:
        return {
            "_id": session.get("user_id"),
            "username": session.get("username"),
            "email": session.get("email", "")
        }
    return None


def is_authenticated():
    """Checks if a user is currently logged in."""
    return "user_id" in session


# =============================================================================
# WEB ROUTES: HOME & LISTINGS
# =============================================================================

@app.route("/")
def index():
    """Home / Landing page: displays featured luxury stays."""
    all_listings = logic.get_all_listings()
    return render_template("landing.html", listings=all_listings)


@app.route("/listings", methods=["GET"])
def listings_index():
    """Explore page: displays all listings with search and category filtering."""
    search = request.args.get("search", "").strip()
    filtered_listings = logic.get_all_listings(search if search else None)
    return render_template("listings/listings.html", listings=filtered_listings, search=search)


@app.route("/listings/host", methods=["GET"])
def host_new_listing():
    """Renders form to add a new listing. Requires user login."""
    if not is_authenticated():
        session["redirect_url"] = request.path
        flash("You must be logged in to host or manage a property!", "error")
        return redirect("/login")
    return render_template("listings/host.html")


@app.route("/listings", methods=["POST"])
def create_listing_route():
    """Processes form submission to create a new property listing."""
    if not is_authenticated():
        flash("You must be logged in to create a listing!", "error")
        return redirect("/login")

    # Read form inputs (supports both listing[field] and field format)
    title = request.form.get("listing[title]") or request.form.get("title", "")
    description = request.form.get("listing[description]") or request.form.get("description", "")
    image = request.form.get("listing[image]") or request.form.get("image", "")
    price = request.form.get("listing[price]") or request.form.get("price", 15000)
    location = request.form.get("listing[location]") or request.form.get("location", "")
    country = request.form.get("listing[country]") or request.form.get("country", "")

    owner_user = get_current_user()
    new_listing = logic.create_listing(
        title=title,
        description=description,
        image=image,
        price=price,
        location=location,
        country=country,
        owner_user=owner_user
    )

    flash("Listing successfully created!", "success")
    return redirect(f"/listings/{new_listing['_id']}")


@app.route("/listings/<listing_id>", methods=["GET", "POST", "PATCH", "PUT", "DELETE"])
def show_or_modify_listing(listing_id):
    """
    Multi-purpose route handling:
    1. GET: Show listing details
    2. POST with _method=PATCH or PUT: Update listing
    3. POST with _method=DELETE or DELETE: Remove listing
    """
    listing = logic.get_listing_by_id(listing_id)
    if not listing:
        return render_template("errors/404Cast.html"), 404

    # Determine method override (from query parameter or form field)
    override_method = (
        request.args.get("_method", "").upper()
        or request.form.get("_method", "").upper()
        or request.method
    )

    # --- DELETE ACTION ---
    if override_method == "DELETE":
        if not is_authenticated():
            flash("You must be logged in!", "error")
            return redirect("/login")

        curr_user = get_current_user()
        owner = listing.get("owner", {})
        if str(owner.get("_id")) != str(curr_user.get("_id")) and owner.get("username") != curr_user.get("username"):
            flash("You do not have permission to delete this listing!", "error")
            return redirect(f"/listings/{listing_id}")

        logic.delete_listing(listing_id)
        flash("Listing successfully deleted!", "success")
        return redirect("/listings")

    # --- UPDATE (PATCH / PUT / POST edit) ACTION ---
    if override_method in ("PATCH", "PUT") or (request.method == "POST" and not override_method):
        if not is_authenticated():
            flash("You must be logged in!", "error")
            return redirect("/login")

        curr_user = get_current_user()
        owner = listing.get("owner", {})
        if str(owner.get("_id")) != str(curr_user.get("_id")) and owner.get("username") != curr_user.get("username"):
            flash("You do not have permission to edit this listing!", "error")
            return redirect(f"/listings/{listing_id}")

        title = request.form.get("listing[title]") or request.form.get("title")
        description = request.form.get("listing[description]") or request.form.get("description")
        image = request.form.get("listing[image]") or request.form.get("image")
        price = request.form.get("listing[price]") or request.form.get("price")
        location = request.form.get("listing[location]") or request.form.get("location")
        country = request.form.get("listing[country]") or request.form.get("country")

        logic.update_listing(listing_id, title, description, image, price, location, country)
        flash("Listing updated successfully!", "success")
        return redirect(f"/listings/{listing_id}")

    # --- GET: RENDER DETAILS ---
    return render_template("listings/show.html", listing=listing)


@app.route("/listings/<listing_id>/edit", methods=["GET", "POST"])
def edit_listing(listing_id):
    """Renders the edit form for a listing (Requires Login & Ownership)."""
    if not is_authenticated():
        flash("You must be logged in to edit a listing!", "error")
        return redirect("/login")

    listing = logic.get_listing_by_id(listing_id)
    if not listing:
        return render_template("errors/404Cast.html"), 404

    curr_user = get_current_user()
    owner = listing.get("owner", {})
    if str(owner.get("_id")) != str(curr_user.get("_id")) and owner.get("username") != curr_user.get("username"):
        flash("You do not have permission to edit this listing!", "error")
        return redirect(f"/listings/{listing_id}")

    if request.method == "POST":
        title = request.form.get("listing[title]") or request.form.get("title")
        description = request.form.get("listing[description]") or request.form.get("description")
        image = request.form.get("listing[image]") or request.form.get("image")
        price = request.form.get("listing[price]") or request.form.get("price")
        location = request.form.get("listing[location]") or request.form.get("location")
        country = request.form.get("listing[country]") or request.form.get("country")

        logic.update_listing(listing_id, title, description, image, price, location, country)
        flash("Listing updated successfully!", "success")
        return redirect(f"/listings/{listing_id}")

    return render_template("listings/edit.html", listing=listing)


# =============================================================================
# REVIEWS ROUTES
# =============================================================================

@app.route("/listings/<listing_id>/reviews", methods=["POST"])
def create_review(listing_id):
    """Adds a new guest review to the listing."""
    if not is_authenticated():
        flash("You must be logged in to leave a review!", "error")
        return redirect("/login")

    listing = logic.get_listing_by_id(listing_id)
    if not listing:
        return render_template("errors/404Cast.html"), 404

    name = request.form.get("review[name]") or request.form.get("name") or session.get("username", "Guest")
    rating = request.form.get("review[rating]") or request.form.get("rating", 5)
    description = request.form.get("review[description]") or request.form.get("description", "")

    logic.add_review(listing_id, name, rating, description)
    flash("Review successfully created!", "success")
    return redirect(f"/listings/{listing_id}")


@app.route("/listings/<listing_id>/reviews/<review_id>", methods=["POST", "DELETE"])
def delete_review(listing_id, review_id):
    """Deletes a guest review from the listing."""
    if not is_authenticated():
        flash("You must be logged in!", "error")
        return redirect("/login")

    logic.delete_review(listing_id, review_id)
    flash("Review successfully deleted!", "success")
    return redirect(f"/listings/{listing_id}")


# =============================================================================
# USER AUTHENTICATION ROUTES (Signup, Login, Logout)
# =============================================================================

@app.route("/signup", methods=["GET", "POST"])
def signup():
    """User registration route."""
    if is_authenticated():
        flash("You are already logged in!", "error")
        return redirect("/listings")

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not email or not password:
            flash("All fields are required!", "error")
            return redirect("/signup")

        new_user, error = logic.create_user(username, email, password)
        if error:
            flash(error, "error")
            return redirect("/signup")

        # Automatically log in new user
        session["user_id"] = new_user["_id"]
        session["username"] = new_user["username"]
        session["email"] = new_user["email"]

        flash("Welcome to Dwellio!", "success")
        return redirect(session.pop("redirect_url", "/listings"))

    return render_template("users/signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """User login route."""
    if is_authenticated():
        flash("You are already logged in!", "error")
        return redirect("/listings")

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        user = logic.authenticate_user(username, password)
        if not user:
            flash("Invalid username or password!", "error")
            return redirect("/login")

        # Set user in session
        session["user_id"] = user["_id"]
        session["username"] = user["username"]
        session["email"] = user.get("email", "")

        flash(f"Welcome back, {user['username']}!", "success")
        return redirect(session.pop("redirect_url", "/listings"))

    return render_template("users/login.html")


@app.route("/logout", methods=["GET"])
def logout():
    """Clears user session and logs out."""
    session.clear()
    flash("You have logged out successfully!", "success")
    return redirect("/listings")


# =============================================================================
# REST API ENDPOINTS (JSON APIs for Lab Viva demonstration)
# Uses standard request.get_json() and jsonify()
# =============================================================================

@app.route("/api/listings", methods=["GET"])
def api_get_listings():
    """API: Returns all listings as JSON."""
    search = request.args.get("search")
    listings = logic.get_all_listings(search)
    return jsonify({"success": True, "count": len(listings), "data": listings}), 200


@app.route("/api/listings/<listing_id>", methods=["GET"])
def api_get_listing(listing_id):
    """API: Returns a single listing by ID as JSON."""
    listing = logic.get_listing_by_id(listing_id)
    if not listing:
        return jsonify({"success": False, "error": "Listing not found"}), 404
    return jsonify({"success": True, "data": listing}), 200


@app.route("/api/listings", methods=["POST"])
def api_create_listing():
    """API: Creates a new listing using JSON request body."""
    body = request.get_json() or {}
    title = body.get("title")
    description = body.get("description")
    location = body.get("location")
    country = body.get("country")
    price = body.get("price", 15000)
    image = body.get("image", "")

    if not title or not description or not location or not country:
        return jsonify({"success": False, "error": "Missing required fields"}), 400

    owner_user = get_current_user() or {"_id": "api_user", "username": "admin", "email": "admin@dwellio.com"}
    new_item = logic.create_listing(title, description, image, price, location, country, owner_user)
    return jsonify({"success": True, "data": new_item}), 201


@app.route("/api/listings/<listing_id>", methods=["PUT"])
def api_update_listing(listing_id):
    """API: Updates an existing listing using JSON request body."""
    body = request.get_json() or {}
    updated = logic.update_listing(
        listing_id=listing_id,
        title=body.get("title"),
        description=body.get("description"),
        image=body.get("image"),
        price=body.get("price"),
        location=body.get("location"),
        country=body.get("country")
    )
    if not updated:
        return jsonify({"success": False, "error": "Listing not found"}), 404
    return jsonify({"success": True, "data": updated}), 200


@app.route("/api/listings/<listing_id>", methods=["DELETE"])
def api_delete_listing(listing_id):
    """API: Deletes a listing by ID."""
    deleted = logic.delete_listing(listing_id)
    if not deleted:
        return jsonify({"success": False, "error": "Listing not found"}), 404
    return jsonify({"success": True, "message": "Listing deleted successfully"}), 200


# =============================================================================
# 404 ERROR HANDLER
# =============================================================================

@app.errorhandler(404)
def not_found_error(error):
    """Central 404 handler rendering our custom dark Vice City 404 page."""
    return render_template("errors/404.html"), 404


# =============================================================================
# RUN FLASK SERVER
# =============================================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    print(f"============================================================")
    print(f" Dwellio Python Flask server running at http://127.0.0.1:{port}")
    print(f" Default Admin Credentials -> username: admin | password: admin123")
    print(f"============================================================")
    app.run(host="0.0.0.0", port=port, debug=True)
