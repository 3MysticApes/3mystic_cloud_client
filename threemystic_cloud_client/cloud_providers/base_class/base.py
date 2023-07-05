from threemystic_common.base_class.base_provider import base
from abc import abstractmethod

class cloud_client_provider_base(base):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    
    self._post_init(*args, **kwargs)

  
  def _post_init(self, *args, **kwargs):
    pass
  
  def update_provider_config_completed(self, status, *args, **kwargs):
    self.get_config()["_config_process"] = status
    self._save_config()
  
  def is_provider_config_completed(self, *args, **kwargs):
    return self.get_config().get("_config_process") is True
  
  def get_main_directory_name(self, *args, **kwargs):
    return "client"

  @abstractmethod
  def get_account_name(self, account, *args, **kwargs):
    pass

  @abstractmethod
  def get_account_id(self, account, *args, **kwargs):
    pass

  @abstractmethod
  def make_account(self, account, *args, **kwargs):
    pass  

  def __load_config(self, *args, **kwargs):
    config_data = self.get_common().helper_config().load(
      path= self.config_path(),
      config_type= "yaml"
    )
    if config_data is not None:
      return config_data
    
    return {}

  def is_cli_installed(self, *args, **kwargs):
    return self.get_config().get("cli_installed") == True

  def get_aws_poll_login(self, *args, **kwargs):
    if(self.get_config().get("aws_poll_login") is None):
      return 120
    return self.get_config().get("aws_poll_login")

  def get_aws_poll_authenticate(self, *args, **kwargs):
    if(self.get_config().get("aws_poll_authenticate") is None):
      return 240
    return self.get_config().get("aws_poll_authenticate")

  def valid_auth_options(self, *args, **kwargs):
    return ["sso"]

  def config_path(self, *args, **kwargs):
    return self.get_common().get_threemystic_directory_config().joinpath(f"{self.get_main_directory_name()}/config_{self.get_provider()}")
    
  def get_aws_user_path(self, *args, **kwargs):
    return self.get_common().helper_path().expandpath_user("~/.aws")
  
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
        "profile_name": self.get_common().helper_type().string().set_case(string_value= profile, case= "lower"),
        "profile_data": profile_data
      }
    
    return None

  def config_profile_name_exists(self, *args, **kwargs):
    
    return self.get_config_profile_name(*args, **kwargs) != None
  
  def _update_config(self,config_key, config_value, refresh= False,  *args, **kwargs):
     self.get_config(refresh = True)[config_key] = config_value
  
  def _save_config(self, *args, **kwargs):
     if not self.config_path().parent.exists():
       self.config_path().mkdir(parents= True)
     self.config_path().write_text(
      data= self.get_common().helper_yaml().dumps(data= self.get_config())
     )
     self.get_config(refresh = True)

  def get_config(self, refresh = False, *args, **kwargs):
    if hasattr(self, "_config_data") and not refresh:
      return self._config_data
    
    self._config_data = self.__load_config()    
    self._config_data["profiles"] = {self.get_common().helper_type().string().set_case(string_value= profile_name, case= "lower"):profile_data for profile_name,profile_data in self.get_config_profiles().items()}

    return self.get_config(*args, **kwargs)
  
  def get_config_value(self, config_key, default_if_none = None, refresh = False, *args, **kwargs):
    config_value = self.get_config(refresh= refresh).get(config_key)
    if config_value is not None:
      return config_value
    
    return default_if_none

  def has_config_profiles(self, *args, **kwargs):
    
    if self.get_config().get("profiles") is None:
      return False
    
    return len(self.get_config().get("profiles")) > 0

  def get_config_profiles(self, *args, **kwargs):
    if self.get_config().get("profiles") is not None:
      return self.get_config().get("profiles")
    
    self.get_config()["profiles"] = {}
    return self.get_config_profiles()

  def get_config_profile_name(self, profile_name = None, *args, **kwargs):
    if self.get_common().helper_type().string().is_null_or_whitespace(string_value= profile_name):
      return None
    
    profile_name = self.get_common().helper_type().string().set_case(string_value= profile_name, case= "lower")
    for existing_profile_name, profile_data in self.get_config_profiles().items():
      if(existing_profile_name != profile_name):
        continue
      
      return profile_data
    
    return None

  
  def action_config(self, *args, **kwargs):
    print("Provider config not configured")
  
  def action_test(self, *args, **kwargs):
    print("Provider test config not configured")
  
  def action_token(self, *args, **kwargs):
    print("Provider token config not configured")

    

  
  

