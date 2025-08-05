# TechLab SMS Gateway

Generic SMS Gateway integration module for Odoo 18 Community Edition with queue_job support.

## Features

- **Multiple SMS Gateways**: Configure multiple SMS gateways with different APIs
- **Asynchronous Processing**: Uses queue_job for reliable SMS sending
- **SMS Templates**: Create reusable templates with dynamic content
- **Complete Logging**: Track all sent messages with detailed logs
- **CRM Integration**: Send SMS from Partner and Lead records
- **Test Tools**: Built-in test wizard for gateway verification

## Installation

1. Ensure you have the `queue_job` module installed
2. Copy this module to your Odoo addons directory
3. Update your module list
4. Install the `techlab_sms_gateway` module

## Dependencies

- `base`
- `queue_job`
- `crm`

## Configuration

### Setting up SMS Gateways

1. Go to **SMS → Gateway SMS**
2. Create a new gateway with the following information:
   - **Name**: Descriptive name for your gateway
   - **URL**: API endpoint of your SMS provider
   - **Method**: HTTP method (GET or POST)
   - **Parameters**: Configure parameter names for message, phone, and API key
   - **Headers**: HTTP headers in JSON format
   - **Parameters Template**: Request template with placeholders

### Example Configuration

For a generic REST API:

```json
Headers:
{
    "Content-Type": "application/json",
    "Authorization": "Bearer your-api-key"
}

Parameters Template:
{
    "message": "{message}",
    "to": "{phone}",
    "from": "YourCompany"
}
```

### Creating SMS Templates

1. Go to **SMS → Template SMS**
2. Create templates with placeholders like `${object.name}`, `${object.phone}`, etc.
3. Assign templates to specific models (res.partner, crm.lead, etc.)

## Usage

### Sending SMS from Records

1. Open a Partner or Lead record
2. Click the **Send SMS** button
3. Select a gateway and template (optional)
4. Customize the message if needed
5. Click **Send SMS**

### Testing Gateways

1. Go to **SMS → Gateway SMS**
2. Open a gateway record
3. Click **Test SMS**
4. Enter a phone number and test message
5. Click **Send Test SMS**

### Monitoring Logs

1. Go to **SMS → Log SMS**
2. View all sent messages with their status
3. Check response details for debugging

## Technical Details

### Models

- `sms.gateway`: Gateway configuration
- `sms.gateway.log`: SMS sending logs
- `sms.template`: SMS templates with placeholders
- `sms.test.wizard`: Gateway testing wizard
- `send.sms.wizard`: SMS sending wizard

### Key Methods

- `sms.gateway._send_sms_request()`: Synchronous SMS sending
- `sms.gateway.send_sms_async()`: Asynchronous SMS sending with queue_job
- `sms.template.render_sms()`: Template rendering with object values

### Queue Job Integration

The module uses the `@job` decorator for asynchronous SMS sending:

```python
@job
def send_sms_async(self, message, phone_number, model=None, res_id=None):
    # Send SMS and log results
    # Post to chatter if model/res_id provided
```

## Security

- System administrators have full access to all SMS features
- Regular users can view gateways and logs but cannot modify them
- All users can use the SMS sending wizards

## Extending the Module

### Adding Custom Gateways

You can extend the `sms.gateway` model to add gateway-specific logic:

```python
class SmsGateway(models.Model):
    _inherit = 'sms.gateway'
    
    def _prepare_custom_gateway_params(self, message, phone):
        # Custom logic for specific gateway
        pass
```

### Custom Template Placeholders

Extend the `sms.template` model to add custom placeholder processing:

```python
class SmsTemplate(models.Model):
    _inherit = 'sms.template'
    
    def render_sms(self, record):
        rendered = super().render_sms(record)
        # Add custom placeholder processing
        return rendered
```

## Support

For support and customization requests, contact TechLab.

## License

LGPL-3