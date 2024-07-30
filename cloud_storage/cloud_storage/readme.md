Store Odoo attachments in the cloud
===================================

Odoo attachments are made into URL-type attachments, and their binary content is uploaded in the cloud.

The following use-cases are covered:
* Attachments uploaded using the chatter *Attach file* button
* Attachments generated when rendering a PDF report file (e.g. printed invoice)

The following cloud storage services are supported
* Google Cloud Storage
* Azure Blob Storage

To manage existing attachments stored in the filestore we suggest implementing an Odoo scheduled action that will make use of the method `move_to_cloud` of model `ir.attachment`

## Account Setup

### Google Cloud
* Create a Google Cloud account
* Create a services account
* Download json key from the services account
* Create a bucket for your Odoo files

### MS Azure Blob Storage
* Create a Azure Blob Storage account
* The connection string can be found in your account settings
* Create a container for your Odoo files

## Odoo database

* Paste the account key (json or connection string) in module settings
* Fill in the bucket or container name

## Security

* Your bucket / container should not be public because files will be accessed through a signed url
* URL stored in Odoo will include an access token (see [Azure SAS], [Google Signed URLs])
* CORS must be configured for Odoo to be allowed to preview PDFs (see [Azure CORS], [Google CORS])

## Testing with emulators

### fake-gcs-server (Google Cloud Storage emulator)
> Requires additional module **cloud_storage_testing**
* Can be run as a standalone docker container, see [Github doc]
* Uses credentials with no private key, hence does not support signed urls
* Set your local emulator `host:port` in place of the Google json key in cloud storage settings
* Set the following json key in cloud storage settings, make sure `api_endpoint` is set to your local emulator `host:port`
```
{"api_endpoint": "http://0.0.0.0:4443"}
```

### Azurite (Azure Blob Storage emulator)
* Can be run as a standalone docker container, see [MS Azurite doc]
* Uses predefined testing credentials and supports signed urls
* Set the following connection string in cloud storage settings, make sure `BlobEndpoint` is set to your local emulator `host:port`
```
DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://0.0.0.0:10000/devstoreaccount1
```

[Google Signed URLs]: https://cloud.google.com/storage/docs/access-control/signed-urls
[Azure SAS]: https://docs.microsoft.com/en-us/azure/storage/common/storage-sas-overview
[Google CORS]: https://cloud.google.com/storage/docs/configuring-cors
[Azure CORS]: https://docs.microsoft.com/en-us/rest/api/storageservices/cross-origin-resource-sharing--cors--support-for-the-azure-storage-services

[Github doc]: https://github.com/fsouza/fake-gcs-server?tab=readme-ov-file#using-the-emulator-in-docker
[MS Azurite doc]: https://learn.microsoft.com/en-us/azure/storage/common/storage-use-azurite?tabs=docker-hub%2Cblob-storage#run-azurite
