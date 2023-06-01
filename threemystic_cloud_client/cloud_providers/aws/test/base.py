from threemystic_cloud_client.cloud_providers.aws.base_class.base import cloud_client_provider_aws_base as base

class cloud_client_aws_test_base(base):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

  # There is not post init when in Config Mode
  def _post_init(self, *args, **kwargs):
    pass
    
  def update_config_profile(self, config, profile_name, running_config, auto_save = True, *args, **kwargs):
    if config is None:
      config = self._load_config()

    if config.get("profiles") is None:
      config["profiles"] = {
      }
    
    if config.get("profiles").get("aws") is None:
      config["profiles"]["aws"] = {
      }

    config["profiles"]["aws"][profile_name] = running_config
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