{
    'name': 'TechLab SMS Gateway',
    'version': '18.0.1.0.0',
    'category': 'Tools',
    'summary': 'Generic SMS Gateway integration with queue_job support',
    'description': """
        TechLab SMS Gateway Module
        ==========================
        
        This module provides a generic SMS gateway integration system with the following features:
        
        * Support for multiple SMS gateways
        * Asynchronous SMS sending using queue_job
        * SMS templates with placeholder support
        * Integration with partner and CRM lead records
        * Complete logging and tracking of sent messages
        * Test wizard for gateway configuration
        
        Compatible with Odoo 18 Community Edition and follows OCA standards.
    """,
    'author': 'TechLab',
    'website': 'https://www.techlab.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'queue_job',
        'crm',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/sms_gateway_views.xml',
        'views/sms_template_views.xml',
        'views/sms_gateway_log_views.xml',
        'views/res_partner_views.xml',
        'views/crm_lead_views.xml',
        'wizard/sms_test_wizard_views.xml',
        'wizard/send_sms_wizard_views.xml',
        'views/menu_views.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'external_dependencies': {
        'python': ['requests'],
    },
}