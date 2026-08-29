"""Application entry point.

Production runs this through gunicorn (see .replit): `gunicorn main:app`.
The app object is built here rather than at import of ``app`` so that
importing the application module has no side effects and stays testable.

Debug mode is opt-in via FLASK_DEBUG=1 and never on by default - the Werkzeug
debugger permits arbitrary code execution wherever it is reachable.
"""

import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "5000")),
        debug=os.environ.get("FLASK_DEBUG") == "1",
    )
