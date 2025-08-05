from odoo import models, api, _


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    def action_send_sms(self):
        """Action to send SMS to lead"""
        self.ensure_one()
        
        # Get phone number (prefer mobile, fallback to phone)
        phone_number = self.mobile or self.phone
        
        if not phone_number:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'warning',
                    'message': _('No phone number found for lead %s') % self.name,
                    'sticky': False,
                }
            }
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Send SMS'),
            'res_model': 'send.sms.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_phone_number': phone_number,
                'default_res_model': self._name,
                'default_res_id': self.id,
                'default_partner_name': self.name,
            }
        }