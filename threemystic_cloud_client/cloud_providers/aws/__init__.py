from threemystic_cloud_client.cloud_providers.aws.base_class.base import cloud_client_provider_aws_base as base


class cloud_client_aws(base):
  def __init__(self, *args, **kwargs):
    super().__init__(logger_name= "cloud_client_aws", *args, **kwargs)
  
  # There is not post init when in Config Mode
  def _post_init(self, *args, **kwargs):
    pass
  
  def action_test(self, *args, **kwargs):
    if not self.is_provider_config_completed():
      print("Provider must be configured first")
      self._setup_another_config()
      return
    from threemystic_cloud_client.cloud_providers.aws.action_test.step_1 import cloud_client_aws_test_step_1 as test
    next_step = test(common= self.get_common(), logger= self.get_common().get_logger(), *args, **kwargs)
    
    next_step.step()

  def action_config(self, *args, **kwargs):     
    from threemystic_cloud_client.cloud_providers.aws.config.step_1 import cloud_client_aws_config_step_1 as step
    next_step = step(common= self.get_common(), logger= self.get_common().get_logger())
    
    next_step.step()

  def action_token(self, *args, **kwargs):     
    from threemystic_cloud_client.cloud_providers.aws.action_token.step_1 import cloud_client_aws_token_step_1 as step
    next_step = step(common= self.get_common(), logger= self.get_common().get_logger())
    
    next_step.step()

  def action_generate(self, *args, **kwargs):     
    from threemystic_cloud_client.cloud_providers.aws.action_generate.step_1 import cloud_client_aws_generate_step_1 as step
    next_step = step(common= self.get_common(), logger= self.get_common().get_logger())
    
    next_step.step()


  
    
    
  
