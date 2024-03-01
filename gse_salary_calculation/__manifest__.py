# -*- coding: utf-8 -*-
{
    'name': "gse_basic_calculation",

    'summary': """
        Customizations pour Goshop Energy""",

    'description': """
    """,

    'author': "Benjamin Kisenge",
    'website': "https://dev--glowing-faun-e9789d.netlify.app",

    'category': 'Customizations',
    'version': '1.0.0.0',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': [
        'hr_payroll',
    ],

    'data': [
        'views/hr_contract_views.xml',
        'views/salary_calculation_wizard.xml',
        'security/ir.model.access.csv'
    ],
    'external_dependencies': {
        'python': ['numpy'],
    },
}
