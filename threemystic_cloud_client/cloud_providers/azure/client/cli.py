from threemystic_cloud_client.cloud_providers.azure.client.base_class.base import cloud_client_azure_client_base as base
from azure.identity import AzureCliCredential



class cloud_client_azure_client_cli(base):
  def __init__(self, *args, **kwargs):
    super().__init__(logger_name= "cloud_client_azure_client_sso", *args, **kwargs)

  def login(self, *args, **kwargs):
    self.__login(*args, **kwargs)
  
  def __login(self, on_login_function = None, tenant = None, *args, **kwargs):
 
    tenant_id = f' --tenant {self.get_tenant_id(tenant= tenant)}' if tenant is not None else ""

    self._az_cli(
      command= f"az login{tenant_id} --allow-no-subscriptions",
      on_login_function = on_login_function
    )
        
  def get_tenant_credential(self, tenant, *args, **kwargs):
    if self.get_common().helper_type().string().is_null_or_whitespace(string_value= self.get_tenant_id(tenant= tenant)):
      raise self.get_common().exception().exception(
        exception_type = "argument"
      ).type_error(
        logger = self.get_common().get_logger(),
        name = "tenant_id",
        message = f"tenant_id cannot be null or whitespace"
      )

    if self._get_credential().get(self.get_tenant_id(tenant= tenant)) is not None:
      return self._get_credential().get(self.get_tenant_id(tenant= tenant))
    
    self._get_credential()[self.get_tenant_id(tenant= tenant)] = AzureCliCredential(tenant_id= self.get_tenant_id(tenant= tenant))        
    return self.get_tenant_credential(tenant= tenant, *args, **kwargs)

  