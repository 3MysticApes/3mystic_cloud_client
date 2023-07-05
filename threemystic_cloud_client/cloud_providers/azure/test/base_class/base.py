from threemystic_cloud_client.cloud_providers.azure.base_class.base import cloud_client_provider_azure_base as base

class cloud_client_azure_test_base(base):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

  def step(self, *args, **kwargs):
    if self.is_cli_installed() != True:
      from threemystic_cloud_client.cli import cloud_client_cli
      cloud_client_cli().process_client_action(force_action= "config")
      print("-----------------------------")
      print()
      print()
      print("Continue to test")
      print("-----------------------------")
      
    return True