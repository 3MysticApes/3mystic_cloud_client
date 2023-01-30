from threemystic_cloud_client.cloud_providers.aws.config.base import cloud_client_aws_config_base as base
from threemystic_common.base_class.generate_data.generate_data_handlers import generate_data_handlers
import configparser

class cloud_client_aws_config_step_2(base):
  def __init__(self, *args, **kwargs):
    super().__init__(logger_name= "cloud_client_aws_config_step_2", *args, **kwargs)

  def step(self, config, is_new_config, *args, **kwargs):

    if not super().step(config= config):
      return

    if is_new_config:
      self.__step_new(config= config)
      return
    
    self.__step_existing(config= config)

  def __get_profile_data_geerationn(self, *args, **kwargs):
    return {
      "profile_name": {
        "validation": lambda item: self.get_common().helper_type().regex().get(pattern= "^[a-z][a-z0-9_-]{1,}$").fullmatch(self.get_common().helper_type().string().trim(string_value= str(item))) if item is not None else False,
        "messages":{
          "validation": f"It should be alphanumeric and can have underscores or dashes and must start with a letter and be at lest 2 characters ^[a-z][a-z0-9_-]\{1,}$",
        },
        "conversion": lambda item: self.get_common().helper_type().string().trim(string_value= self.get_common().helper_type().string().set_case(string_value= item, case= "lower")) if item is not None else None,
        "desc": f"Profile Name (it will be converted to all lowercase)\nRequirments: alphanumeric and can have underscores or dashes and must start with a letter and be at lest 2 characters ^[a-z][a-z0-9_-]\{1,}$",
        "handler": generate_data_handlers.get_handler(handler= "base"),
        "optional": False
      }
    }
  
  def __get_response_item(self, key, response, *args, **kwargs):
    if response is None:
      return None

    if response.get(key) is not None:
      return self.__get_response_item(key= key, response= response.get(key))
    
    return self.get_common().helper_type().string().set_case(string_value= response.get("formated"), case= "lower")   
    
  def __step_existing(self, config, *args, **kwargs):
    if self.get_existing_profiles(config= config) is None:
      print("No existing profiles please run new")
      return
    
    response = self.get_common().generate_data().generate(
      generate_data_config = self.__get_profile_data_geerationn()
    )
    
    profile_name = self.__get_response_item(key= "profile_name", response= response)

    if profile_name is None:
      return
    
    running_config = None
    for existing_profile_name, existing_config in self.get_existing_profiles(config= config).items():
      if existing_profile_name == profile_name:
        running_config = existing_config
        break

    if running_config is None:
      print("Profile not found")
      return

    if running_config.get("auth_method") == "sso":
      self.__step_process_sso(
        config= config,
        profile_name= profile_name,
        running_config= running_config
      )

  def __step_new(self, config, *args, **kwargs):

    if not super().step(config= config):
      return
    
    running_config = {}
    response = self.get_common().generate_data().generate(
      generate_data_config = self.get_common().helper_type().dictionary().merge_dictionary([
        {}, 
        self.__get_profile_data_geerationn(),
        {
          "auth_method": {
            "validation": lambda item: self.get_common().helper_type().string().set_case(string_value= item, case= "lower") in self.valid_auth_options(),
            "messages":{
              "validation": f"Valid Options: {self.valid_auth_options()}",
            },
            "conversion": lambda item: self.get_common().helper_type().string().trim(string_value= self.get_common().helper_type().string().trim(string_value= self.get_common().helper_type().string().set_case(string_value= item, case= "lower"))) if item is not None else None,
            "desc": f"Which provider should we configure\nvalid options are {self.valid_auth_options()}",
            "handler": generate_data_handlers.get_handler(handler= "base"),
            "optional": False
          }
        }
      ])
    )

    if response is None:
      return
    
    profile_name = self.__get_response_item(key= "profile_name", response= response)
    if self.get_common().helper_type().string().is_null_or_whitespace(string_value= profile_name):
      print("Profile Name was empty.")
      return
      
    running_config["auth_method"] = self.__get_response_item(key= "auth_method", response= response)   
    if self.get_common().helper_type().string().is_null_or_whitespace(string_value= running_config["auth_method"]):
      print("Auth Method was empty.")
      return 
    
    self.__step_process_sso(
      config= config,
      profile_name= profile_name,
      running_config= running_config
    )
  
  def __step_process_sso_valid_profile(self, profile_name, existing_profile, *args, **kwargs):

    if self.get_common().helper_type().string().is_null_or_whitespace(string_value= profile_name):
      return False if self.get_common().helper_type().string().is_null_or_whitespace(string_value= existing_profile) else True
      
    
    profile_name = self.get_common().helper_type().string().trim(string_value= profile_name)  
    config_parser = configparser.ConfigParser()
    with self.get_common().helper_path().expandpath_user(path= self.aws_config_path()).open(mode="r") as config_file:
      config_parser.read_file(config_file)

    return config_parser.has_section(f"profile {profile_name}")

  def get_default_default_profile(self, config, profile_name, running_config):
    if running_config.get("default_profile") == True:
      return True
    
    if self.get_existing_profiles(config= config) is None:
      return True

    for profile, details in self.get_existing_profiles(config= config).items():
      if profile.lower() == profile_name:
        continue

      if details.get("default_profile") != True:
        continue
      
      return False
    
    return True
    


  def __step_process_sso(self, config, profile_name = None, running_config = {}, *args, **kwargs):
    
    existing_sso_profile_name = running_config.get("sso_profile_name")
    print(existing_sso_profile_name)
    response = self.get_common().generate_data().generate(
      generate_data_config = {
        "use_cli_profile": {
          "validation": lambda item: self.get_common().helper_type().bool().is_bool(check_value= item),
          "allow_empty": True,
          "messages":{
            "validation": f"Valid options for Yes are: {self.get_common().helper_type().bool().is_true_values()}\nValid options for No are: {self.get_common().helper_type().bool().is_false_values()}",
          },
          "conversion": lambda item: self.get_common().helper_type().bool().is_true(check_value= item),
          "desc": f"Use preconfigured aws cli sso profile (created with aws configure sso --profile <profile_name>)\nValid optiond for yes: {self.get_common().helper_type().bool().is_true_values()}{'' if self.get_common().helper_type().string().is_null_or_whitespace(string_value= existing_sso_profile_name) else '\n(If empty it will use the existing '+running_config.get('use_cli_profile')+')'}",
          "handler": generate_data_handlers.get_handler(handler= "base"),
          "default": running_config.get("use_cli_profile"),
          "optional": False
        },
        "sso_profile_name": {
          "validation": lambda item: self.__step_process_sso_valid_profile(profile_name= item, existing_profile= existing_sso_profile_name),
          "allow_empty": True,
          "skip": lambda item: item.get("use_cli_profile").get("formatted") if item is not None and item.get("use_cli_profile") is not None else False,
          "messages":{
            "validation": f"Could not find profile.",
          },
          "conversion": lambda item: self.get_common().helper_type().string().trim(string_value= item),
          "desc": f"Enter the SSO Profile Name{'' if self.get_common().helper_type().string().is_null_or_whitespace(string_value= existing_sso_profile_name) else ' (If empty it will use the existing profile '+existing_sso_profile_name+')'}",
          "handler": generate_data_handlers.get_handler(handler= "base"),
          "default": running_config.get("sso_profile_name"),
          "optional": False
        },
        "sso_start_url": {
          "validation": lambda item: item,
          "skip": lambda item: not item.get("use_cli_profile").get("formatted") if item is not None and item.get("use_cli_profile") is not None else True,
          "messages":{},
          "conversion": lambda item: self.get_common().helper_type().string().trim(item),
          "desc": f"Enter the SSO start url (ex: https://<aws_id>.awsapps.com/start",
          "handler": generate_data_handlers.get_handler(handler= "base"),
          "default": running_config.get("sso_start_url"),
          "optional": not self.get_common().helper_type().string().is_null_or_whitespace(string_value= running_config.get("sso_start_url"))
        },
        "sso_region": {
          "validation": lambda item: item,
          "skip": lambda item: not item.get("use_cli_profile").get("formatted") if item is not None and item.get("use_cli_profile") is not None else True,
          "messages":{},
          "conversion": lambda item: self.get_common().helper_type().string().trim(item),
          "desc": f"Enter the default region to use",
          "handler": generate_data_handlers.get_handler(handler= "base"),
          "default": running_config.get("sso_region") if not self.get_common().helper_type().string().is_null_or_whitespace(string_value= running_config.get("sso_region")) else "us-east-1",
          "optional": True
        },
        "sso_account_id": {
          "validation": lambda item: self.get_common().helper_type().regex().get(pattern= "^[0-9]{12,}$").fullmatch(str(item)) if item is not None else False,
          "skip": lambda item: not item.get("use_cli_profile").get("formatted") if item is not None and item.get("use_cli_profile") is not None else True,
          "messages":{
            "validation": f"It should be a 12 digit string (if its under 12 characters it should have leading zeros) ex. 000000000001",
          },
          "conversion": lambda item: item,
          "desc": f"Enter the organization account id (main account id)\n It should be 12 numeric characters.",
          "handler": generate_data_handlers.get_handler(handler= "base"),
          "default": running_config.get("sso_account_id"),
          "optional": not self.get_common().helper_type().string().is_null_or_whitespace(string_value= running_config.get("sso_account_id"))
        },
        "sso_role_name": {
          "validation": lambda item: item,
          "skip": lambda item: not item.get("use_cli_profile").get("formatted") if item is not None and item.get("use_cli_profile") is not None else True,
          "messages":{},
          "conversion": lambda item: self.get_common().helper_type().string().trim(item),
          "desc": f"Enter the role to use",
          "handler": generate_data_handlers.get_handler(handler= "base"),
          "default": running_config.get("sso_role_name"),
          "optional": not self.get_common().helper_type().string().is_null_or_whitespace(string_value= running_config.get("sso_role_name"))
        },
        "output": {
          "validation": lambda item: item,
          "skip": lambda item: not item.get("use_cli_profile").get("formatted") if item is not None and item.get("use_cli_profile") is not None else True,
          "messages":{},
          "conversion": lambda item: self.get_common().helper_type().string().trim(item),
          "desc": f"Enter a valid output format. For a full list goto:\nhttps://docs.aws.amazon.com/cli/latest/userguide/cli-usage-output-format.html",
          "handler": generate_data_handlers.get_handler(handler= "base"),
          "default": running_config.get("output") if not self.get_common().helper_type().string().is_null_or_whitespace(string_value= running_config.get("output")) else "json",
          "optional": True
        },        
        "default_profile": {
          "validation": lambda item: self.get_common().helper_type().bool().is_bool(check_value= item),
          "allow_empty": True,
          "messages":{
            "validation": f"Valid options for Yes are: {self.get_common().helper_type().bool().is_true_values()}\nValid options for No are: {self.get_common().helper_type().bool().is_false_values()}{'' if self.get_common().helper_type().string().is_null_or_whitespace(string_value= existing_sso_profile_name) else '\n(If empty it will use the existing '+running_config.get('use_cli_profile')+')'}",
          },
          "conversion": lambda item: self.get_common().helper_type().bool().is_true(check_value= item),
          "desc": f"Is this the default profile 3mystic apps should use when profile is not passed. You can only have one profile,\nValid optiond for yes: {self.get_common().helper_type().bool().is_true_values()}",
          "handler": generate_data_handlers.get_handler(handler= "base"),
          "default": self.get_default_default_profile(config = config, profile_name= profile_name, running_config= running_config),
          "optional": False
        }
      }
    )
    
    if response is None:
      return

    for key, item in response.items():
      running_config[key] = item.get("formated") if item is not None else ""
    
    if self.get_common().helper_type().string().is_null_or_whitespace(string_value=running_config.get("sso_profile_name")):
      running_config["sso_profile_name"] = existing_sso_profile_name
    
    self.update_config_profile(config= config, profile_name= profile_name, running_config= running_config)
    print(f"Profile ({profile_name} saved/updated)")

    
  
