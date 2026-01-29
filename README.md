# McLuck - Safety Quiz Application

A Flask-based web application for conducting safety quizzes with user authentication and score tracking. Data is stored locally in a JSON file.

## Features

- **User Authentication**: Secure registration and login with bcrypt password hashing
- **Safety Quiz**: Interactive quiz interface for safety training
- **Score Tracking**: Automatic score submission and tracking
- **User Dashboard**: View quiz results and pass/fail status
- **Local Storage**: All user data stored locally in `users_data.json`

## Technology Stack

- **Backend**: Flask (Python)
- **Authentication**: bcrypt for password hashing
- **Storage**: JSON file-based local storage
- **Frontend**: HTML templates with Tailwind CSS

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/NamasteIndia/mcluck.git
cd mcluck
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables (optional):
   - Copy `.env.example` to `.env` if you need to customize settings
   - The default secret key will be used if not specified

## Running the Application

### Development Mode

Run the Flask development server:

```bash
python app.py
```

The application will be available at `http://localhost:8080`

### Production Mode

For production deployment, use Gunicorn:

```bash
gunicorn app:app --bind 0.0.0.0:8080
```

## Usage

1. **Register**: Create a new account with a unique username and password
2. **Login**: Sign in with your credentials
3. **Take Quiz**: Complete the safety quiz on the main page
4. **View Results**: Check your score and pass/fail status in the profile section
5. **Logout**: End your session securely

## Grading System

- **Total Marks**: 50
- **Passing Score**: 10 or above
- **Result**: Displayed as PASSED (green) or FAILED (red)

## Data Storage

User data is stored locally in `users_data.json` with the following structure:

```json
{
  "username": {
    "username": "username",
    "password": "hashed_password",
    "last_score": 0
  }
}
```

**Note**: The `users_data.json` file is automatically created on first use and is excluded from version control via `.gitignore`.

## Security

- Passwords are hashed using bcrypt with salt
- Session management with secure cookies
- Local file-based storage (no external database required)

## Project Structure

```
mcluck/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── users_data.json     # Local user data storage (auto-created)
├── templates/          # HTML templates
│   ├── index.html      # Quiz page
│   ├── login.html      # Login page
│   ├── register.html   # Registration page
│   └── profile.html    # User dashboard
├── .env                # Environment variables (not in git)
├── .gitignore          # Git ignore rules
├── Procfile            # Deployment configuration
└── README.md           # This file
```

## Environment Variables

You can customize the following environment variables in `.env`:

- `SECRET_KEY`: Flask session secret key (default: "tata_steel_safety_2026_portal")
- `PORT`: Application port (default: 8080)

## Deployment

### Deploy to Koyeb

1. Push your code to GitHub
2. Connect your GitHub repository to Koyeb
3. Set environment variables in Koyeb dashboard (if needed)
4. Deploy!

### Deploy to Heroku

```bash
heroku create your-app-name
git push heroku main
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Support

For issues and questions, please open an issue on the GitHub repository.