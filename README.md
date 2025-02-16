# EtherEscape

EtherEscape is a web application designed to help users discover and schedule activities based on their interests and location. Built with Flask and MongoDB, the application provides features such as user authentication, activity suggestions powered by Gemini AI, scheduling events, and verifying event attendance. Although the project initially planned to incorporate Ethereum-based smart contracts to verify attendance on-chain, that feature is not yet implemented due to errors.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Project Structure](#project-structure)
- [Possible Feature Extensions](#possible-feature-extensions)
- [License](#license)

## Features

Currently, EtherEscape implements the following features:

- **User Authentication:**  
  - Sign up new users.
  - Login and logout using Flask-Login.
  
- **Activity Suggestions:**  
  - Fetch activity suggestions using Gemini AI based on user interests and geolocation.
  
- **Event Scheduling and Verification:**  
  - Schedule events and store them in MongoDB.
  - Verify event attendance by checking user proximity to the event location (using the Haversine formula).
  
- **Public Events:**  
  - Display dummy public events.
  
- **User Account Management:**  
  - Display scheduled events and activity history.
  - Track user points based on event verification.

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/etherescape.git
   cd etherescape
   ```
2. **Create a virtual environment and activate it:**
    ```bash 
    python3 -m venv venv
    source venv/bin/activate    # On Windows use `venv\Scripts\activate`
    ```
1. **Install the required dependencies:**
    
    bash
    
    Copy
    
    `pip install -r requirements.txt`
    
    **Required packages include:**
    
    - Flask
    - Flask-Login
    - pymongo
    - python-dotenv
    - Werkzeug
    - httpx
    - asyncio
    - pydantic
    - Gemini AI SDK (from the `google` package, if applicable)
2. **Install and run MongoDB:**
    
    Make sure you have MongoDB installed and running. You can download MongoDB from [mongodb.com](https://www.mongodb.com/try/download/community).
    

## Configuration

3. **Environment Variables:**
    
    Create a `.env` file in the project root directory with the following variables:
    
    ```bash
    SECRET_KEY="your_super_secret_key MONGO_URI=mongodb+srv://<username>:<password>@cluster0.mongodb.net/etherescape?retryWrites=true&w=majority"
    GEMINI_API_KEY="your_gemini_api_key"
    ```
    
    Adjust the values as needed for your environment.
    

## Running the Application

4. **Start the Flask Application:**
    
    Ensure your virtual environment is activated and run:
    
    ```bash
    flask run 
    ```
    
5. **Access the Application:**
    
    Open your web browser and navigate to:
    
    `http://127.0.0.1:8800/`
    
    From here, you can sign up, log in, and explore the available routes:
    
    - **Landing Page:** `/`
    - **Login:** `/login`
    - **Sign Up:** `/signup`
    - **Activity Suggestions:** `/activities`
    - **Public Events:** `/public_events`
    - **Schedule Event:** `/schedule_event`
    - **Verify Event:** `/verify_event/<event_id>`
    - **User Account:** `/account`
    - **Logout:** `/logout`

## Project Structure

```bash

etherescape/
├── app.py                 # Main Flask application with routes and logic.
├── templates/             # HTML templates for the application.
│   ├── landing.html
│   ├── login.html
│   ├── signup.html
│   ├── activities.html
│   ├── public_events.html
│   ├── schedule.html
│   ├── schedule_event.html
│   └── account.html
├── static/                # CSS, JavaScript, and other static files.
├── .env                   # Environment variables file.
├── requirements.txt       # List of required Python packages.
└── README.md              # This file.
```
## Possible Feature Extensions

While the current implementation covers core functionalities such as user authentication, activity suggestions, event scheduling, and basic event verification, there are several potential extensions to enhance the platform:

6. **Public Events Organized by Users:**
    
    - Allow users to create and manage public events that other users can join and attend.
    - Enable event organizers to invite friends or community members.
    - Provide an RSVP system for users to confirm attendance.
7. **Ethereum-Based Smart Contracts for Event Verification:**
    
    - Integrate smart contracts to verify user attendance on-chain.
    - Use blockchain-based verification to secure and immutably log event attendance.
    - Explore partnerships with blockchain platforms for decentralization and added trust.
8. **Extended Point System and Leaderboards:**
    
    - Expand the point system to include leaderboards, encouraging competition among users.
    - Introduce mini-competitions among friends or within community groups.
    - Reward top performers with special badges or achievements.
9. **Discounts and Rewards:**
    
    - Partner with local businesses or activity venues to offer discounts for users with high engagement or event attendance.
    - Implement a reward system where users can redeem points for discounts at paid activity places across various regions.

## License

This project is licensed under the MIT License.