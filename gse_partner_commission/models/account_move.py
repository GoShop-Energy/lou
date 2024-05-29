# -*- coding: utf-8 -*-

from odoo import fields, models, _

class AccountMove(models.Model):
    _inherit = 'account.move'

    def button_cancel(self):
        res = super(AccountMove, self).button_cancel()
        self._cancel_commission()
        return res

    def _cancel_commission(self):
        for move in self.filtered(lambda m: m.state == 'cancel'):
            if move.commission_po_line_id:
                # Already has a commission PO line, create a refund line
                sign = -1
            else:
                # No commission PO line, nothing to do
                continue

            comm_by_rule = defaultdict(float)
            product = None
            order = None
            desc_lines = ""

            for line in move.invoice_line_ids:
                rule = line._get_commission_rule()
                if rule:
                    if not product:
                        product = rule.plan_id.product_id
                    if not order:
                        order = line.subscription_id
                        desc_lines += _("\n%s: from %s to %s", line.product_id.name, format_date(self.env, line.subscription_start_date),
                                        format_date(self.env, line.subscription_end_date))
                    commission = move.currency_id.round(line.price_subtotal * rule.rate / 100.0)
                    comm_by_rule[rule] += commission

            # regulate commissions
            for r, amount in comm_by_rule.items():
                if r.is_capped:
                    amount = min(amount, r.max_commission)
                    comm_by_rule[r] = amount

            total = sum(comm_by_rule.values())
            if not total:
                continue

            # build description lines
            desc = f"{_('Commission on %s') % (move.name)}, {move.partner_id.name}, {formatLang(self.env, move.amount_untaxed, currency_obj=move.currency_id)}"
            if order:
                desc += f"\n{order.name}, {desc_lines}"
                end_date_list = move.invoice_line_ids.mapped('subscription_end_date')
                start_date_list = move.invoice_line_ids.mapped('subscription_start_date')
                date_to = max([ed for ed in end_date_list if ed])
                date_from = min([sd for sd in start_date_list if sd])
                delta = relativedelta(date_to + relativedelta(days=1), date_from)
                n_months = delta.years * 12 + delta.months + delta.days // 30
                if n_months:
                    desc += _(' (%d month(s))', n_months)

            purchase = move._get_commission_purchase_order()

            line = self.env['purchase.order.line'].sudo().create({
                'name': desc,
                'product_id': product.id,
                'product_qty': 1,
                'price_unit': total * sign,
                'product_uom': product.uom_id.id,
                'date_planned': fields.Datetime.now(),
                'order_id': purchase.id,
                'qty_received': 1,
            })

            move.commission_po_line_id = line
            msg_body = 'Commission canceled. Invoice: %s. Amount: %s.' % (
                move._get_html_link(),
                formatLang(self.env, total, currency_obj=move.currency_id),
            )
            purchase.message_post(body=msg_body)
