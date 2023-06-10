from threemystic_cloud_client.cloud_providers.aws.base_class.base import cloud_client_provider_aws_base as base

class cloud_client_aws_test_base(base):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

  def step(self, *args, **kwargs):
    if not self.has_config_profiles() or self.is_cli_installed() != True:
      from threemystic_cloud_client.cli import cloud_client_cli
      cloud_client_cli().process_client_action(action= "config")

    return True