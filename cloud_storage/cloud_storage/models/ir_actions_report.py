from odoo import models

class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    def _render_qweb_pdf(self, report_ref, res_ids=None, data=None):
        # Assurez-vous que res_ids est une liste
        if not isinstance(res_ids, list):
            res_ids = [res_ids]
        
        # move attachments for the given records after pdf creation
        # only not yet cloud attachments will be moved
        res = super()._render_qweb_pdf(report_ref, res_ids, data)
        attachments = self.env['ir.attachment'].search([
            ('res_model', '=', self._get_report(report_ref).model),
            ('res_id', 'in', res_ids),
        ])
        attachments.move_to_cloud()
        return res
