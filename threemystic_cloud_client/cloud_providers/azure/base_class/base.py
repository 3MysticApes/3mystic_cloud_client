from threemystic_cloud_client.cloud_providers.base_class.base import cloud_client_provider_base as base



class cloud_client_provider_azure_base(base):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

  def get_account_name(self, account):
    raise Exception("fix")

  def get_account_id(self, account):
    raise Exception("fix")

  def make_account(self, account):
    raise Exception("fix")
    

