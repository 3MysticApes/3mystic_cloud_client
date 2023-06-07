from threemystic_cloud_client.cloud_providers.aws.base_class.base import cloud_client_provider_aws_base as base


class cloud_client_aws(base):
  def __init__(self, *args, **kwargs):
    super().__init__(logger_name= "cloud_client_aws", provider= "aws", *args, **kwargs)
  
  # There is not post init when in Config Mode
  def _post_init(self, *args, **kwargs):
    pass
  
  def action_test(self, *args, **kwargs):
    from threemystic_cloud_client.cloud_providers.aws.test.step_1 import cloud_client_aws_test_step_1 as test
    next_step = test(common= self.get_common(), logger= self.get_logger(), *args, **kwargs)

    if self.is_cli_installed() != True:
      print("Please install the aws cli")
      return
    
    next_step.step()

  def action_config(self, *args, **kwargs): 
    
    from threemystic_cloud_client.cloud_providers.aws.config.step_1 import cloud_client_aws_config_step_1 as step
    next_step = step(common= self.get_common(), logger= self.get_logger())
    
    next_step.step()


  
    
    
  
