# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api,models
from PyPDF2 import PdfFileReader, PdfFileWriter
import PIL.Image as Image
import shutil
import os

class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    @api.model
    def _run_wkhtmltopdf(
            self,
            bodies,
            report_ref=False,
            header=None,
            footer=None,
            landscape=False,
            specific_paperformat_args=None,
            set_viewport_size=False):
        
        ''' Method extension for compressing pdf task report
        '''
        
        pdf_content = super()._run_wkhtmltopdf(
            bodies,
            report_ref,
            header,
            footer,
            landscape,
            specific_paperformat_args,
            set_viewport_size)
        
        report_sudo = self._get_report(report_ref)
        
        # Compression is perfomed only in the project.task records
        if report_sudo.model == "project.task":
            # Create a temporary file to store the pdf to compress
            f = open('original.pdf', 'wb')
            f.write(pdf_content)
            f.close()

            # Compress the original file
            self.compress_pdfs('original.pdf')

            # Get the compressed file in base64
            compressed_pdf = self._get_compressed_pdf('compressed.pdf')
            pdf_content = compressed_pdf

            # Delete the two files
            os.remove('original.pdf')
            os.remove('compressed.pdf')
        
        return pdf_content
    

    def compress_pdfs(self, pdf_path): 
        reader = PdfFileReader(pdf_path)
        writer = PdfFileWriter()

        extracted_image_paths = []

        # Iterate through the pages of the original PDF
        for page_number in range(len(reader.pages)):
            page = reader.pages[page_number]
            writer.addPage(page)

            # Get the image references from the page resources
            if '/XObject' in page['/Resources']:
                image_ref = page['/Resources']['/XObject'].getObject()
                

                # Iterate through the image references
                for image_obj in image_ref.keys(): 
                    if image_ref[image_obj]['/Subtype'] == '/Image':
                    #     # Get the image data
                        img_data = image_ref[image_obj].getData() 

                        # Create directory if it does not exist
                        directory = f"images/page{page_number}"
                        os.makedirs(directory, exist_ok=True)

                        # Adjust image object name for file name
                        image_obj_name = image_obj.replace("/", "_")

                        # Save the image to a file
                        image_file_path = f"{directory}/{image_obj_name}.jpg"
                        with open(image_file_path, "wb") as f:
                            f.write(img_data)

                        try: 
                            # Compress the image
                            img = Image.open(image_file_path)
                            img_compressed = img.convert("RGB")
                            img_compressed.save(image_file_path, format="JPEG", quality=10)

                            # Read the compressed image data
                            with open(image_file_path, "rb") as f:
                                compressed_img_data = f.read()

                            # Replace the original image data in the PDF with the compressed image data
                            image_ref[image_obj]._data = compressed_img_data

                            # Add the image file path to the list
                            extracted_image_paths.append(image_file_path)
                        except Exception as e:
                            pass

        output_pdf_path = "compressed.pdf"
        with open(output_pdf_path, "wb") as f:
            writer.write(f)

        # Delete the extracted image files
        directory_path = 'images'
        if os.path.exists(directory_path):
            shutil.rmtree(directory_path)
        else:
            print(f"The directory {directory_path} does not exist.") 
    
    def _get_compressed_pdf(self, pdf_file_path):
        with open(pdf_file_path, "rb") as pdf_file:
            pdf_binary_data = pdf_file.read()
            if not pdf_binary_data.startswith(b'%PDF'):
                pdf_binary_data = b'%PDF-1.4\n' + pdf_binary_data
        return pdf_binary_data
