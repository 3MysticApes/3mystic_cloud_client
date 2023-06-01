import sys
from threemystic_common.base_class.base_script_options import base_process_options


class cloud_client_cli(base_process_options):
  def __init__(self, *args, **kwargs):
    from threemystic_cloud_client.cloud_client import cloud_client
    self._cloud_client = cloud_client()
    
    super().__init__(common= self._cloud_client.get_common(), *args, **kwargs)

    self.parser = self.get_parser(
      parser_init_kwargs = {
        "description": "One Action is required"
      },
      parser_args = {
        # I can create other actions just by duplication this and changing the const
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
      }
    )

    processed_info = self.process_opts(
      parser = self.parser
    )

    self._client_action = processed_info["processed_data"].get("client_action")
    
    
  def __process_client_action(self, action):
    if action == "config":
      from threemystic_cloud_client.cli.actions.config import cloud_client_config as user_action
      user_action(cloud_client= self._cloud_client).main()
      return

    if action == "test":
      from threemystic_cloud_client.cli.actions.test import cloud_client_test as user_action
      user_action(cloud_client= self._cloud_client).main()
      return

    return

  def main(self, *args, **kwargs):    

    print(f"Thank you for using the 3 Mystic Apes Cloud Client. You currenly have installed\n3mystic_cloud_client version {self._cloud_client.version()}\n3mystic_common version {self._cloud_client.get_common().version()}")
    print()
    print()

    if self._client_action is None:
      self.parser.print_help()
      return
    
    self.__process_client_action(action= self._client_action )

def main(*args, **kwargs):    
  cloud_client_cli(*args, **kwargs).main(*args, **kwargs)
    

if __name__ == '__main__':   
  cloud_client_cli().main(sys.argv[1:])