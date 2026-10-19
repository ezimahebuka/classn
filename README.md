# Roundcube-Style Webmail Login Demo

<!-- A local-only Flask mock login that recreates the supplied Roundcube-inspired screen. It does not authenticate with an email provider and must not be used to collect real account credentials. The default test credentials are `demo-user` and `demo-pass-123`; they can be changed with local environment variables. -->

## Run locally

<!-- ```sh
cd /Users/colin/Desktop/WebMailLogin
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
python -c 'import secrets; print(secrets.token_hex(32))'
``` -->

<!-- Paste the generated value into `FLASK_SECRET_KEY` in `.env`. Then start the development server:

```sh
python app.py
``` -->

<!-- Open <http://127.0.0.1:5000>. Sign in with the demo credentials in `.env.example`. The Flask-WTF CSRF token protects the POST route; the server checks required fields and compares against the configured mock values. It does not store, print, return, or forward submitted credentials. Only a success/failure message is retained briefly in the Flask session to show the result. -->

## Optional Telegram notifications

<!-- Set `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` in `.env`. Notifications are disabled when either value is blank. Each notification contains only the event type, UTC timestamp, boolean demo-validation result, and random event ID. Telegram delivery errors do not block the demo response. Keep `.env` local; it is excluded by `.gitignore`. -->

## Files

<!-- - `app.py`: Flask routes, CSRF setup, mock credential comparison, and metadata-only Telegram notification.
- `requirements.txt`: Flask, CSRF, dotenv, and HTTP client dependencies.
- `.env.example`: documented local demo settings and empty Telegram placeholders.
- `.gitignore`: excludes local secrets, virtual environments, and Python-generated files.
- `templates/login.html`: accessible login form, inline logo and icons, and result message.
- `static/css/style.css`: screenshot-matched colors, sizing, spacing, focus states, and responsive layout.
- `static/js/app.js`: prevents duplicate form submissions while the POST is in flight.
- `tests/test_app.py`: verifies demo success/failure, metadata-only notifications, and CSRF rejection. -->
