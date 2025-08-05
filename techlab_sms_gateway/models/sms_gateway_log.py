import logging
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class SmsGatewayLog(models.Model):
    _name = 'sms.gateway.log'
    _description = 'SMS Gateway Log'
    _order = 'timestamp desc'
    _rec_name = 'display_name'

    gateway_id = fields.Many2one(
        'sms.gateway',
        string='Gateway',
        required=True,
        ondelete='cascade'
    )
    message = fields.Text(
        string='Message',
        required=True
    )
    phone_number = fields.Char(
        string='Phone Number',
        required=True
    )
    status = fields.Selection([
        ('success', 'Success'),
        ('error', 'Error')
    ], string='Status', required=True)
    response_code = fields.Char(
        string='Response Code'
    )
    response_body = fields.Text(
        string='Response Body'
    )
    timestamp = fields.Datetime(
        string='Timestamp',
        required=True,
        default=fields.Datetime.now
    )
    res_model = fields.Char(
        string='Related Model',
        help='Model name of the related record'
    )
    res_id = fields.Integer(
        string='Related Record ID',
        help='ID of the related record'
    )
    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
        store=True
    )
    record_ref = fields.Reference(
        string='Related Record',
        selection='_selection_target_model',
        compute='_compute_record_ref'
    )

    @api.depends('gateway_id', 'phone_number', 'timestamp')
    def _compute_display_name(self):
        for log in self:
            log.display_name = _('%s - %s (%s)') % (
                log.gateway_id.name or '',
                log.phone_number or '',
                log.timestamp.strftime('%Y-%m-%d %H:%M:%S') if log.timestamp else ''
            )

    def _selection_target_model(self):
        """Get available models for reference field"""
        models = self.env['ir.model'].search([])
        return [(model.model, model.name) for model in models]

    @api.depends('res_model', 'res_id')
    def _compute_record_ref(self):
        for log in self:
            if log.res_model and log.res_id:
                try:
                    log.record_ref = '%s,%s' % (log.res_model, log.res_id)
                except Exception:
                    log.record_ref = False
            else:
                log.record_ref = False

    def action_view_related_record(self):
        """Action to view the related record"""
        self.ensure_one()
        if not self.res_model or not self.res_id:
            return False
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Related Record'),
            'res_model': self.res_model,
            'res_id': self.res_id,
            'view_mode': 'form',
            'target': 'current'
        }