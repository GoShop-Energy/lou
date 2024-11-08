import ast
import logging

from odoo import api, fields, models, Command
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare

logger = logging.getLogger(__name__)


class Bonus(models.Model):
    _name = 'gse.bonus'
    _description = 'Bonus'
    _order = 'id desc'

    timesheet_id = fields.Many2one('account.analytic.line', copy=True)
    so_line = fields.Many2one('sale.order.line', required=True, copy=True)
    employee_id = fields.Many2one('hr.employee', required=True, copy=True)
    order_id = fields.Many2one(related='so_line.order_id', store=True, required=True, copy=True)
    order_date = fields.Datetime(related='order_id.date_order', store=True)
    company_id = fields.Many2one(related='order_id.company_id')
    currency_id = fields.Many2one(related='company_id.currency_id')
    amount = fields.Monetary(string='Amount', required=True)
    state = fields.Selection(related='order_id.bonus_state')

    vendor_bill_move_ids = fields.Many2many(
        'account.move', compute='_compute_vendor_bill_move_ids',
        help="Vendor bill but also Vendor bill credit note")
    vendor_bill_move_count = fields.Integer(string='# Invoices', compute='_compute_vendor_bill_move_count', groups="account.group_account_manager")
    vendor_bill_move_line_ids = fields.Many2many('account.move.line', ondelete='restrict')

    @api.depends('vendor_bill_move_ids')
    def _compute_vendor_bill_move_count(self):
        for bonus in self:
            bonus.vendor_bill_move_count = len(bonus.vendor_bill_move_ids)

    @api.depends('vendor_bill_move_line_ids')
    def _compute_vendor_bill_move_ids(self):
        for bonus in self:
            bonus.vendor_bill_move_ids = bonus.vendor_bill_move_line_ids.move_id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('timesheet_id'):
                # Bonus from labor
                so_line = self.env['account.analytic.line'].browse(vals['timesheet_id']).so_line.id
                if so_line != vals.get('so_line'):
                    raise UserError('This should never happen. timesheet != SO')
                vals['so_line'] = so_line
            else:
                # Bonus from transport
                if not vals.get('so_line'):
                    raise UserError('This should never happen. no SOL on bonus')

        return super().create(vals_list)

    def unlink(self):
        move_lines = self.vendor_bill_move_line_ids
        res = super().unlink()
        for line in move_lines:
            vendor_bill = line.move_id
            line.unlink()
            # Unlink the vendor bill if nothing in it anymore
            if not vendor_bill.invoice_line_ids:
                vendor_bill.write({'state': 'draft'})
                vendor_bill.unlink()
        return res

    def action_view_invoices(self):
        action = self.env['ir.actions.act_window']._for_xml_id('technicians.action_view_invoices')
        # action['display_name'] = self.name
        action['domain'] = [('id', 'in', self.vendor_bill_move_ids.ids)]
        context = action['context'].replace('active_id', str(self.id))
        action['context'] = ast.literal_eval(context)
        return action

    def generate_bonuses(self, order):
        if not order:
            return

        if not (order.date_order > fields.Datetime.from_string('2023-05-31 23:59:59')):
            # This should not but a `raise UserError()` because you still want
            # to validate SO after that date but just not generating bonuses.
            logger.info("Impossible de générer un bonus pour une SO validée avant le 1er juin 2023 (SO %s %s).", order.id, order.date_order)
            return

        order.ensure_one()

        # Check if bonuses can be created: the SO must:
        # - be fully paid
        # - be fully delivered
        # - have its related labor service tasks done (related SOL will be
        #   marked as delivered, so it should be covered by previous point)
        if any([move_state not in ('paid', 'reversed') for move_state in order.invoice_ids.mapped('payment_state')]):
            logger.info("Not all invoices are fully paid or reversed (SO %s %s).", order.id, order.date_order)
            return
        if any(line for line in order.order_line if line.product_uom_qty != line.qty_invoiced):
            logger.info("Not all products have been invoiced (SO %s %s).", order.id, order.date_order)
            return

        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        # keep only consumable + stockable products and services products which generate tasks
        for line in order.order_line.filtered(lambda line: not (line.is_downpayment or line.display_type or line.product_uom_qty == 0)):
            if line.product_id.type == 'service' and line.product_id.service_tracking != 'no':
                # As long as something different from 0 has been delivered, it's
                # ok for the bonus. Eg 30 min will be marked as 0.5/1.
                if line.qty_delivered == 0:
                    logger.info("The service line product has 0 marked as delivered (SO %s %s).", order.id, order.date_order)
                    return
            elif line.product_id.type == 'service' and line.product_id.service_policy == 'ordered_prepaid':
                # prepaid service will/could remain at 0 delivered qty but it's
                # normal and should not block the bonus
                pass
            else:
                if not float_compare(line.qty_delivered, line.product_uom_qty, precision_digits=precision) >= 0:
                    logger.info("Not all deliverable products have been delivered (SO %s %s).", order.id, order.date_order)
                    return

        involved_employees = self.env['hr.employee']

        # Generate bonus for every SOL related to a labor task
        for labor_order_line in order.order_line.filtered(
            lambda line: (
                line.product_id.service_tracking != 'no'
                and line.task_id
                and line.task_id.stage_id.with_context(lang='en_US').name == "Done"
                and not line.task_id.disallow_transport_expenses
                and line.product_id.get_bonus_rate()
            )
        ):
            labor_task = labor_order_line.task_id

            # eg 2.25 for 2h15min
            task_total_hours = labor_task.total_hours_spent
            if not task_total_hours:
                logger.info("The task has no timesheet encoded (SO %s %s).", order.id, order.date_order)
                continue
            # convert in company currency
            labor_price_subtotal = labor_order_line.currency_id._convert(
                labor_order_line.price_subtotal,
                order.company_id.currency_id,
                order.company_id,
                fields.Date.today()
            )
            # eg 300$ / 10% = 30$
            reward_to_distribute = (labor_price_subtotal * labor_order_line.product_id.get_bonus_rate()) / 100

            if not reward_to_distribute:
                logger.info("No bonus rate detected: 0%% set on product AND company rate).")
                continue

            # eg 30$ / 2.25 = 13,33$ for one hour
            one_hour_reward = reward_to_distribute / task_total_hours

            # {
            #     user_1: {
            #         timesheet_3: 40
            #         timesheet_5: 10
            #     }
            #     user_2: {
            #         timesheet_4: 30
            #     }
            # }
            total_timesheet_unit_amount = 0
            # restricted users can't access / see other users timesheet by default
            for timesheet in labor_task.sudo().timesheet_ids.filtered('unit_amount'):
                total_timesheet_unit_amount += timesheet.unit_amount

                running_contract = timesheet.employee_id.sudo().contract_ids.filtered(lambda cont: cont.state == 'open')
                if not running_contract or not running_contract[0].allow_transport_expenses:
                    logger.info("This employee isn't allowed to expense transport (set on contract) or has no running contract.")
                    continue

                if timesheet.bonuses_ids:
                    logger.info("This timesheet is already linked to a bonus")
                    continue

                # Create bonus
                bonus_amount = timesheet.unit_amount * one_hour_reward  # TODO: check if `unit_amount` in minutes?
                bonus = self.sudo().create({
                    'timesheet_id': timesheet.id,
                    'so_line': timesheet.so_line.id,
                    'employee_id': timesheet.employee_id.id,
                    'amount': bonus_amount,
                    'order_id': timesheet.order_id.id,
                })
                bonus.add_bonus_on_vendor_bill()
                involved_employees |= timesheet.employee_id            

            logger.info("Task total hours: %s, Timesheet total unit amount: %s for Task %s", task_total_hours, total_timesheet_unit_amount, labor_task.name)

            if float_compare(task_total_hours, total_timesheet_unit_amount, precision_digits=precision) != 0:
                raise UserError("Total hours spent on task does not match timesheet sum (rounded values).")

        # Generate bonus for every transport products
        if involved_employees:
            for transport_order_line in order.order_line.filtered(
                # This need to be `bonus_rate` and not `get_bonus_rate()`
                # because it would fallback on company rate if set and would
                # grant bonus on any line not linked to a task.
                # TODO: Something better that "no task"?
                lambda line: not line.task_id and line.product_id and line.product_id.bonus_rate
            ):
                # convert in company currency
                transport_total = transport_order_line.currency_id._convert(
                    transport_order_line.price_subtotal,
                    order.company_id.currency_id,
                    order.company_id,
                    fields.Date.today()
                )
                reward_per_employee = (transport_total * transport_order_line.product_id.get_bonus_rate()) / 100 / len(involved_employees)

                if not reward_per_employee:
                    # There might be no timesheet encoded, or 0% set on product AND
                    # company rate
                    continue

                # note: `involved_employees` are already ensure to have contract allowing transport expenses
                for employee in involved_employees:
                    bonus = self.sudo().create({
                        'so_line': transport_order_line.id,
                        'amount': reward_per_employee,
                        'order_id': order.id,
                        'employee_id': employee.id,
                    })
                    bonus.add_bonus_on_vendor_bill()

    def add_bonus_on_vendor_bill(self, credit_note=False):
        """ Create or update vendor bill with new bonus. """
        Move = self.env['account.move'].with_context(skip_invoice_sync=False)

        self.ensure_one()

        journal = self.order_id.company_id.bonus_journal_id
        if not journal:
            raise UserError("Aucun journal pour les bonus n'est sélectionné")
        if not journal.default_account_id:
            raise UserError("Le journal sélectionné %r pour les bonus n'a pas de `default_account_id`" % journal.name)

        partner_id = self.employee_id.work_contact_id.id
        if not partner_id:
            raise UserError("L'employé n'a pas d'adresse enregistrée.")

        move_type = 'in_refund' if credit_note else 'in_invoice'

        move = Move.search([
            ('company_id', '=', self.company_id.id),
            ('move_type', '=', move_type),
            ('partner_id', '=', partner_id),
            ('journal_id', '=', journal.id),
            ('state', '=', 'draft'),
        ], limit=1)
        if not move:
            vals = {
                'company_id': self.company_id.id,
                'move_type': move_type,
                'partner_id': partner_id,
                'invoice_date': self.write_date,
                'date': self.write_date,
                'ref': 'Commission for SO %s' % self.order_id.name,
            }
            if not credit_note:
                # if credit note, let journal be found
                vals['journal_id'] = journal.id
            move = Move.create(vals)
        move_line = self.env['account.move.line'].with_context(skip_invoice_sync=False).create({
            'move_id': move.id,
            'product_id': self.company_id.bonus_product_id.id,
            'name': 'Commission for SO %s (SOL: %s)' % (self.order_id.name, self.so_line.name),
            # bonus amount is negative if bonus from credit note, but in
            # credit note itself the line need to be positive
            'price_unit': -self.amount if credit_note else self.amount,
            'tax_ids': None,
        })
        self.vendor_bill_move_line_ids = [Command.link(move_line.id)]

    def revert(self):
        self = self.with_context(skip_invoice_sync=False)
        """ Revert a bonus:
        - If it's already paid, it should generate a vendor bill credit note
          with the same amount
        - If it's not yet paid, it should simply remove the bonus itself """
        for bonus in self:
            bonus_vendor_bill_excluded_credit_node = bonus.vendor_bill_move_line_ids.move_id.filtered(lambda m: m.move_type == 'in_invoice')
            vendor_bill_paid = bonus_vendor_bill_excluded_credit_node.payment_state == 'paid'
            if vendor_bill_paid:
                # Generate vendor bill credit note to revert bonus
                revert_bonus = bonus.sudo().copy({'amount': -bonus.amount})
                revert_bonus.add_bonus_on_vendor_bill(credit_note=True)
            else:
                # Delete bonus
                bonus.sudo().unlink()
