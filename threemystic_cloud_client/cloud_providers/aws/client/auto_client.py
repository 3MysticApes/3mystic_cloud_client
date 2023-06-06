from threemystic_cloud_client.cloud_providers.aws.base_class.base import cloud_client_provider_aws_base as base

class cloud_client_aws_client_auto(base):
  def __init__(self, *args, **kwargs):
    super().__init__(logger_name= "cloud_client_aws_auto", provider= "aws", *args, **kwargs)

    self.__set_profile(*args, **kwargs)
  
  def get_profile(self, *args, **kwargs):
    if(not hasattr(self, "__profile")):
      raise self._main_reference.exception().exception(
          exception_type = "generic"
        ).type_error(
          logger = self.get_common().get_logger(),
          name = "Cloud Client Profile",
          message = f"Profile was not set"
        )
    
    if(self.__profile is None):
      raise self._main_reference.exception().exception(
          exception_type = "generic"
        ).type_error(
          logger = self.get_common().get_logger(),
          name = "Cloud Client Profile",
          message = f"Profile is None"
        )
    
    return self.__profile
  
  def __set_profile(self, profile_name = None, *args, **kwargs):
    if not self.get_common().helper_type().string().is_null_or_whitespace(string_value= profile_name):
      profile_data = self.get_config_profile_name(profile_name= profile_name)
      if profile_data is None:
        raise self._main_reference.exception().exception(
          exception_type = "argument"
        ).type_error(
          logger = self.get_common().get_logger(),
          name = "profile_name",
          message = f"profile_name is not found"
        )
      
      self.__profile = {
        "profile_name": profile_name,
        "profile_data": profile_data
      }
      return
    
    self.__profile = self.get_default_profile()

  def get_client(self, *args, **kwargs):
    if self.get_profile()["profile_data"]["auth_method"].lower() == "sso":
      from threemystic_cloud_client.cloud_providers.aws.client.sso import cloud_client_aws_client_sso as client
      return client(profile_data= self.get_profile())
  