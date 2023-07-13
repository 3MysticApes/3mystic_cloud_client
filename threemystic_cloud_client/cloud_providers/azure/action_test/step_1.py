from threemystic_cloud_client.cloud_providers.azure.action_test.base_class.base import cloud_client_azure_test_base as base
from threemystic_common.base_class.generate_data.generate_data_handlers import generate_data_handlers


class cloud_client_azure_test_step_1(base):
  def __init__(self, *args, **kwargs):
    super().__init__(logger_name= "cloud_client_azure_test", *args, **kwargs)
    

  def step(self, *args, **kwargs):
    if not super().step( *args, **kwargs):
      return
    
    from threemystic_cloud_client.cloud_client import cloud_client
    azure_client = cloud_client(logger= self.get_common().get_logger(), common=self.get_common()).client(
      provider= "azure"
    )
    
    print(f"You have the following tenants:")
    for tenant in azure_client.get_tenants():
      print(f"{azure_client.get_tenant_id(tenant= tenant)}")
    
    print(f"You have the following accounts:")
    for account in azure_client.get_accounts():
      print(f"{azure_client.get_account_id(account= account)}:{azure_client.get_account_name(account= account)}")

    print()
    print()
    print("--------------------------------")
    print()
    print()
    print("If not all your accounts are listing you can try the commands below. ")
    print("If accounts are still missing please log into the portal and verify all the tenants. It is possible they are missing from the CLI.")
    for tenant in azure_client.get_tenants():
      print(f"az login --tenant {azure_client.get_tenant_id(tenant= tenant)}")

    print(f"az account list --refresh")
    
  
