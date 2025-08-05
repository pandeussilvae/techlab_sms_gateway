from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SmsTestWizard(models.TransientModel):
    _name = 'sms.test.wizard'
    _description = 'SMS Test Wizard'

    gateway_id = fields.Many2one(
        'sms.gateway',
        string='Gateway',
        required=True,
        help='SMS gateway to test'
    )
    phone_number = fields.Char(
        string='Phone Number',
        required=True,
        help='Phone number to send test SMS to'
    )
    message = fields.Text(
        string='Message',
        required=True,
        default='This is a test SMS from TechLab SMS Gateway.',
        help='Test message content'
    )

    @api.onchange('gateway_id')
    def _onchange_gateway_id(self):
        """Update form when gateway changes"""
        if not self.gateway_id:
            return
        
        # You could add gateway-specific default messages here
        if not self.message:
            self.message = 'This is a test SMS from TechLab SMS Gateway.'

    def action_send_test_sms(self):
        """Send test SMS using selected gateway"""
        self.ensure_one()
        
        if not self.gateway_id:
            raise UserError(_('Please select a gateway'))
        
        if not self.phone_number:
            raise UserError(_('Please enter a phone number'))
        
        if not self.message:
            raise UserError(_('Please enter a message'))
        
        # Send SMS asynchronously
        try:
            self.gateway_id.with_delay().send_sms_async(
                message=self.message,
                phone_number=self.phone_number,
                model=None,
                res_id=None
            )
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'success',
                    'title': _('SMS Test'),
                    'message': _('Test SMS has been queued for sending to %s via %s') % (
                        self.phone_number, self.gateway_id.name
                    ),
                    'sticky': False,
                }
            }
            
        except Exception as e:
            raise UserError(_('Failed to send test SMS: %s') % str(e))