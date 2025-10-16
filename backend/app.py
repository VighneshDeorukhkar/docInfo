from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import os
from dotenv import load_dotenv
import logging

# Load env variables
load_dotenv()
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

# Flask setup
app = Flask(__name__)

# CORS
CORS(app,
     origins=["https://docinfo-frontend.onrender.com", "http://localhost:3000"],
     supports_credentials=True,
     methods=["GET", "POST", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"])

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "requests.db")
FILES_PATH = os.path.join(BASE_DIR, "files")
os.makedirs(FILES_PATH, exist_ok=True)

# Config
app.config.update({
    "SQLALCHEMY_DATABASE_URI": f"sqlite:///{DB_PATH}",
    "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    "MAIL_SERVER": "smtp.gmail.com",
    "MAIL_PORT": 587,
    "MAIL_USE_TLS": True,
    "MAIL_USERNAME": EMAIL_USER,
    "MAIL_PASSWORD": EMAIL_PASS,
})

db = SQLAlchemy(app)
mail = Mail(app)

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")

# Database model
class RequestModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200))
    document_name = db.Column(db.String(200))
    status = db.Column(db.String(50), default="pending")

with app.app_context():
    db.create_all()

# Routes
@app.route("/")
def home():
    return jsonify({"message": "Backend is running", "routes": ["/request-document", "/get-requests", "/approve-request/<id>", "/reject-request/<id>"]})

@app.route("/request-document", methods=["POST", "OPTIONS"])
def request_document():
    if request.method == "OPTIONS":
        return jsonify({"message": "CORS preflight"}), 200

    data = request.get_json()
    if not data or "email" not in data or "document_name" not in data:
        return jsonify({"error": "Missing email or document_name"}), 400

    new_req = RequestModel(email=data["email"], document_name=data["document_name"])
    db.session.add(new_req)
    db.session.commit()
    return jsonify({"message": "Request submitted"}), 200

@app.route("/get-requests", methods=["GET"])
def get_requests():
    all_requests = RequestModel.query.all()
    result = [{"id": r.id, "email": r.email, "document": r.document_name, "status": r.status} for r in all_requests]
    return jsonify(result), 200

@app.route("/approve-request/<int:req_id>", methods=["POST"])
def approve_request(req_id):
    req = RequestModel.query.get(req_id)
    if not req:
        return jsonify({"error": "Request not found"}), 404

    req.status = "approved"
    db.session.commit()

    filename = req.document_name if req.document_name.lower().endswith(".pdf") else req.document_name + ".pdf"
    doc_path = os.path.join(FILES_PATH, filename)
    if not os.path.exists(doc_path):
        return jsonify({"error": f"Document not found: {filename}"}), 404

    try:
        msg = Message(subject=f"Document Approved: {req.document_name}",
                      sender=EMAIL_USER,
                      recipients=[req.email],
                      body=f"Your requested document '{req.document_name}' has been approved.")
        with open(doc_path, "rb") as fp:
            msg.attach(filename, "application/pdf", fp.read())
        mail.send(msg)
        return jsonify({"message": "Approved and email sent"}), 200
    except Exception as e:
        return jsonify({"error": f"Email failed: {str(e)}"}), 500

@app.route("/reject-request/<int:req_id>", methods=["POST"])
def reject_request(req_id):
    req = RequestModel.query.get(req_id)
    if not req:
        return jsonify({"error": "Request not found"}), 404

    req.status = "rejected"
    db.session.commit()
    return jsonify({"message": "Request rejected"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
