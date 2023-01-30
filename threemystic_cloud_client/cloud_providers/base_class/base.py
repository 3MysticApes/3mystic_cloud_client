from threemystic_cloud_client.base_class.base import base

class cloud_client_provider_base(base):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

  def is_cli_installed(self, config, *args, **kwargs):
    return config["cli_installed"] == True

  def valid_auth_options(self, *args, **kwargs):
    return ["sso"]

  def config_path(self, *args, **kwargs):
    return self.get_common().get_threemystic_config_path().joinpath("3mystic_cloud_client_config")
    
  def aws_config_path(self, *args, **kwargs):
    return "~/.aws/config"
  
  def get_existing_profiles(self, config, *args, **kwargs):
    return config.get("profiles") if config is not None else None 
  
  def load_config(self, *args, **kwargs):
    return self.get_common().helper_config().load(
      path= self.config_path(),
      config_type= "yaml"
    )
  
  
  