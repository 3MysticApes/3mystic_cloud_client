from threemystic_cloud_client.cloud_providers.azure.base_class.base import cloud_client_provider_azure_base as base

class cloud_client_azure(base):
  def __init__(self, *args, **kwargs):
    super().__init__(logger_name= "cloud_client_azure", provider= "azure", *args, **kwargs)
  
  def config(self, *args, **kwargs):
    cli_doc_link = "https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-windows?tabs=azure-cli"

    print("Currently this app integrates directly with the azure cli. If you  have not configured the azure cli plus do so now.")
    print()
    print(f"if you need to install the cli you can goto here: {cli_doc_link}")
    
    
  
