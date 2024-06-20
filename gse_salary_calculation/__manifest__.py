# -*- coding: utf-8 -*-
{
    'name': "GSE salary calculation",
    'author': "Benjamin Kisenge",
    'website': "https://dev--glowing-faun-e9789d.netlify.app",
    'category': 'Customizations',
    'version': '1.0.0.0',
    'license': 'LGPL-3',
    'depends': [
        'hr_payroll',
    ],

    'data': [
        'views/hr_contract_views.xml',
        'views/salary_calculation_wizard.xml',
        'security/ir.model.access.csv'
    ]
}
