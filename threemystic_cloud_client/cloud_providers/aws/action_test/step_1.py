from threemystic_cloud_client.cloud_providers.aws.action_test.base_class.base import cloud_client_aws_test_base as base
from threemystic_common.base_class.generate_data.generate_data_handlers import generate_data_handlers
from threemystic_cloud_client.cloud_providers.aws.action_test.step_2 import cloud_client_aws_test_step_2 as nextstep
from threemystic_common.base_class.base_script_options import base_process_options
import textwrap, argparse

class cloud_client_aws_test_step_1(base):
  def __init__(self, *args, **kwargs):
    super().__init__(logger_name= "cloud_client_aws_test", *args, **kwargs)

    self._process_options = base_process_options(common= self.get_common())
    self._token_parser_args = {   }

    self._process_cli_args()
  
  def _process_cli_args(self, *args, **kwargs):
    parser = self._process_options.get_parser(
      parser_init_kwargs = {
        "prog": "3mystic_cloud_client --test -p aws",
        "formatter_class": argparse.RawDescriptionHelpFormatter,
        "description": textwrap.dedent('''\
        Tests the profile configuration
        '''),
        "add_help": False,
        "epilog": ""
      },
      parser_args = self.get_common().helper_type().dictionary().merge_dictionary([
        {},
        self._token_parser_args,
        {
          "--profile": {
            "default": None, 
            "type": str,
            "dest": "test_profile",
            "help": "The 3Mystic profile to use.",
            "action": 'store'
          }
        }
      ])
    )


    processed_arg_info = self._process_options.process_opts(
      parser = parser
    )

    self._processed_arg_info = processed_arg_info.get("processed_data")

  def step(self, *args, **kwargs):
    if not super().step( *args, **kwargs):
      return
    
    if not self.get_common().helper_type().string().is_null_or_whitespace(string_value= self._processed_arg_info.get("test_profile")):
      if self.config_profile_name_exists(profile_name= self._processed_arg_info.get("test_profile")):
        return nextstep(init_object = self).step( profile_name= self._processed_arg_info.get("test_profile"))


    response = self.get_common().generate_data().generate(
      generate_data_config = {
        "profile": {
            "validation": lambda item: self.config_profile_name_exists( profile_name= item),
            "messages":{
              "validation": f"Please enter a valid existing Cloud Client Profile",
            },
            "conversion": lambda item: self.get_common().helper_type().string().set_case(string_value= self.get_common().helper_type().string().trim(string_value= item), case= "lower"),
            "desc": f"What Cloud Client Profile to load",
            "handler": generate_data_handlers.get_handler(handler= "base"),
            "optional": True,
            "default": self.get_default_profile_name()
        }
      }
    )

    if response is None:
      return

    if not self.config_profile_name_exists(profile_name= response["profile"].get("formated")):
      print(f"Profile Not Found: {response['profile'].get('formated')}")
      return

    
    nextstep(init_object = self).step( profile_name= response['profile'].get('formated'))
    
  
