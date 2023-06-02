from threemystic_cloud_client.cloud_providers.aws.test.base import cloud_client_aws_test_base as base
from threemystic_common.base_class.generate_data.generate_data_handlers import generate_data_handlers


class cloud_client_aws_test_step_1(base):
  def __init__(self, *args, **kwargs):
    super().__init__(logger_name= "cloud_client_aws_test", provider= "aws", *args, **kwargs)
    

  def step(self, config, profile, *args, **kwargs):
    if not super().step(config= config, *args, **kwargs):
      return
    
    
    
    
  
