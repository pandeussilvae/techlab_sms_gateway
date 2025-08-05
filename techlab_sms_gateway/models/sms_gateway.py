import json
import logging
import requests
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.queue_job.job import job

_logger = logging.getLogger(__name__)


class SmsGateway(models.Model):
    _name = 'sms.gateway'
    _description = 'SMS Gateway Configuration'
    _order = 'name'

    name = fields.Char(
        string='Gateway Name',
        required=True,
        help='Name of the SMS gateway'
    )
    url = fields.Char(
        string='Gateway URL',
        required=True,
        help='API endpoint URL for the SMS gateway'
    )
    method = fields.Selection([
        ('GET', 'GET'),
        ('POST', 'POST')
    ], string='HTTP Method', default='POST', required=True)
    message_param = fields.Char(
        string='Message Parameter',
        required=True,
        default='message',
        help='Parameter name for the SMS message content'
    )
    recipient_param = fields.Char(
        string='Recipient Parameter',
        required=True,
        default='phone',
        help='Parameter name for the phone number'
    )
    api_key_param = fields.Char(
        string='API Key Parameter',
        help='Parameter name for the API key (optional)'
    )
    api_key_value = fields.Char(
        string='API Key Value',
        help='API key value (optional)'
    )
    headers = fields.Text(
        string='HTTP Headers',
        help='HTTP headers in JSON format',
        default='{"Content-Type": "application/json"}'
    )
    params_template = fields.Text(
        string='Parameters Template',
        required=True,
        help='Template for query parameters or JSON body. Use {message}, {phone}, {api_key} placeholders',
        default='{"message": "{message}", "phone": "{phone}"}'
    )
    active = fields.Boolean(
        string='Active',
        default=True
    )
    is_default = fields.Boolean(
        string='Default Gateway',
        help='Set as default gateway for SMS sending'
    )
    log_count = fields.Integer(
        string='Log Count',
        compute='_compute_log_count'
    )

    @api.depends('log_count')
    def _compute_log_count(self):
        for gateway in self:
            gateway.log_count = self.env['sms.gateway.log'].search_count([
                ('gateway_id', '=', gateway.id)
            ])

    @api.constrains('headers')
    def _check_headers_format(self):
        for record in self:
            if record.headers:
                try:
                    json.loads(record.headers)
                except json.JSONDecodeError:
                    raise ValidationError(_('Headers must be in valid JSON format'))

    @api.constrains('is_default')
    def _check_single_default(self):
        if self.is_default:
            other_defaults = self.search([
                ('is_default', '=', True),
                ('id', '!=', self.id)
            ])
            if other_defaults:
                raise ValidationError(_('Only one gateway can be set as default'))

    def _prepare_request_params(self, message, phone_number):
        """Prepare request parameters from template"""
        self.ensure_one()
        
        # Prepare substitution values
        substitutions = {
            'message': message,
            'phone': phone_number,
            'api_key': self.api_key_value or '',
        }
        
        # Replace placeholders in params template
        params_str = self.params_template
        for key, value in substitutions.items():
            params_str = params_str.replace('{' + key + '}', str(value))
        
        # Parse as JSON if it looks like JSON, otherwise treat as query string
        try:
            params = json.loads(params_str)
        except json.JSONDecodeError:
            # If not valid JSON, treat as query string format
            params = {}
            for param in params_str.split('&'):
                if '=' in param:
                    key, value = param.split('=', 1)
                    params[key] = value
        
        return params

    def _prepare_headers(self):
        """Prepare HTTP headers"""
        self.ensure_one()
        headers = {}
        if self.headers:
            try:
                headers = json.loads(self.headers)
            except json.JSONDecodeError:
                _logger.warning('Invalid JSON in headers for gateway %s', self.name)
        return headers

    def _send_sms_request(self, message, phone_number):
        """Send SMS request synchronously"""
        self.ensure_one()
        
        if not self.active:
            raise UserError(_('Gateway %s is not active') % self.name)
        
        # Prepare request parameters
        params = self._prepare_request_params(message, phone_number)
        headers = self._prepare_headers()
        
        try:
            if self.method == 'GET':
                response = requests.get(
                    self.url,
                    params=params,
                    headers=headers,
                    timeout=30
                )
            else:  # POST
                if headers.get('Content-Type') == 'application/json':
                    response = requests.post(
                        self.url,
                        json=params,
                        headers=headers,
                        timeout=30
                    )
                else:
                    response = requests.post(
                        self.url,
                        data=params,
                        headers=headers,
                        timeout=30
                    )
            
            response.raise_for_status()
            return {
                'success': True,
                'status_code': response.status_code,
                'response_body': response.text
            }
            
        except requests.exceptions.RequestException as e:
            _logger.error('SMS sending failed for gateway %s: %s', self.name, str(e))
            return {
                'success': False,
                'status_code': getattr(e.response, 'status_code', 0) if hasattr(e, 'response') else 0,
                'response_body': str(e)
            }

    @job
    def send_sms_async(self, message, phone_number, model=None, res_id=None):
        """Send SMS asynchronously with queue_job"""
        self.ensure_one()
        
        _logger.info(
            'Sending SMS via gateway %s to %s for model %s, res_id %s',
            self.name, phone_number, model, res_id
        )
        
        # Send the SMS
        result = self._send_sms_request(message, phone_number)
        
        # Log the result
        log_vals = {
            'gateway_id': self.id,
            'message': message,
            'phone_number': phone_number,
            'status': 'success' if result['success'] else 'error',
            'response_code': str(result['status_code']),
            'response_body': result['response_body'],
            'timestamp': fields.Datetime.now(),
            'res_model': model,
            'res_id': res_id,
        }
        self.env['sms.gateway.log'].create(log_vals)
        
        # Post message to chatter if model and res_id are provided
        if model and res_id and result['success']:
            try:
                record = self.env[model].browse(res_id)
                if record.exists():
                    record.message_post(
                        body=_('SMS sent to %s: %s') % (phone_number, message),
                        subject=_('SMS Sent'),
                        message_type='comment'
                    )
            except Exception as e:
                _logger.warning('Failed to post message to chatter: %s', str(e))
        
        return result

    def action_view_logs(self):
        """Action to view SMS logs for this gateway"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('SMS Logs'),
            'res_model': 'sms.gateway.log',
            'view_mode': 'tree,form',
            'domain': [('gateway_id', '=', self.id)],
            'context': {'default_gateway_id': self.id}
        }

    def action_test_sms(self):
        """Action to open SMS test wizard"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Test SMS'),
            'res_model': 'sms.test.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_gateway_id': self.id}
        }

    @api.model
    def get_default_gateway(self):
        """Get the default SMS gateway"""
        default_gateway = self.search([('is_default', '=', True)], limit=1)
        if not default_gateway:
            default_gateway = self.search([('active', '=', True)], limit=1)
        return default_gateway