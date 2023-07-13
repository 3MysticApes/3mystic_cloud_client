from threemystic_cloud_client.cloud_providers.base_class.base import cloud_client_provider_base as base
import os


class cloud_client_provider_aws_base(base):
  def __init__(self, *args, **kwargs):
    # https://github.com/boto/botocore/issues/2705 
    # This update should be temporary until boto version 1.28 is released
    os.environ["BOTO_DISABLE_COMMONNAME"] = "true" 

    super().__init__(provider= "aws", *args, **kwargs)   
    self.links = {
      "cli_doc_link": "https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html",
      "ssm_doc_link": "https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html",
      "saml2aws_doc_link": "https://github.com/Versent/saml2aws"
    }

  def get_account_name(self, account):
    if account is None:
      return None
    if self.get_common().helper_type().general().is_type(obj= account, type_check= str):
      return account.strip()

    if account.get("Name"):
      return account["Name"].strip()
    
    if account.get("accountName"):
      self.get_common().get_logger().warning("accountName will be depreciated use Name")
      return account["accountName"].strip()
    
    raise self.get_common().exception().exception(
      exception_type = "generic"
    ).not_implemented(
      logger = self.get_common().get_logger(),
      name = "account",
      message = f"Unknown account object: {account}."
    )

  def get_account_id(self, account):
    if account is None:
      return None
    if self.get_common().helper_type().general().is_type(obj= account, type_check= str):
      return self.get_common().helper_type().string().trim(string_value=self.get_common().helper_type().string().set_case(string_value= account, case= "lower"))
    
    if account.get("Id"):
      return self.get_common().helper_type().string().trim(string_value=self.get_common().helper_type().string().set_case(string_value= account["Id"], case= "lower"))

    if account.get("accountId"):
      self.get_common().get_logger().warning("accountId will be depreciated use Id")
      return self.get_common().helper_type().string().trim(string_value=self.get_common().helper_type().string().set_case(string_value= account["accountId"], case= "lower"))
    
    raise self.get_common().exception().exception(
      exception_type = "generic"
    ).not_implemented(
      logger = self.get_common().get_logger(),
      name = "account",
      message = f"Unknown account object: {account}."
    )
  
  def make_account(self, **kwargs):    
    account = {}
    if not self.get_common().helper_type().string().is_null_or_whitespace(string_value= kwargs.get("accountId")):
      self.get_common().get_logger().warning("accountId will be depreciated use Id")
      account["accountId"] = self.get_common().helper_type().string().trim(string_value=self.get_common().helper_type().string().set_case(string_value= kwargs.get("accountId"), case= "lower"))
      account["Id"] = self.get_common().helper_type().string().trim(string_value=self.get_common().helper_type().string().set_case(string_value= kwargs.get("accountId"), case= "lower"))

    if not self.get_common().helper_type().string().is_null_or_whitespace(string_value= kwargs.get("Id")):
      account["Id"] = self.get_common().helper_type().string().trim(string_value=self.get_common().helper_type().string().set_case(string_value= kwargs.get("Id"), case= "lower"))

    if not self.get_common().helper_type().string().is_null_or_whitespace(string_value= kwargs.get("accountName")):
      self.get_common().get_logger().warning("accountName will be depreciated use Name")
      account["accountName"] = self.get_common().helper_type().string().trim(string_value=kwargs.get("accountName"))
      account["Name"] = self.get_common().helper_type().string().trim(string_value=kwargs.get("accountName"))

    if not self.get_common().helper_type().string().is_null_or_whitespace(string_value= kwargs.get("Name")):
      account["Name"] = self.get_common().helper_type().string().trim(string_value=kwargs.get("Name"))
    
    return account
  
  
