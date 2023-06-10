from threemystic_cloud_client.cloud_providers.aws.client.base_class.base import cloud_client_aws_client_base as base
import sys
import os
import boto3
from polling2 import TimeoutException, poll
    
class cloud_client_aws_client_sso(base):
  def __init__(self, *args, **kwargs):
    super().__init__(logger_name= "cloud_client_aws_client_sso", *args, **kwargs)

    if(self.get_common().helper_type().string().set_case(string_value= self.get_profile()["profile_data"]["auth_method"], case= "lower") != "sso"):
      raise self.get_common().exception().exception(
          exception_type = "generic"
        ).type_error(
          logger = self.get_common().get_logger(),
          name = "Profile Authentication Invalid",
          message = f"Profile Authentication Invalid - Cloud Client Profile: {self.get_profile()['profile_name']}"
        )
    
    if(self.get_profile()['profile_data']['use_cli_profile'] and not self._has_aws_sso_config_profile()):
      raise self.get_common().exception().exception(
        exception_type = "generic"
      ).type_error(
        logger = self.get_common().get_logger(),
        name = f"AWSCLI SSO Profile NOT FOUND",
        message = f"AWSCLI SSO Profile NOT FOUND - Cloud Client Profile: {self.get_profile()['profile_name']}\nPlease run the following command to configure aws cli:\naws configure sso --profile {self.get_profile()['profile_data']['sso_profile_name']}"
      )
  
  def __get_aws_cli_config(self, refresh= False, *args, **kwargs):
    if(hasattr(self, "_aws_config") and (not refresh)):
      return self._aws_config
    
    self._aws_config = self.get_common().helper_config().load(
      config_type = "config",
      path= self.get_aws_user_path_config()
    )
    return self.__get_aws_cli_config(*args, **kwargs)
  
  def __unset_aws_cli_config(self, *args, **kwargs):
    if(hasattr(self, "_aws_config")):
      delattr(self, "_aws_config")
  
  
  def _has_aws_sso_config_profile(self, refresh = False, *args, **kwargs):

    if not self.get_common().helper_type().string().is_null_or_whitespace(string_value= self.get_profile()['profile_data']['sso_profile_name']) and self.__get_aws_cli_config(refresh= refresh).has_section(f"profile {self.get_profile()['profile_data']['sso_profile_name']}"):
      return True
    
    return False
  
  def _get_aws_sso_config_profile(self, refresh = False, *args, **kwargs):
    
    if(hasattr(self, "_aws_config_profile") and (not refresh)):
      return self._aws_config_profile
    
    if(not self._has_aws_sso_config_profile(refresh= refresh)):
      raise self.get_common().exception().exception(
        exception_type = "generic"
      ).type_error(
        logger = self.get_common().get_logger(),
        name = f"NOT FOUND",
        message = f"AWS SSO PRofile NOT FOUND"
      )
    
    self._aws_config_profile = self.__get_aws_cli_config()[f"profile {self.get_profile()['profile_data']['sso_profile_name']}"]
    self.__unset_aws_cli_config()
    return self._get_aws_sso_config_profile(*args, **kwargs)
  
  def _get_sso_profile_credentials(self, refresh = False, *args, **kwargs):   
    if(hasattr(self, "_aws_config_profile_credentials") and (not refresh)):
      return self._aws_config_profile_credentials
    
    cache_key = f'{self.get_common().encryption().hash(hash_method="sha1").generate_hash(data= self._get_aws_sso_config_profile(refresh= refresh)["sso_start_url"])}.json'    
    
    ssoTokenFile = self.get_aws_user_path().joinpath('sso', 'cache', cache_key)
    
    if not self.get_common().helper_path().is_file(ssoTokenFile):
      raise self.get_common().exception().exception(
        exception_type = "generic"
      ).type_error(
        logger = self.get_common().get_logger(),
        name = f"NOT FOUND",
        message = f"Token File not found or not valid file: {ssoTokenFile}"
      )
      
    with ssoTokenFile.open(mode="r") as sso_cache:
      self._aws_config_profile_credentials = self.get_common().helper_json().loads(data= sso_cache.read())

  def __internal_load_base_configs_ssoprofile(self, *args, **kwargs):
    self._get_sso_profile_credentials()

  def _get_session_accesstoken(self, refresh = False, *args, **kwargs):
    if self.session_expired():
      self.ensure_session()

    if(hasattr(self, "_aws_config_profile_credentials_accesstoken") and (not refresh)):
      if(not self.get_common().helper_type().string().is_null_or_whitespace(string_value= self._aws_config_profile_credentials_accesstoken) ):
        return self._aws_config_profile_credentials_accesstoken
    
    self._aws_config_profile_credentials_accesstoken = self._get_sso_profile_credentials()["accessToken"]
    return self._get_session_accesstoken()
  
  def _get_session_expires(self, refresh = False, *args, **kwargs):
    if(hasattr(self, "_aws_config_profile_credentials_expires") and (not refresh)):
      return self._aws_config_profile_credentials_expires

    if(self.get_common().helper_type().string().is_null_or_whitespace(string_value= self._get_sso_profile_credentials()['expiresAt']) ):
      return self.get_common().helper_type().datetime().timedelta(totalSecondAddTime= -300, time_zone="utc")
    
    self._aws_config_profile_credentials_expires = self.get_common().helper_type().datetime().convert_utc(
      dt= self.get_common().helper_type().datetime().parse_iso(iso_datetime_str= self._get_sso_profile_credentials()['expiresAt'])
    )
    return self._get_session_expires()
    
  def _session_expired(self, refresh = False, *args, **kwargs):
    
    if(self.get_common().helper_type().string().is_null_or_whitespace(string_value= self._get_sso_profile_credentials(refresh= refresh)['expiresAt']) ):
      return True

    return self.get_common().helper_type().datetime().is_token_expired_now(compare_datetime= self._get_session_expires())
    
    
  def authenticate_session(self, *args, **kwargs):
    if(self.get_profile()['profile_data']['use_cli_profile']):
      self.__aws_sso_login_profile()
      return
    
    raise self.get_common().exception().exception(
      exception_type = "generic"
    ).type_error(
      logger = self.get_common().get_logger(),
      name = f"NOT SUPPORTED",
      message = f"Cloud Client Profile not loaded"
    )

  def __aws_sso_login_profile(self, *args, **kwargs):
    if(not self._has_aws_sso_config_profile()):
      raise self.get_common().exception().exception(
        exception_type = "generic"
      ).type_error(
        logger = self.get_common().get_logger(),
        name = f"NOT FOUND",
        message = f"Cloud Client Profile not found - Login"
      )
    
    ssologin_call = f"aws sso login --profile {self.get_profile()['profile_data']['sso_profile_name']}"
    if os.system(ssologin_call) != 0:
      raise self.get_common().exception().exception(
        exception_type = "generic"
      ).type_error(
        logger = self.get_common().get_logger(),
        name = f"NOT AUTHENTICATED",
        message = f"Cloud Client Profile could not authenticate SSO PRofile"
      )

    try:
      logged_in = poll(
        lambda: not self.session_expired(refresh = True),
        ignore_exceptions=(Exception,),
        timeout=self.get_aws_poll_login(),
        step=0.1
      )
      if logged_in is not None:      
        return logged_in
      
      raise self.get_common().exception().exception(
          exception_type = "generic"
        ).type_error(
          logger = self.get_common().get_logger(),
          name = f"NOT SUPPORTED",
          message = f"Could not authenticate SSO.\nPlease check cli version aws --version and make sure you are using v2 then please run aws sso login --profile {self.get_profile()['profile_data']['sso_profile_name']}"
        )
    except Exception as err:
      raise self.get_common().exception().exception(
          exception_type = "generic"
        ).type_error(
          logger = self.get_common().get_logger(),
          name = f"NOT SUPPORTED",
          message = f"Could not authenticate SSO.\nPlease check cli version aws --version and make sure you are using v2 then please run aws sso login --profile {self.get_profile()['profile_data']['sso_profile_name']}"
        )


  def _load_base_configs(self, *args, **kwargs):
    if(self.get_profile()['profile_data']['use_cli_profile']):
      self.__internal_load_base_configs_ssoprofile()
      return
    
    raise self.get_common().exception().exception(
      exception_type = "generic"
    ).type_error(
      logger = self.get_common().get_logger(),
      name = f"NOT SUPPORTED",
      message = f"Cloud Client Profile not loaded"
    )

  def get_default_rolename(self, *args, **kwargs):
    if(self.get_profile()['profile_data']['use_cli_profile']):
      return self._get_aws_sso_config_profile()["sso_role_name"]
    
    raise self.get_common().exception().exception(
      exception_type = "generic"
    ).type_error(
      logger = self.get_common().get_logger(),
      name = f"NOT SUPPORTED",
      message = f"Unknown default role"
    )

  def get_default_region(self, *args, **kwargs):
    if(self.get_profile()['profile_data']['use_cli_profile']):
      if not self.get_common().helper_type().string().is_null_or_whitespace(string_value= self._get_aws_sso_config_profile()["region"]):
        return self._get_aws_sso_config_profile()["region"]
      
      if not self.get_common().helper_type().string().is_null_or_whitespace(string_value= self._get_aws_sso_config_profile()["sso_region"]):
        return self._get_aws_sso_config_profile()["sso_region"]
    
    raise self.get_common().exception().exception(
      exception_type = "generic"
    ).type_error(
      logger = self.get_common().get_logger(),
      name = f"NOT SUPPORTED",
      message = f"Unknown default region"
    )
            
  def get_default_account(self):
    return self.make_account(Id = self._get_aws_sso_config_profile()["sso_account_id"])
  
  def __get_sso_boto_session(self):
    return boto3.Session(
      profile_name = self.get_profile()['profile_data']['sso_profile_name']
    )
  
  def _assume_role(self, account = None, region = None, role = None, force_refresh= False, *args, **kwargs):
        
    if self.get_common().helper_type().string().is_null_or_whitespace(string_value= role):
      role = self.get_default_rolename()
    
    if self.get_common().helper_type().string().is_null_or_whitespace(string_value= region):
        region = self.get_default_region()

    if account is None or (self.get_common().helper_type().general().is_type(obj= account, type_check= str) and self.get_common().helper_type().string().is_null_or_whitespace(string_value= account)):
        account = self.get_default_account()
    
    if not force_refresh and self._get_assumed_role_credentials().get(self._get_assumed_role_credentials_key(account= account, role= role)) is not None:
        experation = self._get_assumed_role_credentials()[self._get_assumed_role_credentials_key(account= account, role= role)]["Credentials"]["Expiration"]
        if self.get_common().helper_type().general().is_type(obj= experation, type_check= str):
            experation = self.get_common().helper_type().datetime().parse_iso(iso_datetime_str=experation)

            if not self.get_common().helper_type().datetime().is_token_expired_now(compare_datetime= experation):
                return self._get_assumed_role_credentials()[self._get_assumed_role_credentials_key(account= account, role= role)]["Credentials"]
    
    self._get_assumed_role_credentials()[self._get_assumed_role_credentials_key(account= account, role= role)] = self.__get_sso_boto_session().client('sso').get_role_credentials(
      roleName=role,
      accountId=self.get_account_id(account= account),
      accessToken=self._get_session_accesstoken()
    )
                
  
  def get_main_account_id(self, *args, **kwargs):
    return self.get_account_id(account= self.get_default_account())

  def get_organization_account_id(self, *args, **kwargs):
    return self.get_account_id(account= self.get_default_account())
