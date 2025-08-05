from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SendSmsWizard(models.TransientModel):
    _name = 'send.sms.wizard'
    _description = 'Send SMS Wizard'

    gateway_id = fields.Many2one(
        'sms.gateway',
        string='Gateway',
        required=True,
        help='SMS gateway to use'
    )
    template_id = fields.Many2one(
        'sms.template',
        string='Template',
        help='SMS template to use (optional)'
    )
    phone_number = fields.Char(
        string='Phone Number',
        required=True,
        help='Phone number to send SMS to'
    )
    message = fields.Text(
        string='Message',
        required=True,
        help='SMS message content'
    )
    res_model = fields.Char(
        string='Related Model',
        help='Model of the related record'
    )
    res_id = fields.Integer(
        string='Related Record ID',
        help='ID of the related record'
    )
    partner_name = fields.Char(
        string='Contact Name',
        readonly=True,
        help='Name of the contact for display purposes'
    )

    @api.model
    def default_get(self, fields_list):
        """Set default values"""
        res = super().default_get(fields_list)
        
        # Set default gateway
        if 'gateway_id' in fields_list and not res.get('gateway_id'):
            default_gateway = self.env['sms.gateway'].get_default_gateway()
            if default_gateway:
                res['gateway_id'] = default_gateway.id
        
        # If we have res_model and res_id, try to find templates
        if res.get('res_model') and 'template_id' in fields_list:
            templates = self.env['sms.template'].get_templates_for_model(res['res_model'])
            if templates:
                # Use the first template as default
                res['template_id'] = templates[0].id
                # If we also have the record, render the template
                if res.get('res_id'):
                    try:
                        record = self.env[res['res_model']].browse(res['res_id'])
                        if record.exists():
                            rendered_message = templates[0].render_sms(record)
                            res['message'] = rendered_message
                    except Exception:
                        pass
        
        return res

    @api.onchange('template_id')
    def _onchange_template_id(self):
        """Update message when template changes"""
        if self.template_id and self.res_model and self.res_id:
            try:
                record = self.env[self.res_model].browse(self.res_id)
                if record.exists():
                    self.message = self.template_id.render_sms(record)
                    # Also update gateway if template has a default gateway
                    if self.template_id.gateway_id:
                        self.gateway_id = self.template_id.gateway_id
            except Exception:
                pass
        elif self.template_id:
            # If no record context, just use the template body
            self.message = self.template_id.body
            if self.template_id.gateway_id:
                self.gateway_id = self.template_id.gateway_id

    @api.onchange('gateway_id')
    def _onchange_gateway_id(self):
        """Filter templates by gateway when gateway changes"""
        if self.gateway_id and self.res_model:
            # Get templates for this model and gateway
            domain = [
                ('model_name', '=', self.res_model),
                ('active', '=', True),
                ('gateway_id', '=', self.gateway_id.id)
            ]
            templates = self.env['sms.template'].search(domain)
            if templates and not self.template_id:
                self.template_id = templates[0]

    def action_send_sms(self):
        """Send SMS to the specified number"""
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
                model=self.res_model,
                res_id=self.res_id
            )
            
            contact_info = self.partner_name or self.phone_number
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'success',
                    'title': _('SMS Sent'),
                    'message': _('SMS has been queued for sending to %s via %s') % (
                        contact_info, self.gateway_id.name
                    ),
                    'sticky': False,
                }
            }
            
        except Exception as e:
            raise UserError(_('Failed to send SMS: %s') % str(e))

    @api.model
    def get_available_templates(self):
        """Get available templates for the current model"""
        if self.res_model:
            return self.env['sms.template'].get_templates_for_model(self.res_model)
        return self.env['sms.template'].browse()