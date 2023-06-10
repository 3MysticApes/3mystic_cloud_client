from threemystic_cloud_client.cloud_providers.azure.base_class.base import cloud_client_provider_azure_base as base


class cloud_client_azure_client_base(base):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)