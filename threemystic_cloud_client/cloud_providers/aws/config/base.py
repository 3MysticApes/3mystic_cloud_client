from threemystic_cloud_client.cloud_providers.base_class.base import cloud_client_provider_base as base

class cloud_client_aws_config_base(base):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

  
  def update_config_profile(self, config, profile_name, running_config, auto_save = True, *args, **kwargs):
    if config.get("profiles") is None:
      config["profiles"] = {}

    config["profiles"][profile_name] = running_config
    if auto_save:
      self.save_config(config= config)

    return config
  
  def save_config(self, config, *args, **kwargs):
     self.config_path().write_text(
      data= self.get_common().helper_yaml().dumps(data= config)
     )
     
  def step(self, config, *args, **kwargs):
    
    if self.is_cli_installed(config= config) != True:
      print("aws cli is not marked as installed please start over")
      return False

    return True