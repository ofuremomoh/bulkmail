from flask import Flask, render_template, request, flash, redirect, url_for
import requests
import re

app = Flask(__name__)
app.secret_key = "supersecretkey"

# MailerSend config
MAILERSEND_API_KEY = "mlsn.c535179a837834293cfa747be0551243a21003f8dd622cd40b242f450990a03a"
MAILERSEND_FROM_EMAIL = "ofure@engagefeed.com"  # Must be verified
MAILERSEND_FROM_NAME = "Sample Test"

# Basic email validation
def is_valid_email(email):
    regex = r"[^@]+@[^@]+\.[^@]+"
    return re.match(regex, email) is not None

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        recipients_raw = request.form.get("recipients", "")
        subject = request.form.get("subject", "")
        text = request.form.get("text", "")

        if not recipients_raw or not subject or not text:
            flash("Please fill in recipients, subject, and message body", "danger")
            return redirect(url_for("index"))

        # Clean, deduplicate, and validate emails
        recipients = [
            r.strip() for r in re.split(r"[\n,]+", recipients_raw)
            if r.strip() and is_valid_email(r.strip())
        ]
        recipients = list(dict.fromkeys(recipients))  # preserve order, remove duplicates

        if not recipients:
            flash("No valid recipient emails provided.", "danger")
            return redirect(url_for("index"))

        errors = []
        sent_count = 0

        headers = {
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "Authorization": f"Bearer {MAILERSEND_API_KEY}"
        }

        # HTML content with image and button
        demo_image_url = "https://via.placeholder.com/600x200.png?text=Demo+Image"
        demo_button_url = "https://example.com"
        demo_button_text = "Click Here"

        html_template = f"""
        <html>
        <body>
            <p>{text}</p>
            <img src="{demo_image_url}" alt="Demo Image" style="width:100%;max-width:600px;">
            <br><br>
            <a href="{demo_button_url}" style="display:inline-block;padding:12px 24px;background-color:#007bff;color:#fff;text-decoration:none;border-radius:5px;">
                {demo_button_text}
            </a>
        </body>
        </html>
        """

        # Send each recipient individually
        for idx, recipient in enumerate(recipients, start=1):
            payload = {
                "from": {"email": MAILERSEND_FROM_EMAIL, "name": MAILERSEND_FROM_NAME},
                "to": [{"email": recipient}],
                "subject": subject,
                "text": text,
                "html": html_template
            }

            # Debug: print payload for each send
            print(f"Sending email {idx} to {recipient} with payload:", payload)

            response = requests.post("https://api.mailersend.com/v1/email", json=payload, headers=headers)

            if response.status_code in [200, 202]:
                sent_count += 1
            else:
                errors.append(f"{recipient}: {response.text}")

        if errors:
            flash(f"Some emails failed: {errors}", "danger")
        else:
            flash(f"Successfully sent {sent_count} emails!", "success")

        return redirect(url_for("index"))

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
