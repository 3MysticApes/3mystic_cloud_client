from threemystic_cloud_client.cloud_providers.aws.client.base_class.base import cloud_client_aws_client_base as base
from threemystic_cloud_client.cloud_providers.aws.client.base_class.base_sso import cloud_client_aws_client_base_sso as base_sso
import sys

if "polling2" in sys.modules:
    from polling2 import TimeoutException, poll
else:
    try:
        from polling import TimeoutException, poll
    except:
        pass
    
class cloud_client_aws_client_sso(base):
  def __init__(self, *args, **kwargs):
    super().__init__(logger_name= "cloud_client_aws_client_sso", provider= "aws", *args, **kwargs)

    if(self.get_profile()["auth_method"].lower() != "sso"):
      raise self._main_reference.exception().exception(
          exception_type = "generic"
        ).type_error(
          logger = self.get_common().get_logger(),
          name = "Profile Authentication Invalid",
          message = f"Profile Authentication Invalid - {self.get_profile()['profile_name']}"
        )
    
    if(not self.is_sso_profile_valid()):
      raise self._main_reference.exception().exception(
          exception_type = "generic"
        ).type_error(
          logger = self.get_common().get_logger(),
          name = f"AWSCLI SSO Profile NOT FOUND",
          message = f"AWSCLI SSO Profile NOT FOUND - {self.get_profile()['profile_name']}\nPlease run the following command to configure aws cli:\naws configure sso --profile {self.get_profile()['profile_name']}"
        )
  
  def _internal_load_base_configs(self):
    pass
    # self._load_aws_credentials_config()
    # self._load_sso_profile()
    # self._load_ssocredentials()

  def get_default_rolename(self, *args, **kwargs):
    pass
  
  def get_default_region(self, *args, **kwargs):
    pass
  
  def get_rolename(self, *args, **kwargs):
    pass
  
  def get_main_account_id(self, *args, **kwargs):
    pass

  def get_organization_account_id(self, *args, **kwargs):
    pass

  def get_organization_account(self, *args, **kwargs):
    pass

  def set_awscli_rolename(self, *args, **kwargs):
    pass

  # set_main_account_id  
  def _set_main_account_id(self, *args, **kwargs):
    pass


  # set_organization_account_id
  def _set_organization_account_id(self, *args, **kwargs):    
    pass
  
  def is_sso_profile_valid(self):

    aws_credentials_config = self.get_common().helper_config().load(
      config_type = "config",
      path= self.get_aws_user_path_config()
    )

    if not self.get_common().helper_type().string().is_null_or_whitespace(string_value= self.get_profile()['profile_name']) and aws_credentials_config.has_section(f"profile {self.get_profile()['profile_name']}"):
      return True
    
    return False
  
  def _load_aws_sso_config(self):
    aws_credentials_config = self.get_common().helper_config().load(
      config_type = "config",
      path= self.get_aws_user_path_config()
    )

    profile_section = aws_credentials_config.has_section(f"profile {self.get_profile()['profile_name']}")