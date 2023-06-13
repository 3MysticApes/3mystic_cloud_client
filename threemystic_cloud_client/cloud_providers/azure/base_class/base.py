from threemystic_cloud_client.cloud_providers.base_class.base import cloud_client_provider_base as base



class cloud_client_provider_azure_base(base):
  def __init__(self, *args, **kwargs):
    super().__init__(provider= "azure", *args, **kwargs)

    self.links = {
      "cli_doc_link": "https://learn.microsoft.com/en-us/cli/azure/install-azure-cli"
    }

  def get_tenant_prefix(self, *args, **kwargs):
    return "/tenants/"

  def get_account_prefix(self, *args, **kwargs):
    return "/subscriptions/"
  
  def get_account_name(self, account, *args, **kwargs):
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

  def get_account_id(self, account, *args, **kwargs):
    if account is None:
      return None
    if self.get_common().helper_type().general().is_type(obj= account, type_check= str):
      return account
    
    id_options = ["subscriptionid", "id"]
    
    if self.get_common().helper_type().general().is_type(obj= account, type_check= dict):
      for key, value in account.items():
        if self.get_common().helper_type().string().set_case(string_value= key, case= "lower") in id_options:
          return value if not self.get_common().helper_type().string().set_case(string_value= value, case= "lower").startswith(self.get_account_prefix()) else self.get_common().helper_type().string().split(string_value= value, separator= "/")[-1]

    for att in dir(account):
      if self.get_common().helper_type().string().set_case(string_value= att, case= "lower") in id_options:
        account_id = getattr(account, att)
        return account_id if not self.get_common().helper_type().string().set_case(string_value= account_id, case= "lower").startswith(self.get_account_prefix()) else self.get_common().helper_type().string().split(string_value= account_id, separator= "/")[-1]
    
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
  
  
  def get_tenant_id(self, tenant, *args, **kwargs):
    if tenant is None:
      return None
    if self.get_common().helper_type().general().is_type(obj= tenant, type_check= str):
      return tenant
    
    id_options = ["tenantid", "id"]
    
    if self.get_common().helper_type().general().is_type(obj= tenant, type_check= dict):
      for key, value in tenant.items():
        if self.get_common().helper_type().string().set_case(string_value= key, case= "lower") in id_options:
          return value if not self.get_common().helper_type().string().set_case(string_value= value, case= "lower").startswith(self.get_tenant_prefix()) else self.get_common().helper_type().string().split(string_value= value, separator= "/")[-1]

    for att in dir(tenant):
      if self.get_common().helper_type().string().set_case(string_value= att, case= "lower") in id_options:
        tenant_id = getattr(tenant, att)
        return tenant_id if not self.get_common().helper_type().string().set_case(string_value= tenant_id, case= "lower").startswith(self.get_tenant_prefix()) else self.get_common().helper_type().string().split(string_value= tenant_id, separator= "/")[-1]
    
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
    

