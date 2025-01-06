"""
This script runs the FlaskWebProject application using a development or production server.
"""

from os import environ
from FlaskWebProject import app

if __name__ == '__main__':
    # Determine host and port from environment variables or use defaults
    HOST = environ.get('SERVER_HOST', '0.0.0.0')  # Use '0.0.0.0' for Azure compatibility
    try:
        PORT = int(environ.get('SERVER_PORT', '5555'))  # Default port is 5555
    except ValueError:
        PORT = 5555

    # Enable debugging in development mode
    DEBUG = environ.get('FLASK_DEBUG', 'False').lower() == 'true'

    # Run the app with SSL context for local testing (optional)
    app.run(host=HOST, port=PORT, debug=DEBUG, ssl_context='adhoc' if DEBUG else None)
