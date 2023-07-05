from threemystic_cloud_client.cloud_providers.aws.config.base_class.base import cloud_client_aws_config_base as base
from threemystic_common.base_class.generate_data.generate_data_handlers import generate_data_handlers
import configparser

class cloud_client_aws_config_step_2(base):
  def __init__(self, *args, **kwargs):
    super().__init__(logger_name= "cloud_client_aws_config_step_2", *args, **kwargs)

  def step_done(self, *args, **kwargs):
    
    self.update_provider_config_completed(status= True)
    self._setup_another_config()


  def step(self, is_new_config, *args, **kwargs):

    if not super().step():
      return

    if is_new_config:
      self.__step_new()
      return
    
    self.__step_existing()

  def __step_new(self, *args, **kwargs):

    if not super().step():
      return
    
    profile_data = {}
    response = self.get_common().generate_data().generate(
      generate_data_config = self.get_common().helper_type().dictionary().merge_dictionary([
        {}, 
        self.__get_profile_data_genrationn(),
        {
          "auth_method": {
            "validation": lambda item: self.get_common().helper_type().string().set_case(string_value= item, case= "lower") in self.valid_auth_options(),
            "messages":{
              "validation": f"Valid Options: {self.valid_auth_options()}",
            },
            "conversion": lambda item: self.get_common().helper_type().string().trim(string_value= self.get_common().helper_type().string().trim(string_value= self.get_common().helper_type().string().set_case(string_value= item, case= "lower"))) if item is not None else None,
            "desc": f"Which provider authentication\nvalid options are {self.valid_auth_options()}",
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
      
    profile_data["auth_method"] = self.__get_response_item(key= "auth_method", response= response)   
    if self.get_common().helper_type().string().is_null_or_whitespace(string_value= profile_data["auth_method"]):
      print("Auth Method was empty.")
      return 

    if(self.config_profile_name_exists(profile_name= profile_name)):
      response_existing = self.get_common().generate_data().generate(
        generate_data_config = {
          "update_existing": {
            "validation": lambda item: self.get_common().helper_type().bool().is_bool(check_value= item),
            "allow_empty": True,
            "messages":{
              "validation": f"Valid options for Yes are: {self.get_common().helper_type().bool().is_true_values()}\nValid options for No are: {self.get_common().helper_type().bool().is_false_values()}",
            },
            "conversion": lambda item: self.get_common().helper_type().bool().is_true(check_value= item),
            "desc": f"Profile Name {profile_name} already exists.\nDo you want to update the existing profile?\nValid optiond for yes: {self.get_common().helper_type().bool().is_true_values()}{self.__get_existing_text(exiting_value= profile_data.get('default_profile'))}",
            "handler": generate_data_handlers.get_handler(handler= "base"),
            "default": False,
            "optional": True
          }
        }
      )
      if(self.__get_response_item(key= "update_existing", response= response_existing) == False):
        print("Please rerun config and use a different profile name")
        return

      profile_data = self.get_config_profile_name(profile_name= profile_name)
      profile_data["auth_method"] = self.__get_response_item(key= "auth_method", response= response) 
    
    self.__step_process_sso(
      profile_name= profile_name,
      profile_data= profile_data
    )
  
  def __step_existing(self, *args, **kwargs):
    if not self.has_config_profiles():
      print("No existing profiles please run new")
      return
    
    response = self.get_common().generate_data().generate(
      generate_data_config = self.__get_profile_data_genrationn()
    )
    
    profile_name = self.__get_response_item(key= "profile_name", response= response)

    if self.get_common().helper_type().string().is_null_or_whitespace(string_value= profile_name):      
      print(f"Profile Name was not valid: {profile_name}")
      return
    
    profile_data = self.get_config_profile_name(profile_name= profile_name)
    
    if profile_data is None:
      print("Profile not found")
      return

    if profile_data.get("auth_method") == "sso":
      self.__step_process_sso(
        profile_name= profile_name,
        profile_data= profile_data
      )

  def __get_profile_data_genrationn(self, *args, **kwargs):
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
    
  

 
  
  def __step_process_sso_valid_profile(self, profile_name, existing_profile, *args, **kwargs):

    if self.get_common().helper_type().string().is_null_or_whitespace(string_value= profile_name):
      return False if self.get_common().helper_type().string().is_null_or_whitespace(string_value= existing_profile) else True
      
    
    profile_name = self.get_common().helper_type().string().trim(string_value= profile_name)  
    config_parser = configparser.ConfigParser()
    if(self.get_common().helper_path().path_exists(path= self.get_aws_user_path_config())):
      with self.get_common().helper_path().expandpath_user(path= self.get_aws_user_path_config()).open(mode="r") as config_file:
        config_parser.read_file(config_file)
    else:
      print()
      print()
      print("*********************************************************")
      print(f"AWS config path not found: {self.get_aws_user_path_config()}")
      print("setup will not work until aws is configured")
      print("*********************************************************")
      print()
      print()
      
      return True
    return config_parser.has_section(f"profile {profile_name}")

  def get_default_profile_setting(self, profile_name, profile_data):
    if profile_data is not None:
      return profile_data.get("default_profile") == True
    
    if self.get_default_profile() is None:
      return True

    existing_profile = self.get_config_profile_name(profile_name= profile_name)
    if(existing_profile is not None):
      return existing_profile.get("default_profile") == True
    
    
    return False
    

  def __get_existing_text(self, exiting_value):
    return (f"\n(If empty it will use the existing: {exiting_value})"
      if not self.get_common().helper_type().string().is_null_or_whitespace(string_value=exiting_value) else ""
    )

  def __step_process_sso(self, profile_name = None, profile_data = {}, *args, **kwargs):
    if(profile_data is None):
      profile_data = {}

    existing_sso_profile_name = profile_data.get("sso_profile_name")
    
    response = self.get_common().generate_data().generate(
      generate_data_config = {
        "use_cli_profile": {
          "validation": lambda item: self.get_common().helper_type().bool().is_bool(check_value= item),
          "allow_empty": True,
          "messages":{
            "validation": f"Valid options for Yes are: {self.get_common().helper_type().bool().is_true_values()}\nValid options for No are: {self.get_common().helper_type().bool().is_false_values()}",
          },
          "conversion": lambda item: self.get_common().helper_type().bool().is_true(check_value= item),
          "desc": f"Use preconfigured aws cli sso profile (created with aws configure sso --profile <profile_name>)\nValid optiond for yes: {self.get_common().helper_type().bool().is_true_values()}{self.__get_existing_text(exiting_value= profile_data.get('use_cli_profile'))}",
          "handler": generate_data_handlers.get_handler(handler= "base"),
          "default": profile_data.get("use_cli_profile") == True,
          "optional": False
        },
        "sso_profile_name": {
          "validation": lambda item: self.__step_process_sso_valid_profile(profile_name= item, existing_profile= existing_sso_profile_name),
          "allow_empty": False,
          "skip": lambda item: item.get("use_cli_profile").get("formatted") if item is not None and item.get("use_cli_profile") is not None else False,
          "messages":{
            "validation": f"Could not find profile.",
          },
          "conversion": lambda item: self.get_common().helper_type().string().trim(string_value= item),
          "desc": f"Enter the SSO Profile Name{self.__get_existing_text(exiting_value= existing_sso_profile_name)}",
          "handler": generate_data_handlers.get_handler(handler= "base"),
          "default": profile_data.get("sso_profile_name"),
          "optional": not self.get_common().helper_type().string().is_null_or_whitespace(string_value= profile_data.get("sso_profile_name"))
        },
        "sso_start_url": {
          "validation": lambda item: item,
          "skip": lambda item: not item.get("use_cli_profile").get("formatted") if item is not None and item.get("use_cli_profile") is not None else True,
          "messages":{},
          "conversion": lambda item: self.get_common().helper_type().string().trim(item),
          "desc": f"Enter the SSO start url (ex: https://<aws_id>.awsapps.com/start",
          "handler": generate_data_handlers.get_handler(handler= "base"),
          "default": profile_data.get("sso_start_url"),
          "optional": not self.get_common().helper_type().string().is_null_or_whitespace(string_value= profile_data.get("sso_start_url"))
        },
        "sso_region": {
          "validation": lambda item: item,
          "skip": lambda item: not item.get("use_cli_profile").get("formatted") is not True if item is not None and item.get("use_cli_profile") is not None else True,
          "allow_empty": True,
          "messages":{},
          "conversion": lambda item: self.get_common().helper_type().string().trim(item),
          "desc": f"Enter the default region to use{self.__get_existing_text(exiting_value= profile_data.get('sso_region'))}",
          "handler": generate_data_handlers.get_handler(handler= "base"),
          "default": profile_data.get("sso_region") if not self.get_common().helper_type().string().is_null_or_whitespace(string_value= profile_data.get("sso_region")) else "us-east-1",
          "optional": False
        },
        "sso_account_id": {
          "validation": lambda item: self.get_common().helper_type().regex().get(pattern= "^[0-9]{12,}$").fullmatch(str(item)) if item is not None else False,
          "skip": lambda item: not item.get("use_cli_profile").get("formatted") if item is not None and item.get("use_cli_profile") is not None else True,
          "allow_empty": True,
          "messages":{
            "validation": f"It should be a 12 digit string (if its under 12 characters it should have leading zeros) ex. 000000000001",
          },
          "conversion": lambda item: item,
          "desc": f"Enter the organization account id (main account id)\n It should be 12 numeric characters.{self.__get_existing_text(exiting_value= profile_data.get('sso_account_id'))}",
          "handler": generate_data_handlers.get_handler(handler= "base"),
          "default": profile_data.get("sso_account_id"),
          "optional": False
        },
        "sso_role_name": {
          "validation": lambda item: item,
          "skip": lambda item: not item.get("use_cli_profile").get("formatted") if item is not None and item.get("use_cli_profile") is not None else True,
          "allow_empty": True,
          "messages":{},
          "conversion": lambda item: self.get_common().helper_type().string().trim(item),
          "desc": f"Enter the role to use{self.__get_existing_text(exiting_value= profile_data.get('sso_account_id'))}",
          "handler": generate_data_handlers.get_handler(handler= "base"),
          "default": profile_data.get("sso_role_name"),
          "optional": False
        },
        "output": {
          "validation": lambda item: item,
          "skip": lambda item: not item.get("use_cli_profile").get("formatted") if item is not None and item.get("use_cli_profile") is not None else True,
          "allow_empty": True,
          "messages":{},
          "conversion": lambda item: self.get_common().helper_type().string().trim(item),
          "desc": f"Enter a valid output format. For a full list goto:\nhttps://docs.aws.amazon.com/cli/latest/userguide/cli-usage-output-format.html{self.__get_existing_text(exiting_value= profile_data.get('output'))}",
          "handler": generate_data_handlers.get_handler(handler= "base"),
          "default": profile_data.get("output") if not self.get_common().helper_type().string().is_null_or_whitespace(string_value= profile_data.get("output")) else "json",
          "optional": False
        },        
        "default_profile": {
          "validation": lambda item: self.get_common().helper_type().bool().is_bool(check_value= item),
          "allow_empty": True,
          "messages":{
            "validation": f"Valid options for Yes are: {self.get_common().helper_type().bool().is_true_values()}\nValid options for No are: {self.get_common().helper_type().bool().is_false_values()}",
          },
          "conversion": lambda item: self.get_common().helper_type().bool().is_true(check_value= item),
          "desc": f"Is this the default profile 3mystic apps should use when profile is not passed. You can only have one profile,\nValid optiond for yes: {self.get_common().helper_type().bool().is_true_values()}{self.__get_existing_text(exiting_value= profile_data.get('default_profile'))}",
          "handler": generate_data_handlers.get_handler(handler= "base"),
          "default": self.get_default_profile_setting(profile_name= profile_name, profile_data= profile_data),
          "optional": False
        }
      }
    )
    
    if response is None:
      return

    for key, item in response.items():
      profile_data[key] = item.get("formated") if item is not None else ""
    
    if self.get_common().helper_type().string().is_null_or_whitespace(string_value=profile_data.get("sso_profile_name")):
      profile_data["sso_profile_name"] = existing_sso_profile_name
    
    self.update_config_profile(profile_name= profile_name, profile_data= profile_data)
    print(f"Profile ({profile_name} saved/updated)")
    self.step_done()
    

    
  
