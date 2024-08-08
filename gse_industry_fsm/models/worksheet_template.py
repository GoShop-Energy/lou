from lxml import etree
from odoo import api, models


class WorksheetTemplate(models.Model):
    _inherit = 'worksheet.template'
    _description = 'Worksheet Template'

    def _get_qweb_arch(self, ir_model, qweb_template_name, form_view_id=False):
        qweb_arch_string = super(WorksheetTemplate, self)._get_qweb_arch(ir_model, qweb_template_name, form_view_id)
        t_root = etree.fromstring(qweb_arch_string)

        view_get_result = self.env[ir_model.model].get_view(form_view_id, 'form')
        form_view_arch = view_get_result['arch']
        form_view_node = etree.fromstring(form_view_arch)


        for row_node in form_view_node.xpath('//group'):
            if 'string' in row_node.attrib:
                custom_section = etree.Element('div', {
                    'class': 'custom-section',
                    'style': 'margin-bottom: 20px; border-bottom: 1px solid grey; font-weight: bold; text-transform: uppercase'
                })
                custom_section.text = row_node.attrib['string']
                t_root.find('.//div').append(custom_section) 

        return etree.tostring(t_root, pretty_print=True, encoding='unicode')

        
