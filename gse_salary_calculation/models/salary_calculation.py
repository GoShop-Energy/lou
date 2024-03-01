# -*- coding: utf-8 -*-
from odoo import models, fields
from odoo.exceptions import UserError
from datetime import datetime, date

class SalaryCalculation(models.TransientModel):
    _name = 'salary.calculation.wizard'
    _description = 'Salary Calculation Wizard'

    net_salary = fields.Float('Net Salary (USD)')
    basic_salary = fields.Float('Basic Salary (USD)')
    tolerance_threshold = fields.Selection([
        ('0.1', '0.1'),
        ('0.01', '0.01'),
        ('0.001', '0.001'),
        ('0.0001', '0.0001'),
    ], string='Tolerance Threshold', required=True, default='0.01')
    struct_id = fields.Many2one('hr.payroll.structure', string='Structure', required=True)
    rule_ids = fields.One2many(related='struct_id.rule_ids', string="Salary Structure Rules")

    # Goal Seek Algorithm
    def goalSeek(self,fun, goal, x0, fTol, MaxIter=500):
        if fun(x0) == goal:
            return x0

        step_sizes = [10 ** i for i in range(-1, 5)] 
        scopes = [10 ** i for i in range(1, 6)]
        x_lb, x_ub = None, None

        for scope in scopes:
            for step_size in step_sizes:
                cA = [x0 + i * step_size for i in range(-int(scope), int(scope) + 1)]
                fA = [fun(xi) - goal for xi in cA]

                for i in range(len(fA) - 1):
                    if fA[i] * fA[i + 1] < 0:
                        x_lb, x_ub = cA[i], cA[i + 1]
                        break
                if x_lb is not None and x_ub is not None:
                    break
            if x_lb is not None and x_ub is not None:
                break

        if x_lb is None or x_ub is None:
            raise ValueError('No solution found')

        iter_num, error = 0, 10

        while iter_num < MaxIter and fTol < error:
            x_m = (x_lb + x_ub) / 2
            f_m = fun(x_m) - goal
            error = abs(f_m)

            if (fun(x_lb) - goal) * (f_m) < 0:
                x_ub = x_m
            elif (fun(x_ub) - goal) * (f_m) < 0:
                x_lb = x_m
            elif f_m == 0:
                return x_m
            else:
                raise ValueError('Failure in Bisection Method')

            iter_num += 1
            if iter_num >= MaxIter:
                raise ValueError("Maximum iteration limit exceeded") 

        return x_m
    
    # Get Net Salary from the basic salary
    def _get_net_salary(self, wage_salary):
        net_salary = 0.0
        line_vals = []
        for payslip in self:
            #  Is the employee exist?
            employee_ = self.env['hr.employee'].search([
                ('name', '=', 'Demo')
            ], limit=1)
            employee = None
            if not employee_:
                employee = self.env['hr.employee'].create({'name': 'Demo'})
            else:
                employee = employee_
            
            contract_ = self.env['hr.contract'].search([
                ('employee_id', '=', employee.id)
            ], limit=1)
            contract = None 
            if not contract_:
                contract = self.env['hr.contract'].create({
                    'date_start': date(2018, 1, 1),
                    'date_end': date(2018, 2, 1),
                    'name': 'Contract for %s' % employee.name,
                    'wage': 5000.0,
                    'state': 'open',
                    'employee_id': employee.id,
                    'structure_type_id': self.struct_id.type_id.id,
                    'date_generated_from': datetime(2018, 1, 1, 0, 0),
                    'date_generated_to': datetime(2018, 1, 1, 0, 0),
                    'work_entry_source': 'attendance',
                })
            else:
                contract = contract_

            payslip_ = self.env['hr.payslip'].search([
                ('employee_id', '=', employee.id)
            ], limit=1)

            py = None

            if not payslip_:
                py = self.env['hr.payslip'].create({
                    'employee_id': employee.id,
                    'contract_id': contract.id,
                    'struct_id': self.struct_id.id,
                    'date_from': date(2018, 1, 1),
                    'date_to': date(2018, 1, 31),
                    'name': "Demo Payslip",
                    'company_id': contract.company_id.id,
                })
            else:
                py = payslip_
            
            if not py.contract_id:
                raise UserError(_("There's no contract set on payslip %s for %s. Check that there is at least a contract set on the employee form.", py.name, py.employee_id.name))

            # Update the wage salary
            save_wage = py.contract_id.wage
            py.contract_id.wage = wage_salary
            localdict = self.env.context.get('force_payslip_localdict', None)

            if localdict is None:
                localdict = py._get_localdict()

            rules_dict = localdict['rules'].dict
            result_rules_dict = localdict['result_rules'].dict

            blacklisted_rule_ids = self.env.context.get('prevent_payslip_computation_line_ids', [])

            result = {}
            for rule in sorted(payslip.rule_ids, key=lambda x: x.sequence):
                if rule.id in blacklisted_rule_ids:
                    continue
                localdict.update({
                    'result': None,
                    'result_qty': 1.0,
                    'result_rate': 100,
                    'result_name': False
                })
                if rule._satisfy_condition(localdict):
                    employee_lang = py.employee_id.sudo().address_home_id.lang
                    context = {'lang': employee_lang}
                    if rule.code in localdict['same_type_input_lines']:
                        for multi_line_rule in localdict['same_type_input_lines'][rule.code]:
                            localdict['inputs'].dict[rule.code] = multi_line_rule
                            amount, qty, rate = rule._compute_rule(localdict)
                            tot_rule = amount * qty * rate / 100.0
                            localdict = rule.category_id._sum_salary_rule_category(localdict,
                                                                                   tot_rule)
                            rule_name = py._get_rule_name(localdict, rule, employee_lang)
                            line_vals.append({
                                'sequence': rule.sequence,
                                'code': rule.code,
                                'name':  rule_name, 
                                'salary_rule_id': rule.id,
                                'contract_id': localdict['contract'].id,
                                'employee_id': localdict['employee'].id,
                                'amount': amount,
                                'quantity': qty,
                                'rate': rate,
                                'slip_id': py.id,
                            })
                    else:
                        amount, qty, rate = rule._compute_rule(localdict)
                        previous_amount = rule.code in localdict and localdict[rule.code] or 0.0
                        tot_rule = amount * qty * rate / 100.0
                        localdict[rule.code] = tot_rule
                        result_rules_dict[rule.code] = {'total': tot_rule, 'amount': amount, 'quantity': qty}
                        rules_dict[rule.code] = rule
                        localdict = rule.category_id._sum_salary_rule_category(localdict, tot_rule - previous_amount)
                        rule_name = py._get_rule_name(localdict, rule, employee_lang)
                        result[rule.code] = {
                            'sequence': rule.sequence,
                            'code': rule.code,
                            'name': rule_name,
                            'salary_rule_id': rule.id,
                            'contract_id': localdict['contract'].id,
                            'employee_id': localdict['employee'].id,
                            'amount': amount,
                            'quantity': qty,
                            'rate': rate,
                            'slip_id': py.id,
                        }
            line_vals += list(result.values())
            for line in line_vals:
                if line['code'] == 'NET':
                    net_salary = line['amount']
            py.contract_id.wage = save_wage
        return net_salary
    
    # Calculate the basic salary from the net salary
    def calculate_salary(self):
        x0=0.0
        for salary_calculation in self:
            fTol = float(salary_calculation.tolerance_threshold)
            basic = self.goalSeek(self._get_net_salary,self.net_salary,x0,fTol)
            salary_calculation.basic_salary = basic

        return {
            'name': 'Salary Calculation',
            'type': 'ir.actions.act_window',
            'res_model': 'salary.calculation.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'view_id': self.env.ref('gse_salary_calculation.view_salary_calculation_wizard_form').id,
            'view_type': 'form',
            'target': 'new'
        }
    
    # Apply the basic salary to the current contract
    def apply_basic_salary(self):
        contract_id = self.env.context.get('current_contract_id') 
        contract = self.env['hr.contract'].browse(contract_id)
        number_of_hours = contract.resource_calendar_id.full_time_required_hours
        if contract.wage_type == 'hourly':
            contract.hourly_wage = self.basic_salary / number_of_hours
        else:
            contract.wage = self.basic_salary
        