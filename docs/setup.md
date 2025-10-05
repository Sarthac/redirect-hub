# Redirect Hub Setup Guide

This guide will walk you through the process of setting up the Redirect Hub project for development.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- [Git](https://git-scm.com/)
- [Python](https://www.python.org/) (version 3.8 or higher recommended)
- [Node.js](https://nodejs.org/) (which includes npm) (Optional, only needed for tailwindcss)

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/sarthac/redirect-hub.git
   cd redirect-hub
   ```

2. **Set up the Python virtual environment and install dependencies:**

   ```bash
   # Create a virtual environment
   python -m venv .venv

   # Activate the virtual environment
   # On Windows
   .venv\Scripts\activate
   # On macOS/Linux
   source .venv/bin/activate

   # Install Python packages
   pip install -r requirements.txt
   ```

3. **Install Node.js dependencies:** (Can be skipped)

   This project uses Tailwind CSS for styling. Install the necessary Node.js packages to build the CSS.

   ```bash
   npm install
   ```

## Configuration

1. **Environment Variables:**

   The application uses environment variables for configuration. Create a `.env` file in the root of the project and add the following variables:

   ```
   FLASK_ENV=development
   SECRET_KEY=your_very_secret_key
   ```

   - `FLASK_ENV`: Set to `development` for development mode, which enables debugging and other development features. For production, it should be set to `production`.
   - `SECRET_KEY`: This is a secret key used for session management. Replace `your_very_secret_key` with a long, random string.

## Running the Application

1. **Build the Tailwind CSS:** (Can be skipped)

   Before running the Flask application, you need to compile the Tailwind CSS.

   ```bash
   npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --watch
   ```
   The `--watch` flag will automatically rebuild the CSS when you make changes to the template files.

2. **Run the Flask Development Server:**

   In a separate terminal, make sure your virtual environment is activated, and then run the application:

   ```bash
   python app.py
   ```

   The application will be available at `http://127.0.0.1:5002`.
