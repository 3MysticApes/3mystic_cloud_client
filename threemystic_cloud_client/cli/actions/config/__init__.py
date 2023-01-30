import sys
from threemystic_common.base_class.generate_data.generate_data_handlers import generate_data_handlers


class cloud_client_config():
  def __init__(self, cloud_client, *args, **kwargs):
    self._cloud_client = cloud_client

  def main(self, *args, **kwargs):
    response = self._cloud_client.get_common().generate_data().generate(
      generate_data_config = {
        "provider": {
            "validation": lambda item: self._cloud_client.get_common().helper_type().string().trim(self._cloud_client.get_common().helper_type().string().set_case(string_value= item, case= "lower")) in self._cloud_client.get_supported_providers(),
            "messages":{
              "validation": f"Valid Provider Options: {self._cloud_client.get_supported_providers()}",
            },
            "conversion": lambda item: self._cloud_client.get_common().helper_type().string().trim(string_value= self._cloud_client.get_common().helper_type().string().set_case(string_value= item, case= "lower")) if item is not None else None,
            "desc": f"Which provider should we configure\nvalid options are {self._cloud_client.get_supported_providers()}",
            "default": None,
            "handler": generate_data_handlers.get_handler(handler= "base"),
            "optional": True
        }
      }
    )
    
    provider = self.__get_provider(response).lower()
    if provider not in self._cloud_client.get_supported_providers():
      return
    
    if provider == "azure":
      from threemystic_cloud_client.cloud_providers.azure import cloud_client_azure as client
      client(common= self._cloud_client.get_common()).config()

    
    if provider == "aws":
      from threemystic_cloud_client.cloud_providers.aws  import cloud_client_aws as client
      client(common= self._cloud_client.get_common()).config()
  
  def __get_provider(self, provider, *args, **kwargs):
    if provider is None:
      return ""

    if provider.get("provider") is not None:
      return self.__get_provider(provider= provider.get("provider"))
    
    return provider.get("formated") if provider.get("formated") is not None else ""
      

  
