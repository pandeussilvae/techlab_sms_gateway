# TechLab SMS Gateway - Module Structure

## Complete Module Documentation

This document provides a comprehensive overview of the `techlab_sms_gateway` module structure and implementation.

## File Structure

```
techlab_sms_gateway/
├── __init__.py
├── __manifest__.py
├── README.md
├── MODULE_STRUCTURE.md
├── demo_setup.py
├── models/
│   ├── __init__.py
│   ├── sms_gateway.py          # Main gateway model
│   ├── sms_gateway_log.py      # Logging model
│   ├── sms_template.py         # Template model
│   ├── res_partner.py          # Partner extension
│   └── crm_lead.py             # Lead extension
├── wizard/
│   ├── __init__.py
│   ├── sms_test_wizard.py      # Gateway test wizard
│   ├── send_sms_wizard.py      # SMS sending wizard
│   ├── sms_test_wizard_views.xml
│   └── send_sms_wizard_views.xml
├── views/
│   ├── sms_gateway_views.xml
│   ├── sms_template_views.xml
│   ├── sms_gateway_log_views.xml
│   ├── res_partner_views.xml
│   ├── crm_lead_views.xml
│   └── menu_views.xml
├── security/
│   └── ir.model.access.csv
└── static/
    └── description/
        ├── index.html
        └── icon.png
```

## Models Overview

### 1. `sms.gateway` - Gateway Configuration
**File**: `models/sms_gateway.py`

**Purpose**: Configure external SMS API gateways

**Key Fields**:
- `name`: Gateway name
- `url`: API endpoint
- `method`: HTTP method (GET/POST)
- `message_param`: Parameter name for message
- `recipient_param`: Parameter name for phone number
- `api_key_param/api_key_value`: API authentication
- `headers`: HTTP headers (JSON format)
- `params_template`: Request template with placeholders
- `active`: Enable/disable gateway
- `is_default`: Default gateway flag

**Key Methods**:
- `_send_sms_request()`: Synchronous SMS sending
- `send_sms_async()`: Asynchronous SMS sending with @job decorator
- `get_default_gateway()`: Get default gateway

### 2. `sms.gateway.log` - SMS Logs
**File**: `models/sms_gateway_log.py`

**Purpose**: Track all sent SMS messages

**Key Fields**:
- `gateway_id`: Related gateway
- `message`: SMS content
- `phone_number`: Recipient phone
- `status`: success/error
- `response_code/response_body`: API response
- `timestamp`: When sent
- `res_model/res_id`: Related record reference

### 3. `sms.template` - SMS Templates
**File**: `models/sms_template.py`

**Purpose**: Reusable SMS templates with dynamic content

**Key Fields**:
- `name`: Template name
- `body`: Message template with ${object.field} placeholders
- `model_id`: Associated Odoo model
- `gateway_id`: Default gateway

**Key Methods**:
- `render_sms()`: Render template with record data
- `get_templates_for_model()`: Get templates for specific model

### 4. Model Extensions
**Files**: `models/res_partner.py`, `models/crm_lead.py`

**Purpose**: Add SMS functionality to existing models

**Added Methods**:
- `action_send_sms()`: Open SMS wizard for the record

## Wizards

### 1. `sms.test.wizard` - Gateway Testing
**File**: `wizard/sms_test_wizard.py`

**Purpose**: Test gateway configurations

**Features**:
- Select gateway to test
- Enter test phone number and message
- Send test SMS asynchronously

### 2. `send.sms.wizard` - SMS Sending
**File**: `wizard/send_sms_wizard.py`

**Purpose**: Send SMS with template support

**Features**:
- Gateway selection
- Template selection (filtered by model)
- Phone number pre-filled from record
- Message editing with template rendering
- Context-aware defaults

## Views and Interface

### Menu Structure
```
SMS (Main Menu)
├── Gateway SMS        # Manage gateways
├── Template SMS       # Manage templates
└── Log SMS           # View sent messages
```

### Form Enhancements
- **Partners**: "Send SMS" button in form view
- **Leads**: "Send SMS" button in form view
- **Gateways**: "Test SMS" button and "Logs" smart button

## Technical Features

### Queue Job Integration
```python
@job
def send_sms_async(self, message, phone_number, model=None, res_id=None):
    # Asynchronous SMS sending
    # Automatic logging
    # Chatter integration
```

### Template System
- Placeholder format: `${object.field_name}`
- Nested field support: `${object.partner_id.name}`
- Safe rendering with error handling
- Model-specific templates

### Error Handling
- Request timeout (30 seconds)
- HTTP error handling
- Detailed error logging
- Graceful failure handling

### Security Model
- **System Admin**: Full CRUD access
- **Users**: Read-only access to gateways/logs
- **All Users**: Can use wizards and send SMS

## Configuration Examples

### Generic REST API
```json
Headers: {"Content-Type": "application/json"}
Template: {"message": "{message}", "phone": "{phone}"}
```

### Twilio
```
URL: https://api.twilio.com/2010-04-01/Accounts/SID/Messages.json
Method: POST
Headers: {"Authorization": "Basic base64(sid:token)"}
Template: Body={message}&To={phone}&From=+1234567890
```

### Vonage (Nexmo)
```json
Headers: {"Content-Type": "application/json"}
Template: {
  "from": "Brand",
  "to": "{phone}",
  "text": "{message}",
  "api_key": "{api_key}"
}
```

## Extensibility

### Custom Gateway Logic
```python
class SmsGateway(models.Model):
    _inherit = 'sms.gateway'
    
    def _prepare_custom_params(self, message, phone):
        # Gateway-specific customization
        pass
```

### Custom Templates
```python
class SmsTemplate(models.Model):
    _inherit = 'sms.template'
    
    def render_sms(self, record):
        rendered = super().render_sms(record)
        # Custom placeholder processing
        return rendered
```

## Installation Notes

1. **Dependencies**: Requires `queue_job` module
2. **Python Packages**: Uses `requests` for HTTP calls
3. **Permissions**: Ensure queue workers are running
4. **Configuration**: Set up at least one gateway before use

## Best Practices

1. **Testing**: Always test gateways before production use
2. **Monitoring**: Regularly check SMS logs for errors
3. **Templates**: Use templates for consistent messaging
4. **Security**: Protect API keys and credentials
5. **Rate Limiting**: Consider provider rate limits

## Troubleshooting

### Common Issues
1. **Queue not processing**: Check queue worker status
2. **Authentication errors**: Verify API credentials
3. **Template errors**: Check placeholder syntax
4. **Network issues**: Verify URL and connectivity

### Debug Steps
1. Check SMS logs for detailed error messages
2. Test gateway configuration with test wizard
3. Verify template rendering with sample data
4. Check queue job status in queue_job module

This module provides a complete, production-ready SMS gateway integration for Odoo 18 CE with proper error handling, logging, and extensibility.