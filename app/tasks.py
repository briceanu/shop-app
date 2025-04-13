from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

from celery import Celery
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from config import settings

app = Celery('tasks', broker='redis://localhost:6379/0')

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_USERNAME,
    MAIL_PORT=465,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

@app.task
def generate_pdf_and_send_email(order_data: dict, email: str):
    # Generate PDF in memory
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, height - 50, "Order Receipt")

    p.setFont("Helvetica", 12)
    y = height - 100
    for item in order_data["items"]:
        p.drawString(100, y, f"{item['name']} x {item['quantity']} - ${item['price']:.2f}")
        y -= 20

    p.drawString(100, y - 10, f"Total: ${order_data['total']:.2f}")
    p.showPage()
    p.save()
    buffer.seek(0)
    pdf_bytes = buffer.read()

    # Attach PDF to email
    message = MessageSchema(
        subject="Your Order Receipt",
        recipients=[email],
        body="Thank you for your order. Your receipt is attached.",
        subtype=MessageType.plain,
        attachments=[{
            "file": pdf_bytes,
            "filename": "order_receipt.pdf",
            "content_type": "application/pdf"
        }]
    )

    fm = FastMail(conf)
    fm.send_message(message)
