from threemystic_cloud_client.base_class.base import base
import abc

class cloud_client_provider_base(base):
  def __init__(self, provider, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self._provider = provider

  @abc.abstractmethod
  def get_account_name(self, account):
    pass

  @abc.abstractmethod
  def get_account_id(self, account):
    pass

  @abc.abstractmethod
  def make_account(self, account):
    pass
  
  def get_provider(self, *args, **kwargs):
    return self._provider

  def is_cli_installed(self, config, *args, **kwargs):
    return config["cli_installed"] == True

  def valid_auth_options(self, *args, **kwargs):
    return ["sso"]

  def config_path(self, *args, **kwargs):
    return self.get_common().get_threemystic_config_path().joinpath("3mystic_cloud_client_config")
    
  def aws_config_path(self, *args, **kwargs):
    return "~/.aws/config"
  
  def get_existing_profiles(self, config = None, *args, **kwargs):
    if config is None:
      config = self._load_config()

    profiles = config.get("profiles") if config is not None else None 
    return profiles.get(self.get_provider()) if profiles is not None else None
    
    
  
  def _load_config(self, *args, **kwargs):
    return self.get_common().helper_config().load(
      path= self.config_path(),
      config_type= "yaml"
    )
  
  def load_config(self, provider, profile_name = None, *args, **kwargs):
    for profile, data in self.get_existing_profiles().items():
      if self.get_common().helper_type().string().is_null_or_whitespace(string_value= profile_name):
        if self.get_common().helper_type().bool().is_true(check_value= data.get("default_profile")):
          return data
      
      if profile.lower() == profile_name.lower():
        return data
    
    return None

    

  
  

