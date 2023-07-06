from threemystic_cloud_client.cloud_providers.azure.base_class.base import cloud_client_provider_azure_base as base

class cloud_client_azure_client_auto(base):
  def __init__(self, *args, **kwargs):
    super().__init__(logger_name= "cloud_client_azure_auto", *args, **kwargs)

  def _login(self, *args, **kwargs):
    pass
  
  def get_client(self, *args, **kwargs):

    from threemystic_cloud_client.cloud_providers.azure.client.cli import cloud_client_azure_client_cli as client
    return client()
  