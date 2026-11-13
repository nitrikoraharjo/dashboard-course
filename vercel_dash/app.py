# vercel_dash/app.py — pintu masuk (entrypoint) untuk Vercel
# Vercel mencari variabel bernama `app` yang berupa server WSGI.
# Server Flask milik Dash ada di `dash_app.server`.
from app_dash_callback import app as dash_app

app = dash_app.server

if __name__ == "__main__":
    dash_app.run(debug=False, port=8053)
