from threemystic_cloud_client.cloud_providers.aws.test.base import cloud_client_aws_test_base as base
from threemystic_common.base_class.generate_data.generate_data_handlers import generate_data_handlers


class cloud_client_aws_test_step_1(base):
  def __init__(self, *args, **kwargs):
    super().__init__(logger_name= "cloud_client_aws_test", provider= "aws", *args, **kwargs)
    

  def step(self, config, *args, **kwargs):
    if not super().step(config= config, *args, **kwargs):
      return
    
    
    response = self.get_common().generate_data().generate(
      generate_data_config = {
        "profile": {
            "validation": lambda item: self.profile_exists(config= config, profile_name= item),
            "messages":{
              "validation": f"Please enter a valid existing Cloud Client Profile",
            },
            "conversion": lambda item: self.get_common().helper_type().string().trim(string_value= item).lower(),
            "desc": f"What Cloud Client Profile to load",
            "handler": generate_data_handlers.get_handler(handler= "base"),
            "optional": True,
            "default": 
        }
      }
    )

    if response is None:
      return

    if not self.profile_exists(config= config, profile_name= response["profile"].get("formated")):
      print(f"Profile Not Found: {response['profile'].get('formated')}")
      return

    print(f"Profile Found: {response['profile'].get('formated')}")
    from threemystic_cloud_client.cloud_providers.aws.test.step_2 import cloud_client_aws_test_step_2 as nextstep
    nextstep(init_object = self).step(config= config, profile= response['profile'].get('formated'))
    
  
