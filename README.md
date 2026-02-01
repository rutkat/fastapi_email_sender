# Email Token Generator

A FastAPI test for generating and sending emails from HTML templates using a custom domain name as the email provider.

## Features

- Generate emails from HTML templates using Jinja2 templating
- Send emails using custom domain SMTP credentials
- Support for email attachments
- Template management (list, upload, use templates)

### Installation

1. Clone the repository or download the files
2. Install the required packages:

```bash
pip install -r requirements.txt
```

3. Set up environment variables:

```bash
export SMTP_SERVER=smtp.yourdomain.com
export SMTP_PORT=587
export SMTP_USERNAME=your-email@yourdomain.com
export SMTP_PASSWORD=your-password
export USE_TLS=true
export TEMPLATE_DIR=templates
```

### Configuration

The application can be configured through environment variables:

| Environment Variable | Description | Default Value |
|----------------------|-------------|---------------|
| `SMTP_SERVER` | SMTP server hostname | "" |
| `SMTP_PORT` | SMTP server port | 587 |
| `SMTP_USERNAME` | SMTP username | "" |
| `SMTP_PASSWORD` | SMTP password | "" |
| `USE_TLS` | Enable TLS encryption | true |
| `TEMPLATE_DIR` | Directory for HTML templates | "templates" |

## Usage

### Starting the Server

```bash
python main.py
```

The server will start on `http://localhost:8000`.

### API Endpoints

#### 1. List Available Templates

```http
GET /templates
```

Response:
```json
{
  "templates": ["welcome.html", "password_reset.html"]
}
```

#### 2. Send Email

```http
POST /send-email
Content-Type: application/json

{
  "template_name": "welcome.html",
  "subject": "Welcome to Our Service!",
  "recipients": ["user@example.com"],
  "context": {
    "user_name": "John Doe",
    "company_name": "Your Company",
    "activation_link": "https://example.com/activate?token=123",
    "support_email": "support@example.com",
    "current_year": "2023",
    "company_address": "123 Main St, City, State"
  }
}
```

#### 3. Generate HTML Content (Preview)

```http
POST /generate-email-html
Content-Type: application/json

{
  "template_name": "welcome.html",
  "context": {
    "user_name": "John Doe",
    "company_name": "Your Company",
    "activation_link": "https://example.com/activate?token=123",
    "support_email": "support@example.com",
    "current_year": "2023",
    "company_address": "123 Main St, City, State"
  }
}
```

Response:
```json
{
  "html_content": "<!DOCTYPE html>...rendered HTML content...</html>"
}
```

#### 4. Upload Template

```http
POST /upload-template
Content-Type: multipart/form-data

File: template.html
```

### Example Usage with cURL

```bash
# List templates
curl http://localhost:8000/templates

# Send email
curl -X POST "http://localhost:8000/send-email" \
     -H "Content-Type: application/json" \
     -d '{
       "template_name": "welcome.html",
       "subject": "Welcome!",
       "recipients": ["user@example.com"],
       "context": {
         "user_name": "John Doe",
         "company_name": "Your Company",
         "activation_link": "https://example.com/activate?token=123",
         "support_email": "support@example.com",
         "current_year": "2023",
         "company_address": "123 Main St, City, State"
       }
     }'

# Generate HTML preview
curl -X POST "http://localhost:8000/generate-email-html" \
     -H "Content-Type: application/json" \
     -d '{
       "template_name": "welcome.html",
       "context": {
         "user_name": "John Doe",
         "company_name": "Your Company"
       }
     }'
```

## Sample Templates

The application includes two sample templates:

1. **welcome.html** - A welcome email template for new users
2. **password_reset.html** - A password reset email template

## Security Considerations

- Store SMTP credentials securely using environment variables or a secrets management system
- Use TLS for SMTP communication (enabled by default)
- Validate email addresses before sending
- Consider implementing rate limiting for email sending endpoints
- Add authentication/authorization for production use

## Troubleshooting

1. **Email Sending Fails**
   - Verify SMTP credentials and server details
   - Check if the SMTP server requires authentication
   - Ensure port and TLS settings are correct

2. **Template Not Found**
   - Check the template directory path
   - Verify the template file exists and has a .html extension
   - Ensure proper file permissions

3. **Rendering Errors**
   - Check template variable names match the context provided
   - Validate Jinja2 syntax in templates

## Extension Ideas

- Add email queue system for bulk sending
- Implement email templates with multiple language support
- Add email analytics and tracking
- Create a web interface for template management
- Add attachment handling via URL or upload

## License

This project is open source and available under the MIT License.