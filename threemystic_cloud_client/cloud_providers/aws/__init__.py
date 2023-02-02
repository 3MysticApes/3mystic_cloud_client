from threemystic_cloud_client.cloud_providers.base_class.base import cloud_client_provider_base as base
from threemystic_common.base_class.generate_data.generate_data_handlers import generate_data_handlers
from threemystic_cloud_client.cloud_providers.aws.config.step_1 import cloud_client_aws_config_step_1 as step


class cloud_client_aws(base):
  def __init__(self, *args, **kwargs):
    super().__init__(logger_name= "cloud_client_aws", provider= "aws", *args, **kwargs)

  def config(self, *args, **kwargs):
    cli_doc_link = "https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
    ssm_doc_link = "https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html"
    saml2aws_doc_link = "https://github.com/Versent/saml2aws"

    
    config = self._load_config()
    next_step = step(common= self.get_common(), logger= self.get_logger())
    print("The aws cli is required for setup.")
    print()
    print(f"if you need to install the cli you can goto here: {cli_doc_link}\nIt is also highly recommended to install the ssm plugin here: {ssm_doc_link}")
    print()
    print(f"If you are using saml2aws you need to also install {saml2aws_doc_link}")
    print()
    print()
    print("-----------------------------")
    
    if config.get("cli_installed") != True:
      config["cli_installed"] = self._is_aws_installed()
    
    if config["cli_installed"] is None:
      return
    
    if self.is_cli_installed(config= config) != True:
      print("Please install the aws cli and if needed saml2aws before continuing")
      return
    
    next_step.step(config= config)


  def _is_aws_installed(self):
    response = self.get_common().generate_data().generate(
      generate_data_config = {
        "installed": {
            "validation": lambda item: self.get_common().helper_type().bool().is_bool(check_value= item),
            "messages":{
              "validation": f"Valid options for Yes are: {self.get_common().helper_type().bool().is_true_values()}",
            },
            "conversion": lambda item: self.get_common().helper_type().bool().is_true(check_value= item),
            "desc": f"Have you already installed the aws cli and saml2aws if needed?\nValid Options: {self.get_common().helper_type().bool().is_true_values()}",
            "default": False,
            "handler": generate_data_handlers.get_handler(handler= "base"),
            "optional": True
        }
      }
    )

    
    return self.__get_installed(installed= response) == True

  def __get_installed(self, installed, *args, **kwargs):
    if installed is None:
      return ""
    
    if installed.get("installed") is not None:
      return self.__get_installed(installed= installed.get("installed"))
    
    return installed.get("formated") if installed.get("formated") is not None else False
    
    
  
