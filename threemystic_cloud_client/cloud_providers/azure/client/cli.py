from threemystic_cloud_client.cloud_providers.azure.client.base_class.base import cloud_client_azure_client_base as base
from azure.identity import AzureCliCredential



class cloud_client_azure_client_cli(base):
  def __init__(self, *args, **kwargs):
    super().__init__(logger_name= "cloud_client_azure_client_sso", *args, **kwargs)

  
  def _login(self, on_login_function = None, tenant = None, *args, **kwargs):
 
    tenant_id = f' --tenant {self.get_tenant_id(tenant= tenant)}' if tenant is not None else ""

    return self._az_cli(
      command= f"az login{tenant_id} --allow-no-subscriptions",
      on_login_function = on_login_function
    )
        
  def _get_tenant_credential(self, tenant, *args, **kwargs):
    return AzureCliCredential(tenant_id= self.get_tenant_id(tenant= tenant))

  