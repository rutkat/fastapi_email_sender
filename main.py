from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import jinja2
import logging
from pathlib import Path

app = FastAPI(title="Email Generator API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models
class EmailTemplate(BaseModel):
    template_name: str
    subject: str
    recipients: List[str]
    context: Dict[str, str]
    attachments: Optional[List[str]] = []

class EmailConfig(BaseModel):
    smtp_server: str
    smtp_port: int
    username: str
    password: str
    use_tls: bool = True

# Configuration (in production, use environment variables)
class Config:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.username = os.getenv("SMTP_USERNAME", "")
        self.password = os.getenv("SMTP_PASSWORD", "")
        self.use_tls = os.getenv("USE_TLS", "true").lower() == "true"
        self.template_dir = os.getenv("TEMPLATE_DIR", "templates")

# Template loader
class TemplateManager:
    def __init__(self, template_dir: str = "templates"):
        self.template_dir = Path(template_dir)
        self.template_dir.mkdir(exist_ok=True)

        # Setup Jinja2 environment
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.template_dir),
            autoescape=jinja2.select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )

    def get_template(self, template_name: str):
        try:
            return self.env.get_template(template_name)
        except jinja2.TemplateNotFound:
            raise HTTPException(status_code=404, detail=f"Template '{template_name}' not found")

    def list_templates(self) -> List[str]:
        template_files = []
        for file in self.template_dir.glob("*.html"):
            template_files.append(file.name)
        return template_files

# Email sender
class EmailSender:
    def __init__(self, config: EmailConfig):
        self.config = config

    def send_email(self, template: str, subject: str, recipients: List[str],
                   context: Dict[str, str], attachments: Optional[List[str]] = None):
        try:
            # Load and render template
            template_obj = template_manager.get_template(template)
            html_content = template_obj.render(**context)

            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.config.username
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = subject

            # Add HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)

            # Handle attachments if provided
            if attachments:
                for attachment_path in attachments:
                    if os.path.exists(attachment_path):
                        with open(attachment_path, 'rb') as attachment:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(attachment.read())
                            encoders.encode_base64(part)
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename= {os.path.basename(attachment_path)}'
                            )
                            msg.attach(part)

            # Send email
            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                if self.config.use_tls:
                    server.starttls()
                server.login(self.config.username, self.config.password)
                server.send_message(msg)

            logger.info(f"Email sent successfully to {recipients}")
            return {"status": "success", "message": "Email sent successfully"}

        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

# Initialize components
config = Config()
template_manager = TemplateManager(config.template_dir)
email_sender = EmailSender(EmailConfig(
    smtp_server=config.smtp_server,
    smtp_port=config.smtp_port,
    username=config.username,
    password=config.password,
    use_tls=config.use_tls
))

@app.get("/")
def read_root():
    return {"message": "Email Generator API is running"}

@app.get("/templates")
def get_templates():
    """Get list of available email templates"""
    return {"templates": template_manager.list_templates()}

@app.post("/send-email")
def send_email(email_data: EmailTemplate):
    """Send email using HTML template"""
    try:
        result = email_sender.send_email(
            template=email_data.template_name,
            subject=email_data.subject,
            recipients=email_data.recipients,
            context=email_data.context,
            attachments=email_data.attachments
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-email-html")
def generate_email_html(template_name: str, context: Dict[str, str]):
    """Generate HTML content from template without sending"""
    try:
        template_obj = template_manager.get_template(template_name)
        html_content = template_obj.render(**context)
        return {"html_content": html_content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload-template")
async def upload_template(file: UploadFile = File(...)):
    """Upload HTML template file"""
    try:
        if not file.filename.endswith('.html'):
            raise HTTPException(status_code=400, detail="Only HTML files are allowed")

        file_path = template_manager.template_dir / file.filename
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        return {"status": "success", "message": f"Template '{file.filename}' uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)