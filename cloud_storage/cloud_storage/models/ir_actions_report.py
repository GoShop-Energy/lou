from odoo import models

class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    def _render_qweb_pdf(self, report_ref, res_ids=None, data=None):
        res = super()._render_qweb_pdf(report_ref, res_ids, data)
        if res_ids is None:
            res_ids = []
        elif not isinstance(res_ids, (list, tuple)):
            res_ids = [res_ids]
        attachments = self.env['ir.attachment'].search([
            ('res_model', '=', self._get_report(report_ref).model),
            ('res_id', 'in', res_ids),
        ])
        attachments.move_to_cloud()
        
        return res
        