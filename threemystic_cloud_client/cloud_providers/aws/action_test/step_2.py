from threemystic_cloud_client.cloud_providers.aws.action_test.base_class.base import cloud_client_aws_test_base as base
from threemystic_common.base_class.generate_data.generate_data_handlers import generate_data_handlers


class cloud_client_aws_test_step_2(base):
  def __init__(self, *args, **kwargs):
    super().__init__(logger_name= "cloud_client_aws_test2", *args, **kwargs)
    

  def step(self, profile_name, *args, **kwargs):
    if not super().step(*args, **kwargs):
      return
    
    from threemystic_cloud_client.cloud_client import cloud_client
    aws_client = cloud_client(logger= self.get_common().get_logger(), common=self.get_common()).client(
      provider= "aws",
      profile_name= profile_name
    )

    
    print(f"Connected to Account ID: {aws_client.get_main_account_id()}")
    print(f"Org Account ID: {aws_client.get_organization_account_id()}")
    print(f"You have the following accounts:")
    for account in aws_client.get_accounts():
      print(f"{aws_client.get_account_id(account= account)}:{aws_client.get_account_name(account= account)}")
    

    
    
    
    
  
