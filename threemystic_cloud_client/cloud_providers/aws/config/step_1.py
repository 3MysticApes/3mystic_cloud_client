from threemystic_cloud_client.cloud_providers.aws.config.base import cloud_client_aws_config_base as base
from threemystic_common.base_class.generate_data.generate_data_handlers import generate_data_handlers
from threemystic_cloud_client.cloud_providers.aws.config.step_2 import cloud_client_aws_config_step_2 as step


class cloud_client_aws_config_step_1(base):
  def __init__(self, *args, **kwargs):
    super().__init__(logger_name= "cloud_client_aws_config_step_1", *args, **kwargs)
    

  def step(self, config, *args, **kwargs):
    
    if not super().step(config= config):
      return
    
    
    response = self.get_common().generate_data().generate(
      generate_data_config = {
        "type": {
            "validation": lambda item: self.get_common().helper_type().bool().is_bool(check_value= item),
            "messages":{
              "validation": f"Valid options for Yes are: {self.get_common().helper_type().bool().is_true_values()}",
            },
            "conversion": lambda item: self.get_common().helper_type().bool().is_true(check_value= item),
            "desc": f"New Configuration\nValid optiond for yes: {self.get_common().helper_type().bool().is_true_values()}",
            "default": True,
            "handler": generate_data_handlers.get_handler(handler= "base"),
            "optional": True
        }
      }
    )

    if response is None:
      return

    step(init_object = self).step(config= config, is_new_config= response["type"].get("formated") == True)
    
  
