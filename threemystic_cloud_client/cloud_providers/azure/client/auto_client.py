from threemystic_cloud_client.cloud_providers.azure.base_class.base import cloud_client_provider_azure_base as base

class cloud_client_azure_client_auto(base):
  def __init__(self, *args, **kwargs):
    super().__init__(logger_name= "cloud_client_azure_auto", *args, **kwargs)



  def get_client(self, *args, **kwargs):
    if self.get_common().helper_type().string().set_case(string_value= self.get_profile()["profile_data"]["auth_method"], case= "lower") == "sso":
      from threemystic_cloud_client.cloud_providers.azure.client.cli import cloud_client_azure_client_cli as client
      return client()
  