from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Flask setup
app = Flask(__name__)
CORS(app)

# ===================== CONFIG =====================
# Database
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "requests.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"

# Mail
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.getenv("EMAIL_USER")
app.config["MAIL_PASSWORD"] = os.getenv("EMAIL_PASS")

# Initialize extensions
db = SQLAlchemy(app)
mail = Mail(app)

# ===================== DATABASE MODEL =====================
class RequestModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200))
    document_name = db.Column(db.String(200))
    status = db.Column(db.String(50), default="pending")  # pending/approved/rejected

with app.app_context():
    db.create_all()


# ===================== API ROUTES =====================
@app.route("/request-document", methods=["POST"])
def request_document():
    data = request.get_json()
    new_req = RequestModel(
        email=data["email"],
        document_name=data["document_name"]
    )
    db.session.add(new_req)
    db.session.commit()
    return jsonify({"message": "Request submitted"}), 200


@app.route("/get-requests", methods=["GET"])
def get_requests():
    requests_data = RequestModel.query.all()
    result = [
        {"id": r.id, "email": r.email, "document": r.document_name, "status": r.status}
        for r in requests_data
    ]
    return jsonify(result), 200


@app.route("/approve-request/<int:req_id>", methods=["POST"])
def approve_request(req_id):
    req = RequestModel.query.get(req_id)
    if not req:
        return jsonify({"error": "Request not found"}), 404

    req.status = "approved"
    db.session.commit()

    # 🟢 UNC network folder path (update to match your folder)
    NETWORK_BASE_PATH = r"\\10.178.0.14\Public\Telecommunication\06-OLD PROJECT REFERENCE\AWE\Architect Diagram\Rev-A"

    # 🧭 Normalize and create full path to the requested file
    # Construct full UNC path directly
    network_base = r"\\10.178.0.14\Public\Telecommunication\06-OLD PROJECT REFERENCE\AWE\Architect Diagram\Rev-A"
    # Ensure .pdf is always included
    filename = req.document_name
    if not filename.lower().endswith(".pdf"):
        filename += ".pdf"

    doc_path = os.path.join(network_base, filename)
    print("Looking for document at:", doc_path)

    print("Looking for document at:", doc_path)


    # 🧾 Check if file exists
    if not os.path.exists(doc_path):
        print(f"⚠️ File not found: {doc_path}")
        return jsonify({"error": f"Document not found on server: {doc_path}"}), 404

    # 📧 Send email with attachment
    try:
        msg = Message(
            subject=f"Document Request Approved: {req.document_name}",
            sender=app.config["MAIL_USERNAME"],
            recipients=[req.email],
            body=f"Hello,\n\nYour requested document '{req.document_name}' has been approved. The document is attached below.",
        )

        with open(doc_path, "rb") as fp:
            msg.attach(req.document_name, "application/pdf", fp.read())

        mail.send(msg)

        print(f"✅ Sent document '{req.document_name}' to {req.email}")
        return jsonify({"message": "Approved and email sent"}), 200

    except Exception as e:
        print(f"❌ Email send failed: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/reject-request/<int:req_id>", methods=["POST"])
def reject_request(req_id):
    req = RequestModel.query.get(req_id)
    if not req:
        return jsonify({"error": "Request not found"}), 404

    req.status = "rejected"
    db.session.commit()
    return jsonify({"message": "Request rejected"}), 200


if __name__ == "__main__":
    os.makedirs("files", exist_ok=True)
    app.run(debug=True)
