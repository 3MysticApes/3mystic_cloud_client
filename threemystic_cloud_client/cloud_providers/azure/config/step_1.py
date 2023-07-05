from threemystic_cloud_client.cloud_providers.azure.config.base_class.base import cloud_client_azure_config_base as base

class cloud_client_azure_config_step_1(base):
  def __init__(self, *args, **kwargs):
    super().__init__(logger_name= "cloud_client_azure_config_step_1", *args, **kwargs)
    

  def step(self, *args, **kwargs):
    
    if not super().step(force_cli_installed_prompt= True):
      return
    
    if self.is_cli_installed() == True:
      print("Currently this app integrates directly with the azure cli. So as long as the CLI is installed the base is done.")
      print()
      self.update_provider_config_completed(status= True)
    else:
      print("The Azure CLI is required please rerun the config once the CLI has been installed.")
      print()

    self._setup_another_config()
    