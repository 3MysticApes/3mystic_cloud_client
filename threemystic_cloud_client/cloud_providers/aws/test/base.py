from threemystic_cloud_client.cloud_providers.aws.base_class.base import cloud_client_provider_aws_base as base

class cloud_client_aws_test_base(base):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

  # There is not post init when in Config Mode
  def _post_init(self, *args, **kwargs):
    pass

  def step(self, config, *args, **kwargs):
    return True