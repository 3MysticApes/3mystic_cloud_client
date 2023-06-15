from threemystic_cloud_client.cloud_providers.aws.base_class.base import cloud_client_provider_aws_base as base
from threemystic_common.base_class.generate_data.generate_data_handlers import generate_data_handlers

class cloud_client_aws_config_base(base):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

  def update_config_profile(self, profile_name, profile_data, auto_save = True, *args, **kwargs):

    profile_name = self.get_common().helper_type().string().set_case(string_value= profile_name, case= "lower")
    self.get_config_profiles()[profile_name] = profile_data
    if(profile_data["default_profile"]):
      if(profile_name != self.get_default_profile_name() and self.has_default_profile()):

        for existing_profile, existing_profile_data in self.get_config_profiles().items():
          if(not existing_profile_data["default_profile"] or existing_profile == profile_name):
            continue

          existing_profile_data["default_profile"] = False
    
    if auto_save:
      self._save_config()
  
  def update_is_cli_installed(self, is_cli_installed, *args, **kwargs):
    config = self.get_config()
    
    config["cli_installed"] = is_cli_installed

    self._save_config()
  
  def update_sdk_auth(self, sdk_auth = "cli", *args, **kwargs):
    config = self.get_config()
    
    config["sdk_auth"] = sdk_auth

    self._save_config()
     
  def step(self, force_cli_installed_prompt = False, *args, **kwargs):
    
    if (self.is_cli_installed() != True or force_cli_installed_prompt):   
      print("The aws cli is required for setup.")
      print()
      print(f"if you need to install the cli you can goto here: {self.links['cli_doc_link']}\nIt is also highly recommended to install the ssm plugin here: {self.links['ssm_doc_link']}")
      print()
      print()
      print("-----------------------------")
      
      self.update_is_cli_installed(is_cli_installed= self._is_aws_installed())
      self.update_sdk_auth()
      print("cli state updated")
      print("-----------------------------")
      
      if self.is_cli_installed() != True:
        print("Please install the aws cli, if its not already installed.")
        return False

    return True

  def _is_aws_installed(self):
    response = self.get_common().generate_data().generate(
      generate_data_config = {
        "installed": {
            "validation": lambda item: self.get_common().helper_type().bool().is_bool(check_value= item),
            "messages":{
              "validation": f"Valid options for Yes are: {self.get_common().helper_type().bool().is_true_values()}",
            },
            "conversion": lambda item: self.get_common().helper_type().bool().is_true(check_value= item),
            "desc": f"Have you already installed the aws cli?\nValid Options: {self.get_common().helper_type().bool().is_true_values()}",
            "default": self.is_cli_installed(),
            "handler": generate_data_handlers.get_handler(handler= "base"),
            "optional": True
        },
      }
    )

    
    return self.__get_installed(installed= response) == True

  def __get_installed(self, installed, *args, **kwargs):
    if installed is None:
      return ""
    
    if installed.get("installed") is not None:
      return self.__get_installed(installed= installed.get("installed"))
    
    return installed.get("formated") if installed.get("formated") is not None else False