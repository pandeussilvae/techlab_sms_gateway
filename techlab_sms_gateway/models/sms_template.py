import re
import logging
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class SmsTemplate(models.Model):
    _name = 'sms.template'
    _description = 'SMS Template'
    _order = 'name'

    name = fields.Char(
        string='Template Name',
        required=True,
        help='Name of the SMS template'
    )
    body = fields.Text(
        string='Message Body',
        required=True,
        help='SMS message content with placeholders like ${object.name} or ${object.phone}'
    )
    model_id = fields.Many2one(
        'ir.model',
        string='Model',
        required=True,
        help='Model this template applies to'
    )
    model_name = fields.Char(
        string='Model Name',
        related='model_id.model',
        store=True,
        readonly=True
    )
    gateway_id = fields.Many2one(
        'sms.gateway',
        string='Default Gateway',
        help='Default gateway to use with this template'
    )
    active = fields.Boolean(
        string='Active',
        default=True
    )

    @api.constrains('body')
    def _check_body_placeholders(self):
        """Validate that placeholders in body are properly formatted"""
        for template in self:
            if template.body:
                # Check for malformed placeholders
                malformed = re.findall(r'\$\{[^}]*$|\$\{[^}]*\{|\}[^$]*\}', template.body)
                if malformed:
                    raise ValidationError(
                        _('Template body contains malformed placeholders. '
                          'Use ${object.field_name} format.')
                    )

    def render_sms(self, record):
        """Render SMS message with object values"""
        self.ensure_one()
        
        if not record:
            return self.body
        
        # Check if record model matches template model
        if record._name != self.model_name:
            _logger.warning(
                'Record model %s does not match template model %s',
                record._name, self.model_name
            )
        
        # Render the template
        rendered_message = self.body
        
        # Find all placeholders in the format ${object.field_name}
        placeholders = re.findall(r'\$\{object\.([^}]+)\}', self.body)
        
        for placeholder in placeholders:
            try:
                # Get field value from record
                field_parts = placeholder.split('.')
                value = record
                
                for part in field_parts:
                    if hasattr(value, part):
                        value = getattr(value, part)
                        # Handle Many2one fields
                        if hasattr(value, 'name'):
                            value = value.name
                    else:
                        value = ''
                        break
                
                # Convert to string
                if value is None or value is False:
                    value = ''
                else:
                    value = str(value)
                
                # Replace placeholder with value
                placeholder_pattern = r'\$\{object\.' + re.escape(placeholder) + r'\}'
                rendered_message = re.sub(placeholder_pattern, value, rendered_message)
                
            except Exception as e:
                _logger.warning('Error rendering placeholder %s: %s', placeholder, str(e))
                # Leave placeholder as is if there's an error
                continue
        
        return rendered_message

    def action_test_render(self):
        """Action to test template rendering"""
        self.ensure_one()
        
        # Find a sample record of the template's model
        sample_record = self.env[self.model_name].search([], limit=1)
        
        if not sample_record:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'warning',
                    'message': _('No records found for model %s to test template rendering') % self.model_id.name,
                    'sticky': False,
                }
            }
        
        rendered_message = self.render_sms(sample_record)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'title': _('Template Test'),
                'message': _('Rendered message: %s') % rendered_message,
                'sticky': True,
            }
        }

    @api.model
    def get_templates_for_model(self, model_name):
        """Get all active templates for a specific model"""
        return self.search([
            ('model_name', '=', model_name),
            ('active', '=', True)
        ])