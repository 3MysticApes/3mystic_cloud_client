from threemystic_cloud_client.cloud_providers.base_class.base import cloud_client_provider_base as base


class cloud_client_provider_azure_base(base):
  def __init__(self, *args, **kwargs):
    super().__init__(provider= "azure", *args, **kwargs)

    self.links = {
      "cli_doc_link": "https://learn.microsoft.com/en-us/cli/azure/install-azure-cli"
    }

  def serialize_azresource(self, resource):
    if resource is None:
      return None

    return resource.serialize(keep_readonly= True)
    
  def deserialize_azresource(self, resource, aztype):
    if resource is None:
      return None

    return aztype.deserialize(resource)

  def get_resource_id_from_resource(self, resource):
    if resource is None:
        return None

    return self.get_common().helper_type().string().set_case(
      string_value=resource.id.lower(), 
      case= "lower"
    )
  
  def get_resource_group_from_resource(self, resource):
    if hasattr(resource, "resource_group"):
      return resource.resource_group 
    
    resource_id_split = self.get_common().helper_type().string().split(
      string_value= self.get_common().helper_type().string().set_case(
        string_value= self.get_resource_id_from_resource(resource= resource), 
        case= "lower"),
      separator="/",
      regex_split= False
    )
    return resource_id_split[resource_id_split.index("resourcegroups") + 1]
  
  def get_tenant_prefix(self, *args, **kwargs):
    return "/tenants/"

  def get_account_prefix(self, *args, **kwargs):
    return "/subscriptions/"
  
  def get_account_name(self, account, *args, **kwargs):
    if account is None:
      return None
    if self.get_common().helper_type().general().is_type(obj= account, type_check= str):
      return account.strip()
    
    name_options = ["display_name", "name"]

    if self.get_common().helper_type().general().is_type(obj= account, type_check= dict):
      for key, value in account.items():
        if self.get_common().helper_type().string().set_case(string_value= key, case= "lower") in name_options:
          return value.strip()
    
    for att in dir(account):
      if self.get_common().helper_type().string().set_case(string_value= att, case= "lower") in name_options:
        return getattr(account, att).strip()
    
    raise self.get_common().exception().exception(
      exception_type = "generic"
    ).not_implemented(
      logger = self.get_common().get_logger(),
      name = "account",
      message = f"Unknown account object: {account}."
    )

  def get_account_id(self, account, *args, **kwargs):
    if account is None:
      return None
    if self.get_common().helper_type().general().is_type(obj= account, type_check= str):
      return self.get_common().helper_type().string().set_case(string_value= account, case= "lower").strip()
    
    id_options = ["subscriptionid", "subscription_id", "id"]
    
    if self.get_common().helper_type().general().is_type(obj= account, type_check= dict):
      for key, value in account.items():
        if self.get_common().helper_type().string().set_case(string_value= key, case= "lower") in id_options:
          return self.get_common().helper_type().string().set_case(string_value= value, case= "lower").strip() if not self.get_common().helper_type().string().set_case(string_value= value, case= "lower").startswith(self.get_account_prefix()) else self.get_common().helper_type().string().split(string_value= value, separator= "/")[-1]

    for att in dir(account):
      if self.get_common().helper_type().string().set_case(string_value= att, case= "lower") in id_options:
        account_id = getattr(account, att)
        return self.get_common().helper_type().string().set_case(string_value= account_id, case= "lower").strip() if not self.get_common().helper_type().string().set_case(string_value= account_id, case= "lower").startswith(self.get_account_prefix()) else self.get_common().helper_type().string().split(string_value= account_id, separator= "/")[-1]
    
    raise self.get_common().exception().exception(
      exception_type = "generic"
    ).not_implemented(
      logger = self.get_common().get_logger(),
      name = "account",
      message = f"Unknown account object: {account}."
    )
  
  def make_account(self, **kwargs):    
    account = {}

    for key, value in kwargs.items():
      if self.get_common().helper_type().string().set_case(string_value= key, case= "lower") == "id":
        account["Id"] = self.get_common().helper_type().string().set_case(string_value= value, case= "lower").strip()
        continue
      if self.get_common().helper_type().string().set_case(string_value= key, case= "lower") == "name":
        account["Name"] = value.strip()
        continue
        
    
    return account
  
  
  def get_tenant_id(self, tenant, is_account = False, *args, **kwargs):
    if tenant is None:
      return None
    if self.get_common().helper_type().general().is_type(obj= tenant, type_check= str):
      return self.get_common().helper_type().string().set_case(string_value= tenant, case= "lower")
    
    id_options = ["tenantid", "tenant_id", "id"] if not is_account else ["tenantid", "tenant_id"]
    
    if self.get_common().helper_type().general().is_type(obj= tenant, type_check= dict):
      for key, value in tenant.items():
        if self.get_common().helper_type().string().set_case(string_value= key, case= "lower") in id_options:
          return self.get_common().helper_type().string().set_case(string_value= value, case= "lower") if not self.get_common().helper_type().string().set_case(string_value= value, case= "lower").startswith(self.get_tenant_prefix()) else self.get_common().helper_type().string().split(string_value= value, separator= "/")[-1]

    for att in dir(tenant):
      if self.get_common().helper_type().string().set_case(string_value= att, case= "lower") in id_options:
        tenant_id = getattr(tenant, att)
        return self.get_common().helper_type().string().set_case(string_value= tenant_id, case= "lower") if not self.get_common().helper_type().string().set_case(string_value= tenant_id, case= "lower").startswith(self.get_tenant_prefix()) else self.get_common().helper_type().string().split(string_value= tenant_id, separator= "/")[-1]
    
    raise self.get_common().exception().exception(
      exception_type = "generic"
    ).not_implemented(
      logger = self.get_common().get_logger(),
      name = "tenant",
      message = f"Unknown tenant object: {tenant}."
    )
  
  def make_tenant(self, **kwargs):    
    tenant = {}

    for key, value in kwargs.items():
      if self.get_common().helper_type().string().set_case(string_value= key, case= "lower") == "id":
        tenant["Id"] = self.get_common().helper_type().string().set_case(string_value= value, case= "lower")
        continue
      
      if self.get_common().helper_type().string().set_case(string_value= key, case= "lower") == "name":
        tenant["Name"] = value
        continue
        
    
    return tenant
    

