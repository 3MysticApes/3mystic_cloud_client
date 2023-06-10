from threemystic_cloud_client.cloud_providers.base_class.base import cloud_client_provider_base as base



class cloud_client_provider_azure_base(base):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    self.links = {
      "cli_doc_link": "https://learn.microsoft.com/en-us/cli/azure/install-azure-cli"
    }

  def get_account_name(self, account):
    if account is None:
      return None
    if self.get_common().helper_type().general().is_type(obj= account, type_check= str):
      return account
    
    if self.get_common().helper_type().general().is_type(obj= account, type_check= dict):
      for key, value in account.items():
        if self.get_common().helper_type().string().set_case(string_value= key, case= "lower") == "name":
          return value
    
    if hasattr(account, "Name"):
      return account.Name
    
    if hasattr(account, "name"):
      return account.name
    
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
    
    if hasattr(account, "id"):
      return account.id
    
    if hasattr(account, "Id"):
      return account.id
    
    raise self.get_common().exception().exception(
      exception_type = "generic"
    ).not_implemented(
      logger = self.logger,
      name = "account",
      message = f"Unknown account object: {account}."
    )
  
  def make_account(self, **kwargs):    
    account = {}

    for key, value in account.items():
      if self.get_common().helper_type().string().set_case(string_value= key, case= "lower") == "id":
        account["Id"] = value
        continue
      if self.get_common().helper_type().string().set_case(string_value= key, case= "lower") == "name":
        account["Name"] = value
        continue
        
    
    return account
    

