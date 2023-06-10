from threemystic_cloud_client.cloud_providers.base_class.base import cloud_client_provider_base as base
import os


class cloud_client_provider_aws_base(base):
  def __init__(self, *args, **kwargs):
    # https://github.com/boto/botocore/issues/2705 
    # This update should be temporary until boto version 1.28 is released
    os.environ["BOTO_DISABLE_COMMONNAME"] = "true" 

    super().__init__(*args, **kwargs)   
    self.links = {
      "cli_doc_link": "https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html",
      "ssm_doc_link": "https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html",
      "saml2aws_doc_link": "https://github.com/Versent/saml2aws"
    }
  
  
  def get_provider(self, *args, **kwargs)::
    return "aws"

  def get_account_name(self, account):
    if account is None:
      return None
    if self.get_common().helper_type().general().is_type(obj= account, type_check= str):
      return account

    if account.get("Name"):
      return account["Name"]
    
    if account.get("accountName"):
      self.get_logger().warning("accountName will be depreciated use Name")
      return account["accountName"]
    
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
    
    if account.get("Id"):
      return account["Id"]

    if account.get("accountId"):
      self.get_logger().warning("accountId will be depreciated use Id")
      return account["accountId"]
    
    raise self.get_common().exception().exception(
      exception_type = "generic"
    ).not_implemented(
      logger = self.logger,
      name = "account",
      message = f"Unknown account object: {account}."
    )
  
  def make_account(self, **kwargs):    
    account = {}
    if not self.get_common().helper_type().string().is_null_or_whitespace(string_value= kwargs.get("accountId")):
      self.get_logger().warning("accountId will be depreciated use Id")
      account["accountId"] = kwargs.get("accountId")
      account["Id"] = kwargs.get("accountId")

    if not self.get_common().helper_type().string().is_null_or_whitespace(string_value= kwargs.get("Id")):
      account["Id"] = kwargs.get("Id")

    if not self.get_common().helper_type().string().is_null_or_whitespace(string_value= kwargs.get("accountName")):
      self.get_logger().warning("accountName will be depreciated use Name")
      account["accountName"] = kwargs.get("accountName")
      account["Name"] = kwargs.get("accoNameuntId")

    if not self.get_common().helper_type().string().is_null_or_whitespace(string_value= kwargs.get("Name")):
      account["Name"] = kwargs.get("Name")
    
    return account
  
  
