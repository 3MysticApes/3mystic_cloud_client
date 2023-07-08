from threemystic_cloud_client.cli.actions.base_class.base import cloud_client_action_base as base
from threemystic_common.base_class.base_script_options import base_process_options
import textwrap, argparse

class cloud_client_token(base):
  def __init__(self, *args, **kwargs):
    super().__init__(action= "--token", *args, **kwargs)    


  def _process_provider_aws(self, *args, **kwargs):    
    from threemystic_cloud_client.cloud_providers.aws import cloud_client_aws as client
    client(common= self._cloud_client.get_common()).action_token()


  def _process_provider_azure(self, *args, **kwargs):
    
    from threemystic_cloud_client.cloud_providers.azure import cloud_client_azure as client
    client(common= self._cloud_client.get_common()).action_token()      

      

  
