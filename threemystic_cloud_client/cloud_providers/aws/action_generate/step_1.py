from threemystic_cloud_client.cloud_providers.aws.action_test.base_class.base import cloud_client_aws_test_base as base
from threemystic_common.base_class.base_script_options import base_process_options
from threemystic_common.base_class.generate_data.generate_data_handlers import generate_data_handlers
import textwrap, argparse
from threemystic_cloud_client.cloud_client import cloud_client
import re

class cloud_client_aws_generate_step_1(base):
  def __init__(self, *args, **kwargs):
    super().__init__(logger_name= "cloud_client_aws_token", *args, **kwargs)
    
    
    self._process_cli_args()
    self.__generate_format_options = {
      "accountId": {
        "description": "This will be replaced with the account id",
        "handler": lambda item: self._aws_client.get_account_id(account= item["account"])
      },
      "accountName": {
        "description": "This will be replaced with the account name spaces will be replaced with dashes",
        "handler": lambda item: self.get_common().helper_type().string().join("-", str_array= self.get_common().helper_type().string().split(
          string_value= self._aws_client.get_account_name(account= item["account"]),
          separator= "[^a-zA-Z0-9\-\_]"
        ))
      },
      "roleName": {
        "description": "The user role from the aws connection.",
        "handler": lambda item: self._aws_client.get_default_rolename()
      },
      "profileName": {
        "description": "The 3Mystic Cloud Client Profile Name",
        "handler": lambda item: self._aws_client.get_profile().get("profile_name")
      }
    }
    
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
        "prog": "3mystic_cloud_client --generate -p aws",
        "formatter_class": argparse.RawDescriptionHelpFormatter,
        "description": textwrap.dedent('''\
        This tool will help auto generate the aws config file. It will override anyhting alreayd there and will not generate a default profile.
        '''),
        "add_help": False,
        "epilog": ""
      },
      parser_args = self.get_common().helper_type().dictionary().merge_dictionary([
        {},
        token_parser_args,
        {
          "--profile": {
            "default": None, 
            "type": str,
            "dest": "token_profile",
            "help": "The 3Mystic AWS Profile to use. If not provided the default will be used",
            "action": 'store'
          },
        },
      ])
    )


    processed_info = process_options.process_opts(
      parser = self._arg_parser
    )
    
    self._processed_arg_info = processed_info.get("processed_data")
  
  def get_valid_profile_name_options(self, *args, **kwargs):
    return self.__generate_format_options
  
  def get_valid_profile_name_options_display(self, *args, **kwargs):
    for key, item in self.get_valid_profile_name_options().items():
      print(f'{key}: {item.get("description")}')
  
  def step(self, *args, **kwargs):
    if not super().step( *args, **kwargs):
      return
    
    if (self.get_common().helper_type().bool().is_true(check_value= self._processed_arg_info.get("client_help"))):
      self._arg_parser.print_help()
      return
    
    self._aws_client = cloud_client(logger= self.get_common().get_logger(), common=self.get_common()).client(
      provider= "aws",
      profile_name= self._processed_arg_info.get("token_profile")
    )
    
    response = self.get_common().generate_data().generate(
      generate_data_config = {
        "format": {
            "validation": lambda item: ((not self.get_common().helper_type().string().is_null_or_whitespace(string_value= item)) 
                                        and self.get_common().helper_type().string().set_case(string_value= self.get_common().helper_type().string().trim(string_value= item), case= "lower") not in ["default", "profile"]
                                        ),
            "messages":{
              "validation": f"The processed name cannot be profile or default.",
            },
            "conversion": lambda item: self.get_common().helper_type().string().trim(string_value= item),
            "desc": f"What should the format be?\nFormat Variables:\n{self.get_valid_profile_name_options_display()}",
            "default": "{accountName}-{roleName}",
            "handler": generate_data_handlers.get_handler(handler= "base"),
            "optional": True
        }
      }
    )

    if response is None:
      return
    
    self.step_process_generation(format= response.get("format").get("formated"))

  def step_process_generation(self, format, *args, **kwargs):
    if self.get_common().helper_type().string().is_null_or_whitespace(string_value= format):
      format = "{accountName}-{roleName}"

    aws_config = self.get_common().helper_config().load(
      config_type = "config",
      path= self.get_aws_user_path_config()
    )
    
    for account in self._aws_client.get_accounts():
      profile = format
      for key, item in self.get_valid_profile_name_options().items():
        profile= re.sub(
          pattern=f"{{{key}}}", 
          repl= item.get("handler")({"account": account}),
          string= profile, count=0)
      
      aws_config[f"profile {profile}"] = {
        "credential_process": f"3mystic_cloud_client --token -p aws --format cli --profile {self._aws_client.get_profile().get('profile_name')} --account {self._aws_client.get_account_id(account= account)}",
        "region": self._aws_client.get_default_region()
      }
      print(f'Profile - {profile} - Generated for {self._aws_client.get_account_name(account= account)} - {self._aws_client.get_account_id(account= account)}')
  
    with open(self.get_aws_user_path_config(), 'w') as configfile:
      aws_config.write(configfile)

    print("-----------------------------")
    print()
    print()
    print("AWS Config Updated")
    print()
    print()
    print("-----------------------------")
      

      

    
  
