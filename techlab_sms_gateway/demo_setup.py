"""
Demo setup script for TechLab SMS Gateway module.

This script shows example configurations that can be used to set up
the SMS gateway module with sample data.

Note: This is for demonstration purposes only. In a real deployment,
you would configure actual SMS provider details.
"""

# Example Gateway Configuration for a generic SMS API
EXAMPLE_GATEWAY_CONFIG = {
    'name': 'Demo SMS Gateway',
    'url': 'https://api.smsgateway.example.com/send',
    'method': 'POST',
    'message_param': 'message',
    'recipient_param': 'phone',
    'api_key_param': 'api_key',
    'api_key_value': 'your-api-key-here',
    'headers': '{"Content-Type": "application/json", "Authorization": "Bearer your-token"}',
    'params_template': '{"message": "{message}", "phone": "{phone}", "api_key": "{api_key}"}',
    'active': True,
    'is_default': True,
}

# Example Template for Partners
EXAMPLE_PARTNER_TEMPLATE = {
    'name': 'Partner Welcome Message',
    'body': 'Hello ${object.name}, welcome to our company! We\'re excited to work with you. Contact us at ${object.phone} if you have any questions.',
    'model_id': 'base.model_res_partner',  # Reference to res.partner model
    'active': True,
}

# Example Template for CRM Leads
EXAMPLE_LEAD_TEMPLATE = {
    'name': 'Lead Follow-up',
    'body': 'Hi ${object.contact_name}, thank you for your interest in ${object.name}. We will contact you soon at ${object.phone}.',
    'model_id': 'crm.model_crm_lead',  # Reference to crm.lead model
    'active': True,
}

# Example configurations for popular SMS providers

TWILIO_CONFIG = {
    'name': 'Twilio SMS',
    'url': 'https://api.twilio.com/2010-04-01/Accounts/YOUR_ACCOUNT_SID/Messages.json',
    'method': 'POST',
    'message_param': 'Body',
    'recipient_param': 'To',
    'headers': '{"Content-Type": "application/x-www-form-urlencoded", "Authorization": "Basic base64(account_sid:auth_token)"}',
    'params_template': 'Body={message}&To={phone}&From=+1234567890',
    'active': True,
}

NEXMO_CONFIG = {
    'name': 'Vonage (Nexmo) SMS',
    'url': 'https://rest.nexmo.com/sms/json',
    'method': 'POST',
    'message_param': 'text',
    'recipient_param': 'to',
    'api_key_param': 'api_key',
    'headers': '{"Content-Type": "application/json"}',
    'params_template': '{"from": "YourBrand", "to": "{phone}", "text": "{message}", "api_key": "{api_key}", "api_secret": "your-api-secret"}',
    'active': True,
}

TEXTMAGIC_CONFIG = {
    'name': 'TextMagic SMS',
    'url': 'https://rest.textmagic.com/api/v2/messages',
    'method': 'POST',
    'message_param': 'text',
    'recipient_param': 'phones',
    'headers': '{"Content-Type": "application/json", "X-TM-Username": "your-username", "X-TM-Key": "your-api-key"}',
    'params_template': '{"text": "{message}", "phones": "{phone}"}',
    'active': True,
}

def get_example_configs():
    """Return all example configurations"""
    return {
        'gateways': [
            EXAMPLE_GATEWAY_CONFIG,
            TWILIO_CONFIG,
            NEXMO_CONFIG,
            TEXTMAGIC_CONFIG,
        ],
        'templates': [
            EXAMPLE_PARTNER_TEMPLATE,
            EXAMPLE_LEAD_TEMPLATE,
        ]
    }

if __name__ == '__main__':
    print("TechLab SMS Gateway - Demo Configuration Examples")
    print("=" * 50)
    
    configs = get_example_configs()
    
    print("\nGateway Configurations:")
    for i, gateway in enumerate(configs['gateways'], 1):
        print(f"{i}. {gateway['name']}")
        print(f"   URL: {gateway['url']}")
        print(f"   Method: {gateway['method']}")
        print()
    
    print("Template Configurations:")
    for i, template in enumerate(configs['templates'], 1):
        print(f"{i}. {template['name']}")
        print(f"   Body: {template['body'][:60]}...")
        print()