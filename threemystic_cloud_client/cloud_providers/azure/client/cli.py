from threemystic_cloud_client.cloud_providers.azure.client.base_class.base import cloud_client_azure_client_base as base

    
class cloud_client_azure_client_cli(base):
  def __init__(self, *args, **kwargs):
    super().__init__(logger_name= "cloud_client_azure_client_sso", provider= "azure", *args, **kwargs)

    