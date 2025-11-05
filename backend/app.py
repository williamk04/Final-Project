from flask import Flask
from flask_cors import CORS
from routes.plate_route import plate_bp
from routes.dashboard_route import dashboard_bp
app = Flask(__name__)
CORS(app)

app.register_blueprint(plate_bp, url_prefix="/api")
app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
