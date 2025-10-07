# ObesiTrack

🏃‍♀️ ObesiTrack is a web application designed to help users track their weight, predict future weight trends, and receive personalized advice.

## ✨ Features

- **User Authentication**: Secure login and registration system.
- **Weight Tracking**: Log daily weight entries.
- **Data Visualization**: View weight history in an interactive chart.
- **AI-Powered Predictions**: Predict future weight trends based on historical data.
- **Personalized Advice**: Get recommendations based on your progress.
- **Administrator Panel**: Manage users and view system statistics.

## 🚀 Technologies

- **Backend**: Python, FastAPI, SQLAlchemy
- **Database**: PostgreSQL
- **Authentication**: JWT
- **Containerization**: Docker, Docker Hub

## 📦 Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/ObesiTrack.git
   cd ObesiTrack
   ```

2. **Set up the environment**:
   - Create a `.env` file based on `.env.example`.
   - Fill in the required environment variables.

3. **Build and run the Docker container**:
   ```bash
   docker-compose up --build
   ```

4. **Access the application**:
   - The application will be available at `http://localhost:8000`.

## Project Structure

```
ObesiTrack/
├── app/
│   ├── auth/         # Authentication logic
│   ├── models/       # Pydantic models
│   ├── routes/       # API routes
│   ├── static/       # Static files (CSS, JS)
│   ├── templates/    # HTML templates
│   ├── config.py     # Configuration settings
│   ├── database.py   # Database connection
│   └── main.py       # Application entry point
├── data/             # ML model and data
├── docker-compose.yml # Docker Compose configuration
├── Dockerfile        # Docker configuration
└── README.md         # Project documentation
```