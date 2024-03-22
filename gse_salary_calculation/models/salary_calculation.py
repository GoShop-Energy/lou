# -*- coding: utf-8 -*-
from odoo import models, fields, _
from odoo.addons.hr_payroll.models import hr_payslip as hr_payslip_module 
from odoo.exceptions import UserError
from datetime import datetime, date
import numpy as np


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

    def goalSeek(self,fun,goal,x0,fTol,MaxIter=500): 
            if fun(x0)==goal:
                # print('Exact solution found')
                return x0
            # Line Search Method
            step_sizes=np.logspace(-1,4,6)
            scopes=np.logspace(1,5,5)
            x_lb=None
            x_ub=None

            vFun=np.vectorize(fun)

            for scope in scopes:
                break_nested=False
                for step_size in step_sizes:

                    cApos=np.linspace(x0,x0+step_size*scope,int(scope))
                    cAneg=np.linspace(x0,x0-step_size*scope,int(scope))

                    cA=np.concatenate((cAneg[::-1],cApos[1:]),axis=0)

                    fA=vFun(cA)-goal

                    if np.any(np.diff(np.sign(fA))):

                        index_lb=np.nonzero(np.diff(np.sign(fA)))

                        if len(index_lb[0])==1:

                            index_ub=index_lb+np.array([1])

                            x_lb=np.array(cA)[index_lb][0].item()
                            x_ub=np.array(cA)[index_ub][0].item()
                            break_nested=True
                            break
                        else: # Two or more roots possible

                            index_ub=index_lb+np.array([1])

                            print('Other solution possible at around, x0 = ', np.array(cA)[index_lb[0][1]])

                            x_lb=np.array(cA)[index_lb[0][0]].item()
                            x_ub=np.array(cA)[index_ub[0][0]].item()
                            break_nested=True
                            break

                if break_nested:
                    break
            if not x_lb or not x_ub:
                raise UserError('No solution found')

            # Bisection Method
            iter_num=0
            error=10

            while iter_num<MaxIter and fTol<error:
                
                x_m=(x_lb+x_ub)/2
                f_m=fun(x_m)-goal

                error=abs(f_m)

                if (fun(x_lb)-goal)*(f_m)<0:
                    x_ub=x_m
                elif (fun(x_ub)-goal)*(f_m)<0:
                    x_lb=x_m
                elif f_m==0:
                    print('Exact solution found')
                    return x_m
                else:
                    print('Failure in Bisection Method')
                    raise UserError('Failure in Bisection Method')
                
                iter_num+=1
                if iter_num >= MaxIter:
                    raise UserError("Maximum iteration limit exceeded")
            # print("iter_num", iter_num)
            
            return x_m  
    
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
                    # Retrieve the line name in the employee's lang
                    employee_lang = py.employee_id.sudo().address_home_id.lang
                    # This actually has an impact, don't remove this line
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
                        #check if there is already a rule computed with that code
                        previous_amount = rule.code in localdict and localdict[rule.code] or 0.0
                        #set/overwrite the amount computed for this rule in the localdict
                        tot_rule = amount * qty * rate / 100.0
                        localdict[rule.code] = tot_rule
                        result_rules_dict[rule.code] = {'total': tot_rule, 'amount': amount, 'quantity': qty}
                        rules_dict[rule.code] = rule
                        # sum the amount for its salary category
                        localdict = rule.category_id._sum_salary_rule_category(localdict, tot_rule - previous_amount)
                        rule_name = py._get_rule_name(localdict, rule, employee_lang)
                        # create/overwrite the rule in the temporary results 
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
    
    def apply_basic_salary(self):
        contract_id = self._context['params']['id']
        contract = self.env['hr.contract'].browse(contract_id)
        contract.wage = self.basic_salary
        