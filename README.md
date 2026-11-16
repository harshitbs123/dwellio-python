# 🏨 Dwellio (Python Flask Edition)

> **College Computer Programming Lab Mini-Project**  
> A luxury stays and villa rental full-stack web application rewritten in **Python Flask** with a zero-setup local JSON database (`data.json`).

---

## ✨ Key Features
- **Frontend Preserved 100%:** Cyberpunk/Vice-City dark glassmorphic UI styled with Tailwind CSS, custom fonts, FontAwesome icons, and motion interactions.
- **Beginner-Friendly Flask Backend:** Replaced Node.js/Express with clean Python Flask routes in `app.py` and modular CRUD functions in `logic.py`.
- **Zero Database Setup:** Uses Python's built-in `json` module with `data.json`. No MongoDB, SQL service, or local server installation required—runs out of the box!
- **Complete Authentication:** User signup, login, session management, logout, and protected routes (hosting, editing, deleting properties).
- **CRUD Operations:**
  - Create, Read, Update, Delete listings
  - Add & Delete guest reviews with 1–5 star ratings
  - Search by destination, title, location, or country
  - Category filters (Villas, Beachfront, Resorts, Mountains)
- **Dual Support (Web UI + RESTful JSON APIs):**
  - Serves dynamic HTML pages via Jinja2 (`render_template`)
  - Provides REST JSON API endpoints (`/api/listings`) using `request.get_json()` and `jsonify()`

---

## 📁 Project Structure

```text
dwellio-python/
├── app.py                  # Main Flask server, routes, auth & API endpoints
├── logic.py                # Business logic: JSON read/write, listing/review CRUD
├── data.json               # Local database storing listings, reviews, and users
├── requirements.txt        # Python dependencies (Flask)
├── README.md               # Project documentation & Lab Viva cheat sheet
├── templates/              # Jinja2 HTML templates
│   ├── landing.html        # Homepage with hero entrance and featured stays
│   ├── includes/           # Reusable partials (head, navbar, footer)
│   │   ├── head.html
│   │   ├── navbar.html
│   │   └── footer.html
│   ├── listings/           # Listing views
│   │   ├── listings.html   # Explore catalog with search & category filters
│   │   ├── show.html       # Listing details, pricing breakdown & reviews
│   │   ├── host.html       # Create new property form with live preview
│   │   └── edit.html       # Edit property details
│   ├── users/              # Authentication views
│   │   ├── login.html      # Sign in page
│   │   └── signup.html     # Sign up page
│   └── errors/             # Error pages
│       ├── 404.html        # Standard 404 page
│       └── 404Cast.html    # Listing not found page
└── static/                 # Static assets
    ├── css/motion.css      # Smooth motion & animations
    ├── js/motion.js        # Hero transitions & micro-interactions
    ├── fonts/              # Custom brand typography (Stardom, Zodiak)
    ├── logo.png            # Dwellio neon brand logo
    ├── dwellio-vice.png    # Hero artwork
    └── favicon.png         # Site favicon
```

---

## 🚀 Quick Setup & How to Run

### Step 1: Open Terminal in the `dwellio-python` directory
```bash
cd "dwellio-python"
```

### Step 2: (Optional but Recommended) Create & Activate a Virtual Environment
- **macOS / Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```
- **Windows:**
  ```cmd
  python -m venv venv
  venv\Scripts\activate
  ```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```
*(Only installs standard `Flask`)*

### Step 4: Run the Flask App
```bash
python app.py
```
Or:
```bash
python3 app.py
```

### Step 5: Open in Your Browser
Visit: **[http://localhost:5001](http://localhost:5001)** (or `http://127.0.0.1:5001`)

---

## 🔑 Pre-Configured Demo Credentials

| Role | Username | Password | Email |
| :--- | :--- | :--- | :--- |
| **Admin / Host** | `admin` | `admin123` | `admin@dwellio.com` |
| **Demo User** | `demo` | `demo123` | `demo@dwellio.com` |

*You can also create a new account anytime via the **Sign Up** page.*

---

## 📡 REST API Demonstration (For Viva Exam)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/listings` | Fetch all listings as JSON (supports `?search=Goa`) |
| `GET` | `/api/listings/<id>` | Fetch a single listing by its ID |
| `POST` | `/api/listings` | Create a new listing (`request.get_json()`) |
| `PUT` | `/api/listings/<id>` | Update an existing listing |
| `DELETE` | `/api/listings/<id>` | Delete a listing |

---

## 🎓 College Lab Viva Questions & Answers

### Q1: Why did you choose Python Flask over Node.js/Express for this mini-project?
> **Answer:** Flask is a lightweight WSGI micro-framework written in Python. It provides maximum clarity with minimal boilerplate: routes are declared using standard `@app.route()` decorators, session handling is built-in, and code execution is synchronous and easy to debug without complex asynchronous event loops or npm dependency trees.

### Q2: How does data storage work without MongoDB or MySQL?
> **Answer:** All data is persisted in a local `data.json` file. In `logic.py`, Python's standard `json` library is used with `json.load()` to read data into Python lists and dictionaries, and `json.dump()` to save updates back to disk. This eliminates external database installation issues while fulfilling all CRUD requirements.

### Q3: How is user authentication and session management handled?
> **Answer:** Flask provides a cryptographically signed cookie session (`from flask import session`). When a user signs in, their user ID and username are stored in `session['user_id']`. Protected routes (like `/listings/host` or edit/delete) check `is_authenticated()` by verifying if `'user_id'` exists in the session.

### Q4: How are flash notifications displayed after creating a listing or logging in?
> **Answer:** Flask's `flash("message", "success")` stores messages temporarily in the session. An `@app.context_processor` in `app.py` automatically extracts them and makes `success` and `error` lists available to all Jinja2 templates, which are rendered inside `navbar.html`.

### Q5: How does search filtering work?
> **Answer:** The search term is received as a query parameter via `request.args.get('search')`. In `logic.py`, `get_all_listings()` iterates through the listings and performs a case-insensitive substring match against `title`, `location`, `country`, and `description`.
