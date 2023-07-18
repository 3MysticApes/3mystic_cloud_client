from threemystic_cloud_client.cloud_providers.aws.action_test.base_class.base import cloud_client_aws_test_base as base
from threemystic_common.base_class.base_script_options import base_process_options
import textwrap, argparse


class cloud_client_aws_token_step_1(base):
  def __init__(self, *args, **kwargs):
    super().__init__(logger_name= "cloud_client_aws_token", *args, **kwargs)

    self._process_cli_args()
    
  def _process_cli_args(self, *args, **kwargs):
    process_options = base_process_options(common= self.get_common())
    token_parser_args = { 
      "--help,-h": {
        "default": False,
        "dest": "client_help",
        "help": "Display Help",
        "action": 'store_true'
      }
    }
    self._arg_parser = process_options.get_parser(
      parser_init_kwargs = {
        "prog": "3mystic_cloud_client --token -p aws",
        "formatter_class": argparse.RawDescriptionHelpFormatter,
        "description": textwrap.dedent('''\
        Requires additional settings.
          --account is required"
        '''),
        "add_help": False,
        "epilog": ""
      },
      parser_args = self.get_common().helper_type().dictionary().merge_dictionary([
        {},
        token_parser_args,
        {
          "--account": {
            "default": None, 
            "type": str,
            "dest": "token_account",
            "help": "The AWS Account ID to generate access token information for",
            "action": 'store'
          },
          "--profile": {
            "default": None, 
            "type": str,
            "dest": "token_profile",
            "help": "The 3Mystic AWS Profile to use. If not provided the default will be used",
            "action": 'store'
          },
          "--format": {
            "default": "cli", 
            "type": str,
            "choices": ["cli", "raw", "export"],
            "dest": "token_format",
            "help": "The format the token will be returned in the options are export, cli, raw. The default is cli",
            "action": 'store'
          }
        },
      ])
    )


    processed_info = process_options.process_opts(
      parser = self._arg_parser
    )
    
    self._processed_arg_info = processed_info.get("processed_data")
  
    
  def step(self, *args, **kwargs):
    if not super().step( *args, **kwargs):
      return
    
    if (self.get_common().helper_type().bool().is_true(check_value= self._processed_arg_info.get("client_help"))):
      self._arg_parser.print_help()
      return
    
    if (self.get_common().helper_type().string().is_null_or_whitespace(string_value= self._processed_arg_info.get("token_account"))):
      self._arg_parser.print_help()
      return

    from threemystic_cloud_client.cloud_client import cloud_client
    aws_client = cloud_client(logger= self.get_common().get_logger(), common=self.get_common()).client(
      provider= "aws",
      profile_name= self._processed_arg_info.get("token_profile")
    )

    if aws_client.session_expired():
      aws_client.authenticate_session(force_quiet= True)
    
    token_format = self.get_common().helper_type().string().set_case(string_value= self._processed_arg_info.get("token_format"), case= "lower")
    if self.get_common().helper_type().string().is_null_or_whitespace(string_value= self._processed_arg_info.get("token_format")):
      token_format = "cli"
    
    if token_format == "raw":
      print(
        self.get_common().helper_json().dumps(data= aws_client.assume_role(account= self._processed_arg_info.get("token_account")))
      )
      return
    
    if token_format == "export":
      print(
        aws_client.convert_assume_role_credentials_export(credentials= aws_client.assume_role(account= self._processed_arg_info.get("token_account")))
      )
      return
    
    if aws_client.session_expired():
      raise self.get_common().exception().exception(exception_type= "generic").exception(
        message= f"You must authenticate with the provider first. To test the connection you can run\n3mystic_cloud_client -p aws -t --profile {aws_client.get_profile().get('profile_name')}"
      )
      return 1
    
    print(
      self.get_common().helper_json().dumps(data= aws_client.convert_assume_role_credentials_cli(credentials= aws_client.assume_role(account= self._processed_arg_info.get("token_account"))))
    )
    return
    
    
  
