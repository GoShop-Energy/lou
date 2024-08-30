# -*- coding: utf-8 -*-

from odoo import models, api

class FollowupManualReminder(models.TransientModel):
    _inherit = 'account_followup.manual_reminder'

    def process_followup(self):
        """Add a condition to include template_id in the options.
        """
        action = super(FollowupManualReminder, self).process_followup()
        options = self._get_wizard_options()
        if self.template_id:
            options['template_id'] = self.template_id
        action = self.partner_id.execute_followup(options)
        return action or {
            'type': 'ir.actions.act_window_close',
        }