from threemystic_cloud_client.cli.actions.base_class.base import cloud_client_action_base as base
from threemystic_common.base_class.base_script_options import base_process_options
import textwrap, argparse

class cloud_client_token(base):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    self._process_options = base_process_options(common= self._cloud_client.get_common())
    self._token_parser_args = {   }

    


  def _process_provider_aws(self, *args, **kwargs):
    parser = self._process_options.get_parser(
      parser_init_kwargs = {
        "prog": "3mystic_cloud_client -p aws --token",
        "formatter_class": argparse.RawDescriptionHelpFormatter,
        "description": textwrap.dedent('''\
        Requires additional settings.
          --account is required"
        '''),
        "add_help": False,
        "epilog": ""
      },
      parser_args = self._cloud_client.get_common().helper_type().dictionary().merge_dictionary([
        {},
        self._token_parser_args,
        {
          "--account": {
            "default": None, 
            "type": str,
            "dest": "token_account",
            "help": "The AWS Account ID to generate access token information for",
            "action": 'store'
          }
        },
        {
          "--profile": {
            "default": None, 
            "type": str,
            "dest": "token_profile",
            "help": "The 3Mystic profile to use.",
            "action": 'store'
          }
        }
      ])
    )


    processed_info = self._process_options.process_opts(
      parser = parser
    )

    if self._cloud_client.get_common().helper_type().string().is_null_or_whitespace(string_value= processed_info["processed_data"].get("token_account")):
      parser.print_help()
      return
    
      
    from threemystic_cloud_client.cloud_providers.aws import cloud_client_aws as client
    client(common= self._cloud_client.get_common()).action_token()


  def _process_provider_azure(self, *args, **kwargs):
    parser = self._process_options.get_parser(
      parser_init_kwargs = {
        "prog": "3mystic_cloud_client -p azure --token",
        "formatter_class": argparse.RawDescriptionHelpFormatter,
        "description": textwrap.dedent('''\
        Requires additional settings.
          --resource / --resource-type is required

          To learn more please see: https://learn.microsoft.com/en-us/cli/azure/account?view=azure-cli-latest#az-account-get-access-token
        '''),
        "add_help": False,
        "epilog": ""
      },
      parser_args = self._cloud_client.get_common().helper_type().dictionary().merge_dictionary([
        {},
        self._token_parser_args,
        {
          "--resource": {
            "default": None, 
            "type": str,
            "dest": "token_resource",
            "help": "Azure resource endpoints in AAD v1.0.",
            "action": 'store'
          },
          "--resource-type": {
            "default": None, 
            "type": str,
            "dest": "token_resource_type",
            "help": "Type of well-known resource. ie aad-graph, arm, ms-graph",
            "action": 'store'
          },
          "--scope": {
            "default": None, 
            "type": str,
            "dest": "token_scope",
            "help": "Comma Seperated AAD scopes in AAD v2.0.",
            "action": 'store'
          },
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


    processed_info = self._process_options.process_opts(
      parser = parser
    )

    if (self._cloud_client.get_common().helper_type().string().is_null_or_whitespace(string_value= processed_info["processed_data"].get("token_resource")) or 
      self._cloud_client.get_common().helper_type().string().is_null_or_whitespace(string_value= processed_info["processed_data"].get("token_resource_type"))):
      parser.print_help()
      return
    
    from threemystic_cloud_client.cloud_providers.azure import cloud_client_azure as client
    client(common= self._cloud_client.get_common()).action_token()      

      

  
