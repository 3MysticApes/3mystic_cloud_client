from threemystic_cloud_client.cloud_providers.azure.base_class.base import cloud_client_provider_azure_base as base
from threemystic_common.base_class.generate_data.generate_data_handlers import generate_data_handlers

class cloud_client_azure_config_base(base):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

  
  def _login(self, *args, **kwargs):
    pass
  
  def update_is_cli_installed(self, is_cli_installed, *args, **kwargs):
    config = self.get_config()
    if(config is None):
      config = {}
    
    config["cli_installed"] = is_cli_installed

    self._save_config()
  
  def update_sdk_auth(self, sdk_auth = "cli", *args, **kwargs):
    config = self.get_config()
    
    config["sdk_auth"] = sdk_auth

    self._save_config()
     
  def step(self, force_cli_installed_prompt = False, *args, **kwargs):
    
    if (self.is_cli_installed() != True or force_cli_installed_prompt):   
      print("The azure cli is required for setup.")
      print()
      print(f"if you need to install the cli you can goto here: {self.links['cli_doc_link']}")
      print("To ensure your base configuration please run: az configure")
      print()
      print()
      print("-----------------------------")
      
      self.update_is_cli_installed(is_cli_installed= self._is_azure_installed())
      self.update_sdk_auth()
      print("cli state updated")
      print("-----------------------------")
      
      if self.is_cli_installed() != True:
        print("Please install the azure cli")
        return False

    return True

  def _is_azure_installed(self):
    response = self.get_common().generate_data().generate(
      generate_data_config = {
        "installed": {
            "validation": lambda item: self.get_common().helper_type().bool().is_bool(check_value= item),
            "messages":{
              "validation": f"Valid options for Yes are: {self.get_common().helper_type().bool().is_true_values()}",
            },
            "conversion": lambda item: self.get_common().helper_type().bool().is_true(check_value= item),
            "desc": f"Have you already installed the azure cli?\nValid Options: {self.get_common().helper_type().bool().is_true_values()}",
            "default": self.is_cli_installed(),
            "handler": generate_data_handlers.get_handler(handler= "base"),
            "optional": True
        }
      }
    )

    
    return self.__get_installed(installed= response) == True

  def __get_installed(self, installed, *args, **kwargs):
    if installed is None:
      return ""
    
    if installed.get("installed") is not None:
      return self.__get_installed(installed= installed.get("installed"))
    
    return installed.get("formated") if installed.get("formated") is not None else False