from threemystic_cloud_client.cloud_providers.azure.client.base_class.base import cloud_client_azure_client_base as base
from azure.identity import AzureCliCredential



class cloud_client_azure_client_cli(base):
  def __init__(self, *args, **kwargs):
    super().__init__(logger_name= "cloud_client_azure_client_sso", provider= "azure", *args, **kwargs)

  
  def get_tenant_credential(self, tenant_id, *args, **kwargs):
    if self.get_common().helper_type().string().is_null_or_whitespace(string_value= tenant_id):
      raise self._main_reference.exception().exception(
        exception_type = "argument"
      ).type_error(
        logger = self.get_common().get_logger(),
        name = "tenant_id",
        message = f"tenant_id cannot be null or whitespace"
      )

    if self._get_credential().get(tenant_id) is not None:
      return self._get_credential().get(tenant_id)
    
    self.credential[tenant_id] = AzureCliCredential(tenant_id= tenant_id)        
    return self.get_tenant_credential(tenant_id= tenant_id)

  