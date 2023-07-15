from threemystic_cloud_client.cloud_providers.aws.base_class.base import cloud_client_provider_aws_base as base

class cloud_client_aws_generate_base(base):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

  def _login(self, *args, **kwargs):
    pass
  
  def step(self, *args, **kwargs):
    if self.is_cli_installed() != True:
      from threemystic_cloud_client.cli import cloud_client_cli
      cloud_client_cli().process_client_action(force_action= "config")
      print("-----------------------------")
      print()
      print()
      print("Continue to token")
      print("-----------------------------")
      
    return True