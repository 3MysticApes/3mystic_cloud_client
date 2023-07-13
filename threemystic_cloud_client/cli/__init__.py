import sys
from threemystic_common.base_class.base_script_options import base_process_options
from threemystic_cloud_client.cloud_client import cloud_client as threemystic_client

class cloud_client_cli(base_process_options):
  def __init__(self, cloud_client = None, *args, **kwargs):    
    self._cloud_client = threemystic_client() if cloud_client is None else cloud_client
    
    super().__init__(common= self._cloud_client.get_common(), *args, **kwargs)

    self.parser = self.get_parser(
      parser_init_kwargs = {
        "description": "One Action is required",
        "add_help": False,
      },
      parser_args = {
        "--help,-h": {
          "default": False,
          "dest": "client_help",
          "help": "Display Help",
          "action": 'store_true'
        },
        # I can create other actions just by duplication this and changing the const,
        "--version": {
            "default": None, 
            "const": "version",
            "dest": "client_action",
            "help": "Action: outputs the versions of the app being used.",
            "action": 'store_const'
        },
        "--config,-c": {
            "default": None, 
            "const": "config",
            "dest": "client_action",
            "help": "Action: This is so you can setup the cloud client to work with various providers",
            "action": 'store_const'
        },
        "--test,-t": {
            "default": None, 
            "const": "test",
            "dest": "client_action",
            "help": "Action: This is so you can test the config setup to ensure the base connection is good",
            "action": 'store_const'
        },
        "--token": {
            "default": None, 
            "const": "token",
            "dest": "client_action",
            "help": "Action: This is so that you can generate the required token.",
            "action": 'store_const'
        },
        "--generate,-g": {
            "default": None, 
            "const": "generate",
            "dest": "client_action",
            "help": "Action: For providers like aws it is easier to have a profile when interacting with the accounts. This will help generate the various profiles.",
            "action": 'store_const'
        },
        "--provider,-p": {
            "default": None, 
            "type": str,
            "choices": self._cloud_client.get_supported_providers(),
            "dest": "client_provider",
            "help": "Provider: This is to set the provider that should be used",
            "action": 'store'
        }
      }
    )

    processed_info = self.process_opts(
      parser = self.parser
    )

    for key, value in processed_info["processed_data"].items():
      setattr(self, f"_{key}", value)
    
    
  def process_client_action(self, force_action = None, *args, **kwargs):
    if self._cloud_client.get_common().helper_type().string().is_null_or_whitespace(string_value= force_action):
      force_action = self.__get_client_acount()

    if self._cloud_client.get_common().helper_type().string().is_null_or_whitespace(string_value= force_action):
      self.parser.print_help()
      return
    
    if force_action == "version":
      self.version_dispaly()
      return
    
    if self._cloud_client.get_common().helper_type().string().is_null_or_whitespace(string_value=  self.__get_client_provider()):
      self.parser.print_usage()

    if force_action == "config":
      from threemystic_cloud_client.cli.actions.config import cloud_client_config as user_action
      user_action(cloud_client= self._cloud_client).main(provider= self.__get_client_provider())
      return

    if force_action == "test":
      from threemystic_cloud_client.cli.actions.action_test import cloud_client_test as user_action
      user_action(cloud_client= self._cloud_client).main(provider= self.__get_client_provider())
      return

    if force_action == "token":
      from threemystic_cloud_client.cli.actions.action_token import cloud_client_token as user_action
      user_action(cloud_client= self._cloud_client).main(provider= self.__get_client_provider())
      return

    if force_action == "generate":
      from threemystic_cloud_client.cli.actions.action_generate import cloud_client_generate as user_action
      user_action(cloud_client= self._cloud_client).main(provider= self.__get_client_provider())
      return

    return

  def version_dispaly(self, *args, **kwargs): 
    print(f"You currenly have installed")
    print(f"3mystic_cloud_client: v{self._cloud_client.version()}")
    print(f"3mystic_common: v{self._cloud_client.get_common().version()}")
    print()

  def __get_client_provider(self, *args, **kwargs):
    if not hasattr(self, "_client_provider"):
      return None
    
    return self._client_provider

  def __get_client_acount(self, *args, **kwargs):
    if not hasattr(self, "_client_action"):
      return None
    
    return self._client_action
  def main(self, *args, **kwargs):    
    if self.__get_client_acount() is None:
      print(f"Thank you for using the 3 Mystic Apes Cloud Client.")
      self.version_dispaly()
      print()
      self.parser.print_help()
      return
    
    self.process_client_action( )

def main(*args, **kwargs):    
  cloud_client_cli(*args, **kwargs).main(*args, **kwargs)
    

if __name__ == '__main__':   
  cloud_client_cli().main(sys.argv[1:])