from io import BytesIO
from azure.storage.blob import BlobServiceClient, BlobSasPermissions, generate_blob_sas
from odoo import api, models
from odoo.tools import ormcache


class CloudStorageAzureAttachment(models.Model):
    _inherit = 'ir.attachment'

    @api.model
    @ormcache('connect_str')
    def _get_account_info_azure(self, connect_str):
        parameters = connect_str.split(';')
        dict = {}
        for parameter in parameters:
            if '=' not in parameter:
                continue
            key, value = parameter.split('=', 1)
            dict[key] = value
        return dict

    @api.model
    def _generate_signed_url_azure(self, blob):
        connect_str = self.env['ir.config_parameter'].sudo().get_param('azure_connect_str')
        account_info = self._get_account_info_azure(connect_str)
        token = generate_blob_sas(
            account_name=account_info['AccountName'],
            account_key=account_info['AccountKey'],
            container_name=blob.container_name,
            blob_name=blob.blob_name,
            permission=BlobSasPermissions(read=True),
            expiry=self._get_expiry_date()
        )
        return '%s?%s' % (blob.url, token)

    @api.model
    def _get_client_azure(self):
        connect_str = self.env['ir.config_parameter'].sudo().get_param('azure_connect_str')
        return BlobServiceClient.from_connection_string(connect_str)

    def _get_blob_azure(self):
        container_name = self.env['ir.config_parameter'].sudo().get_param('azure_container_name')
        blob_name = self._get_blob_name()
        client = self._get_client_azure()
        return client.get_blob_client(container=container_name, blob=blob_name)

    def _upload_file_azure(self):
        blob = self._get_blob_azure()
        with BytesIO(self.raw) as buffer:
            blob.upload_blob(buffer)
        return self._generate_signed_url_azure(blob)
