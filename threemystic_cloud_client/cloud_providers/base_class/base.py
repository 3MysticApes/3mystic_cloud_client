from threemystic_cloud_client.base_class.base import base
import abc

class cloud_client_provider_base(base):
  def __init__(self, provider, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self._provider = provider
    self.__config = None

  @abc.abstractmethod
  def get_account_name(self, account):
    pass

  @abc.abstractmethod
  def get_account_id(self, account):
    pass

  @abc.abstractmethod
  def make_account(self, account):
    pass  

  def __load_config(self, *args, **kwargs):
    return self.get_common().helper_config().load(
      path= self.config_path(),
      config_type= "yaml"
    )
  
  def get_provider(self, *args, **kwargs):
    return self._provider

  def is_cli_installed(self, *args, **kwargs):
    return self.get_config().get("cli_installed") == True

  def valid_auth_options(self, *args, **kwargs):
    return ["sso"]

  def config_path(self, *args, **kwargs):
    return self.get_common().get_threemystic_config_path().joinpath(f"3mystic_cloud_client_config_{self.get_provider()}")
    
  def get_aws_user_path(self, *args, **kwargs):
    return "~/.aws"
  
  def get_aws_user_path_config(self, *args, **kwargs):
    return f"{self.get_aws_user_path()}/config"
  
  def get_default_profile_name(self, *args, **kwargs):

    default_profile = self.get_default_profile()
    if(default_profile is None):
      return None
    
    return default_profile["profile_name"]
  
  
  def has_default_profile(self, profile_name = None, *args, **kwargs):
    return self.get_default_profile() != None

  def get_default_profile(self, *args, **kwargs):
      
    for profile, profile_data in self.get_config_profiles().items():
      if(not profile_data["default_profile"]):
        continue
      
      return {
        "profile_name": profile.lower(),
        "profile_data": profile_data
      }
    
    return None

  def config_profile_name_exists(self, *args, **kwargs):
    
    return self.get_config_profile_name(*args, **kwargs) != None
  
  def get_config(self, force_update = False, *args, **kwargs):
    if self.__config is not None and not force_update:
      return self.__config
      
    self.__config = self.__load_config()
    if(self.__config is None):
      self.__config = {}
      return self.get_config(*args, **kwargs)
    
    self.__config["profiles"] = {profile_name.lower():profile_data for profile_name,profile_data in self.get_config_profiles().items()}

    return self.get_config(*args, **kwargs)
  
  def has_config_profiles(self, *args, **kwargs):
    
    profiles = self.get_config().get("profiles")
    if profiles is None:
      return False
    
    return len(profiles) > 0

  def get_config_profiles(self, *args, **kwargs):
    if self.get_config().get("profiles") is not None:
      return self.get_config().get("profiles")
    
    self.get_config()["profiles"] = {}
    return self.get_config_profiles()
  
  def has_config_profiles(self, *args, **kwargs):
    return len(self.self.get_config_profiles()) > 0

  def get_config_profile_name(self, profile_name = None, *args, **kwargs):
    if self.get_common().helper_type().string().is_null_or_whitespace(string_value= profile_name):
      return False
    
    profile_name = profile_name.lower()
    for existing_profile_name, profile_data in self.get_config_profiles().items():
      if(existing_profile_name != profile_name):
        continue
      
      return profile_data
    
    return None

  
  def action_config(self, *args, **kwargs):
    print("Provider config not configured")
  
  def action_test(self, *args, **kwargs):
    print("Provider test config not configured")

    

  
  

