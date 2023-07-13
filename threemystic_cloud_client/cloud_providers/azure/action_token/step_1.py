from threemystic_cloud_client.cloud_providers.azure.action_test.base_class.base import cloud_client_azure_test_base as base
from threemystic_common.base_class.generate_data.generate_data_handlers import generate_data_handlers
from threemystic_common.base_class.base_script_options import base_process_options
import textwrap, argparse


class cloud_client_azure_token_step_1(base):
  def __init__(self, *args, **kwargs):
    super().__init__(logger_name= "cloud_client_azure_token", *args, **kwargs)

    self._process_cli_args()
    
  def _process_cli_args(self, *args, **kwargs):
    process_options = base_process_options(common= self.get_common())
    token_parser_args = {   }
    self._arg_parser = process_options.get_parser(
      parser_init_kwargs = {
        "prog": "3mystic_cloud_client --token -p azure",
        "formatter_class": argparse.RawDescriptionHelpFormatter,
        "description": textwrap.dedent('''\
        Requires additional settings.
          --tenant is required
          --resource is required

          To learn more please see: https://learn.microsoft.com/en-us/cli/azure/account?view=azure-cli-latest#az-account-get-access-token
        '''),
        "add_help": False,
        "epilog": ""
      },
      parser_args = self.get_common().helper_type().dictionary().merge_dictionary([
        {},
        token_parser_args,
        {
          "--resource": {
            "default": None, 
            "type": str,
            "dest": "token_resource",
            "help": "Azure resource endpoints in AAD v1.0.",
            "action": 'store'
          },
          # "--resource-type": {
          #   "default": None, 
          #   "type": str,
          #   "dest": "token_resource_type",
          #   "help": "Type of well-known resource. ie aad-graph, arm, ms-graph",
          #   "action": 'store'
          # },
          # "--scope": {
          #   "default": None, 
          #   "type": str,
          #   "dest": "token_scope",
          #   "help": "Comma Seperated AAD scopes in AAD v2.0.",
          #   "action": 'store'
          # },
          "--tenant": {
            "default": None, 
            "type": str,
            "dest": "token_tenant",
            "help": "Tenant ID for which the token is acquired.",
            "action": 'store'
          }
        }
      ])
    )


    processed_info = process_options.process_opts(
      parser = self._arg_parser
    )

    self._processed_arg_info = processed_info.get("processed_data")
  
    
  def step(self, *args, **kwargs):
    if not super().step( *args, **kwargs):
      return
    
    if (self.get_common().helper_type().string().is_null_or_whitespace(string_value= self._processed_arg_info.get("token_tenant")) or (self.get_common().helper_type().string().is_null_or_whitespace(string_value= self._processed_arg_info.get("token_resource")) and 
      self.get_common().helper_type().string().is_null_or_whitespace(string_value= self._processed_arg_info.get("token_resource_type")))):
      self._arg_parser.print_help()
      return

    from threemystic_cloud_client.cloud_client import cloud_client
    azure_client = cloud_client(logger= self.get_common().get_logger(), common=self.get_common()).client(
      provider= "azure"
    )
    
    tenant_credential = azure_client.get_tenant_credential(
      tenant= self._processed_arg_info.get("token_tenant")
    )
    
    if not (self.get_common().helper_type().string().is_null_or_whitespace(string_value= self._processed_arg_info.get("token_resource"))): 
      token_data = tenant_credential.get_token(self._processed_arg_info.get("token_resource"))
      print(self.get_common().helper_json().dumps(data= {
        "token": token_data.token,
        "expires_on": token_data.expires_on
        }))
    
  
