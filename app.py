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
)
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
    UserMixin,
)
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from bson.objectid import ObjectId
from google import genai
import requests
import httpx
import asyncio
import math
from pydantic import BaseModel, TypeAdapter

load_dotenv()  # Load environment variables from .env

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "supersecretkey")

# Setup MongoDB
mongo_uri = os.environ.get("MONGO_URI")
geminapi = os.environ.get("GEMINI_API_KEY")

gemini_client = genai.Client(api_key=geminapi)
client = MongoClient(mongo_uri, server_api=ServerApi("1"))
db = client.get_database(
    "etherescape"
)  # uses the default database specified in the URI
# Test MongoDB connection
try:
    client.admin.command("ping")
    print("Successfully connected to MongoDB!")
except Exception as e:
    print("MongoDB connection error:", e)
    raise e
# Setup Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = "login"  # redirect unauthenticated users to the login page


# User model for Flask-Login
class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data["_id"])
        self.email = user_data["email"]
        self.name = user_data.get("name", self.email.split("@")[0])
        self.bio = user_data.get("bio", "")
        self.interests = user_data.get("interests", "")

    @staticmethod
    def get(user_id):
        user_data = db.User.find_one({"_id": ObjectId(user_id)})
        if user_data:
            return User(user_data)
        return None


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


# --- Public Routes (without navigation bar) ---


@app.route("/")
def landing():
    # Uses a public base template (public_base.html) that does not include the navbar.
    return render_template("landing.html", title="Landing")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user_data = db.User.find_one({"email": email})
        if user_data and check_password_hash(user_data["password"], password):
            user = User(user_data)
            login_user(user)
            # Get user's IP address, handling proxies if necessary:
            if request.headers.get("X-Forwarded-For"):
                ip = request.headers.get("X-Forwarded-For").split(",")[0].strip()
            else:
                ip = request.remote_addr
            # Store the IP in the session
            session["user_ip"] = ip
            return redirect(url_for("activities"))
        else:
            flash("Invalid email or password.")
            return redirect(url_for("login"))
    # Render the login page without navigation.
    return render_template("login.html", title="Log In")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        try:
            first_name = request.form["first_name"]
            last_name = request.form["last_name"]
            email = request.form["email"]
            password = request.form["password"]
            interests_list = request.form.getlist("interests")
            interests = ",".join(interests_list)
            bio = request.form.get("bio", "")

            if db.User.find_one({"email": email}):
                flash("User already exists.")
                return redirect(url_for("signup"))

            hashed_pw = generate_password_hash(password)
            db.User.insert_one(
                {
                    "email": email,
                    "password": hashed_pw,
                    "first_name": first_name,
                    "last_name": last_name,
                    "name": f"{first_name} {last_name}",
                    "bio": bio,
                    "interests": interests,
                }
            )
            flash("Signup successful! Please log in.")
            return redirect(url_for("login"))
        except Exception as e:
            flash("An error occurred: " + str(e))
            return redirect(url_for("signup"))

    # GET request: query the Interests collection
    interests_list = list(db.Interests.find({}, {"_id": 0, "name": 1}))
    return render_template("signup.html", title="Sign Up", interests=interests_list)


# --- Protected Routes (with navigation bar) ---
# These pages require a logged-in user and use a protected base template (protected_base.html).


# Define the schema for an activity suggestion.
class Activity(BaseModel):
    activity: str
    location: str
    description: str
    time_availability: str
    longitude: float
    latitude: float


@app.route("/activities")
@login_required
def activities():
    # Retrieve the user's IP address and interests (these were stored on login)
    user_ip = session.get("user_ip", "Unknown IP")
    user_interests = current_user.interests
    # Render the template with these values so client-side code can use them
    return render_template(
        "activities.html",
        title="Activities",
        user_ip=user_ip,
        user_interests=user_interests,
    )


@app.route("/api/gemini_activities")
@login_required
async def gemini_activities():
    user_ip = session.get("user_ip", "Unknown IP")
    if user_ip == "127.0.0.1":  # Localhost IP
        user_ip = "129.15.64.228"
    user_interests = current_user.interests

    # Fallback if IP is unknown
    if user_ip == "Unknown IP":
        print("User IP is unknown")
        return jsonify([])

    async with httpx.AsyncClient() as client:
        ip_response = await client.get(f"http://ip-api.com/json/{user_ip}")
    if ip_response.status_code != 200:
        print("Failed to retrieve IP information")
        return jsonify([])

    ip_info = ip_response.json()
    city = ip_info.get("city", "Unknown City")
    region = ip_info.get("regionName", "Unknown Region")
    if city == "Unknown City" or region == "Unknown Region":
        print("Failed to retrieve city or region", city, region)
        # Fallback if city or region is unknown
        return jsonify([])

    prompt = (
        f"Give me a list of suggested activities based on these interests: "
        f"{user_interests} in the area of {city}, {region}"
    )

    response = await asyncio.to_thread(
        gemini_client.models.generate_content,
        model="gemini-2.0-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": list[Activity],
        },
    )
    # Assuming the response has a .text attribute that returns JSON or a string
    try:
        activitiesData = response.text
        print("Fetched activities data")
    except Exception as e:
        print("Error fetching activities data:", e)
        activitiesData = []
    return activitiesData


@app.route("/public_events")
@login_required
def public_events():
    # Query all users except the current user
    # Create dummy data for now
    eventsData = [
        {
            "id": 1,
            "title": "Event 1",
            "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        },
        {
            "id": 2,
            "title": "Event 2",
            "description": "Ut enim ad minim veniam, quis nostrud exercitation ullamco.",
        },
        {
            "id": 3,
            "title": "Event 3",
            "description": "Duis aute irure dolor in reprehenderit in voluptate velit.",
        },
        {
            "id": 4,
            "title": "Event 4",
            "description": "Excepteur sint occaecat cupidatat non proident.",
        },
    ]

    return render_template("public_events.html", events=eventsData, title="Events")


@app.route("/schedule")
@login_required
def schedule():
    events = list(
        db.ScheduledEvents.find({"user_id": current_user.id, "verified": False})
    )
    # Convert ObjectIds to strings if needed:
    for event in events:
        event["id"] = str(event["_id"])
    return render_template("schedule.html", schedule=events, title="Schedule")


@app.route("/schedule_event", methods=["GET", "POST"])
@login_required
def schedule_event():
    if request.method == "POST":
        # Retrieve form data
        activity = request.form["activity"]
        description = request.form["description"]
        location = request.form["location"]
        time_availability = request.form["time_availability"]
        scheduled_date = request.form["scheduled_date"]
        longitude = request.form["longitude"]
        latitude = request.form["latitude"]

        # Save scheduled event to the database (in ScheduledEvents collection)
        event_data = {
            "user_id": current_user.id,
            "activity": activity,
            "description": description,
            "location": location,
            "longitude": longitude,
            "latitude": latitude,
            "time_availability": time_availability,
            "scheduled_date": scheduled_date,
            "verified": False,
        }
        db.ScheduledEvents.insert_one(event_data)
        flash("Event scheduled successfully!")
        return redirect(url_for("schedule"))

    # GET request: prefill form fields from query parameters
    activity = request.args.get("activity", "")
    description = request.args.get("description", "")
    location = request.args.get("location", "")
    time_availability = request.args.get("time_availability", "")
    longitude = request.args.get("longitude", "")
    latitude = request.args.get("latitude", "")

    return render_template(
        "schedule_event.html",
        title="Schedule Event",
        activity=activity,
        description=description,
        location=location,
        time_availability=time_availability,
        longitude=longitude,
        latitude=latitude,
    )


@app.route("/verify_event/<event_id>", methods=["POST"])
@login_required
def verify_event(event_id):
    user_lat = float(request.form["latitude"])
    user_long = float(request.form["longitude"])

    print(user_lat, user_long)

    # retrieve event data from database
    try:
        event = db.ScheduledEvents.find_one(
            {"_id": ObjectId(event_id), "user_id": current_user.id}
        )
    except Exception as e:
        flash("Error retrieving event: " + str(e))
        print(e)
        return redirect(url_for("schedule"))

    print(event)

    if not event:
        flash("Event not found or you do not have permission to verify it.")
        return redirect(url_for("schedule"))

    event_lat = float(event.get("latitude"))
    event_lng = float(event.get("longitude"))
    if event_lat is None or event_lng is None:
        flash("Event location not set.")
        return redirect(url_for("schedule"))

    print(event_lat, event_lng)
    # Check if user is 0.1 miles from event location
    distance = calculate_distance(user_lat, user_long, event_lat, event_lng)
    print(distance)
    if distance > 0.1:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "You are not close enough to verify attendance.",
                }
            ),
            400,
        )
    # Otherwise call smart contract to verify event
    try:
        print("Verifying event...")
    except Exception as e:
        flash("Error verifying event: " + str(e))
        return redirect(url_for("schedule"))

    # Add user points
    db.User.update_one({"_id": ObjectId(current_user.id)}, {"$inc": {"points": 10}})

    # mark event as verified
    db.ScheduledEvents.update_one(
        {"_id": ObjectId(event_id)}, {"$set": {"verified": True}}
    )

    return jsonify({"success": True})
    return redirect(url_for("schedule"))


@app.route("/account")
@login_required
def account():
    # Get activity history from verified events under user
    activityHistory = list(
        db.ScheduledEvents.find({"user_id": current_user.id, "verified": True})
    )

    # format events
    for i in range(len(activityHistory)):
        activityHistory[i]["id"] = i + 1
        activityHistory[i]["date"] = activityHistory[i]["scheduled_date"].strftime(
            "%Y-%m-%d"
        )
        activityHistory[i]["title"] = activityHistory[i]["activity"]

    # current_user is provided by Flask-Login. It should contain fields such as email, name, bio, and interests.
    return render_template(
        "account.html",
        user=current_user,
        activityHistory=activityHistory,
        title="Account",
    )


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("landing"))


# ---- Helper Functions ----
def calculate_distance(lat1, long1, lat2, long2):
    # Harversine formula to calculate distance between two lat/long points
    R = 3959  # Radius of the Earth in miles
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(long2 - long1)
    a = (
        math.sin(dLat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dLon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))
    return R * c


if __name__ == "__main__":
    app.run(debug=True, port=8800)
