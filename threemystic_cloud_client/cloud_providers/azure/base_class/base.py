from threemystic_cloud_client.cloud_providers.base_class.base import cloud_client_provider_base as base



class cloud_client_provider_azure_base(base):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    self.links = {
      "cli_doc_link": "https://learn.microsoft.com/en-us/cli/azure/install-azure-cli"
    }

  
  def get_provider(self):
    return "azure"

  def get_account_name(self, account):
    if account is None:
      return None
    if self.get_common().helper_type().general().is_type(obj= account, type_check= str):
      return account
    
    if self.get_common().helper_type().general().is_type(obj= account, type_check= dict):
      for key, value in account.items():
        if self.get_common().helper_type().string().set_case(string_value= key, case= "lower") == "name":
          return value
    
    for att in dir(account):
      if self.get_common().helper_type().string().set_case(string_value= att, case= "lower") == "name":
        return getattr(account, att)
    
    raise self.get_common().exception().exception(
      exception_type = "generic"
    ).not_implemented(
      logger = self.logger,
      name = "account",
      message = f"Unknown account object: {account}."
    )

  def get_account_id(self, account):
    if account is None:
      return None
    if self.get_common().helper_type().general().is_type(obj= account, type_check= str):
      return account
    
    if self.get_common().helper_type().general().is_type(obj= account, type_check= dict):
      for key, value in account.items():
        if self.get_common().helper_type().string().set_case(string_value= key, case= "lower") == "id":
          return value

    for att in dir(account):
      if self.get_common().helper_type().string().set_case(string_value= att, case= "lower") == "id":
        return getattr(account, att)
    
    raise self.get_common().exception().exception(
      exception_type = "generic"
    ).not_implemented(
      logger = self.logger,
      name = "account",
      message = f"Unknown account object: {account}."
    )
  
  def make_account(self, **kwargs):    
    account = {}

    for key, value in kwargs.items():
      if self.get_common().helper_type().string().set_case(string_value= key, case= "lower") == "id":
        account["Id"] = value
        continue
      if self.get_common().helper_type().string().set_case(string_value= key, case= "lower") == "name":
        account["Name"] = value
        continue
        
    
    return account
  
  
  def get_tenant_id(self, tenant):
    if tenant is None:
      return None
    if self.get_common().helper_type().general().is_type(obj= tenant, type_check= str):
      return tenant
    
    tenant_id_options = ["tenantid", "id"]
    if self.get_common().helper_type().general().is_type(obj= tenant, type_check= dict):
      for key, value in tenant.items():
        if self.get_common().helper_type().string().set_case(string_value= key, case= "lower") in tenant_id_options:
          return value

    for att in dir(tenant):
      if self.get_common().helper_type().string().set_case(string_value= att, case= "lower") in tenant_id_options:
        return getattr(tenant, att)
    
    raise self.get_common().exception().exception(
      exception_type = "generic"
    ).not_implemented(
      logger = self.logger,
      name = "tenant",
      message = f"Unknown tenant object: {tenant}."
    )
  
  def make_tenant(self, **kwargs):    
    tenant = {}

    for key, value in kwargs.items():
      if self.get_common().helper_type().string().set_case(string_value= key, case= "lower") == "id":
        tenant["Id"] = value
        continue
      if self.get_common().helper_type().string().set_case(string_value= key, case= "lower") == "name":
        tenant["Name"] = value
        continue
        
    
    return tenant
    

