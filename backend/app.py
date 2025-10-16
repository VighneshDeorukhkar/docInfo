from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import os
from dotenv import load_dotenv
import logging

# ==========================================================
# Load environment variables
# ==========================================================
load_dotenv()
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
print("EMAIL_USER:", EMAIL_USER)
print("EMAIL_PASS:", EMAIL_PASS)

# ==========================================================
# Flask setup
# ==========================================================
app = Flask(__name__)

# ======== GLOBAL CORS CONFIG ========
CORS(app, origins=[
    "https://docinfo-frontend.onrender.com",  # deployed frontend
    "http://localhost:3000"                  # local frontend for testing
], supports_credentials=True)

# ==========================================================
# CONFIGURATION
# ==========================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "requests.db")

app.config.update({
    "SQLALCHEMY_DATABASE_URI": f"sqlite:///{DB_PATH}",
    "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    "MAIL_SERVER": "smtp.gmail.com",
    "MAIL_PORT": 587,
    "MAIL_USE_TLS": True,
    "MAIL_USERNAME": EMAIL_USER,
    "MAIL_PASSWORD": EMAIL_PASS,
})

# Initialize extensions
db = SQLAlchemy(app)
mail = Mail(app)

# ==========================================================
# LOGGING SETUP
# ==========================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]: %(message)s",
    handlers=[logging.StreamHandler()]
)

# ==========================================================
# DATABASE MODEL
# ==========================================================
class RequestModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200))
    document_name = db.Column(db.String(200))
    status = db.Column(db.String(50), default="pending")  # pending/approved/rejected

with app.app_context():
    db.create_all()

# ==========================================================
# ROUTES
# ==========================================================
@app.route("/")
@cross_origin(origins=[
    "https://docinfo-frontend.onrender.com",
    "http://localhost:3000"
])
def home():
    return jsonify({
        "message": "✅ Flask backend is running successfully!",
        "routes": [
            "/request-document (POST)",
            "/get-requests (GET)",
            "/approve-request/<id> (POST)",
            "/reject-request/<id> (POST)"
        ]
    })


@app.route("/request-document", methods=["POST"])
@cross_origin(origins=[
    "https://docinfo-frontend.onrender.com",
    "http://localhost:3000"
], supports_credentials=True)
def request_document():
    data = request.get_json()
    if not data or "email" not in data or "document_name" not in data:
        return jsonify({"error": "Missing email or document_name"}), 400

    new_req = RequestModel(email=data["email"], document_name=data["document_name"])
    db.session.add(new_req)
    db.session.commit()

    logging.info(f"📥 New request added: {data['document_name']} by {data['email']}")
    return jsonify({"message": "Request submitted"}), 200


@app.route("/get-requests", methods=["GET"])
@cross_origin(origins=[
    "https://docinfo-frontend.onrender.com",
    "http://localhost:3000"
])
def get_requests():
    requests_data = RequestModel.query.all()
    result = [
        {"id": r.id, "email": r.email, "document": r.document_name, "status": r.status}
        for r in requests_data
    ]
    return jsonify(result), 200


@app.route("/approve-request/<int:req_id>", methods=["POST"])
@cross_origin(origins=[
    "https://docinfo-frontend.onrender.com",
    "http://localhost:3000"
], supports_credentials=True)
def approve_request(req_id):
    req = RequestModel.query.get(req_id)
    if not req:
        return jsonify({"error": "Request not found"}), 404

    req.status = "approved"
    db.session.commit()

    # Update this path to your actual document folder
    NETWORK_BASE_PATH = r"\\10.178.0.14\Public\Telecommunication\06-OLD PROJECT REFERENCE\AWE\Architect Diagram\Rev-A"

    filename = req.document_name
    if not filename.lower().endswith(".pdf"):
        filename += ".pdf"

    doc_path = os.path.normpath(os.path.join(NETWORK_BASE_PATH, filename))
    logging.info(f"🔍 Looking for document at: {doc_path}")

    if not os.path.exists(doc_path):
        logging.warning(f"⚠️ File not found: {doc_path}")
        return jsonify({"error": f"Document not found on server: {doc_path}"}), 404

    try:
        msg = Message(
            subject=f"Document Request Approved: {req.document_name}",
            sender=EMAIL_USER,
            recipients=[req.email],
            body=f"Hello,\n\nYour requested document '{req.document_name}' has been approved.\nPlease find it attached below.\n\nRegards,\nDocument Control Team",
        )

        with open(doc_path, "rb") as fp:
            msg.attach(filename, "application/pdf", fp.read())

        mail.send(msg)
        logging.info(f"✅ Sent '{filename}' to {req.email}")
        return jsonify({"message": "Approved and email sent"}), 200

    except Exception as e:
        logging.error(f"❌ Email send failed: {e}")
        return jsonify({"error": f"Email failed to send: {str(e)}"}), 500


@app.route("/reject-request/<int:req_id>", methods=["POST"])
@cross_origin(origins=[
    "https://docinfo-frontend.onrender.com",
    "http://localhost:3000"
], supports_credentials=True)
def reject_request(req_id):
    req = RequestModel.query.get(req_id)
    if not req:
        return jsonify({"error": "Request not found"}), 404

    req.status = "rejected"
    db.session.commit()

    logging.info(f"🚫 Request ID {req_id} rejected")
    return jsonify({"message": "Request rejected"}), 200


# ==========================================================
# MAIN ENTRY
# ==========================================================
if __name__ == "__main__":
    os.makedirs("files", exist_ok=True)
    port = int(os.environ.get("PORT", 5000))
    logging.info(f"🚀 Server running on 0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
