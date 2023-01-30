from threemystic_cloud_client.base_class.base import base

class cloud_client_aws_config_base(base):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

  @classmethod
  def is_cli_installed(cls, config, *args, **kwargs):
    return config["cli_installed"] == True

  @classmethod
  def valid_auth_options(cls, *args, **kwargs):
    return ["sso"]

  @classmethod
  def config_path(cls, common, *args, **kwargs):
    return common.get_threemystic_config_path().joinpath("3mystic_cloud_client_config")
    
  @classmethod
  def aws_config_path(cls, *args, **kwargs):
    return "~/.aws/config"
  
  @classmethod
  def get_existing_profiles(cls, config):
    return config.get("profiles") if config is not None else None 
  
  @classmethod
  def update_config_profile(cls, config, common, profile_name, running_config, auto_save = True):
    if config.get("profiles") is None:
      config["profiles"] = {}

    config["profiles"][profile_name] = running_config
    if auto_save:
      cls.save_config(config= config, common= common)

    return config
  
  @classmethod
  def save_config(cls, config, common):
     cls.config_path(common= common).write_text(
      data= common.helper_yaml().dumps(data= config)
     )
  
  @classmethod
  def load_config(cls, common):
     return common.helper_yaml().load_file(path= cls.config_path(common= common))
  
  def step(self, config, *args, **kwargs):
    
    if self.is_cli_installed(config= config) != True:
      print("aws cli is not marked as installed please start over")
      return False

    return True