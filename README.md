# 3mystic_cloud_client
A tool to help uniform the connection to the cloud providers.
Currently supports AWS/Azure

This project is currently in beta, along with the other projects. Once the other projects come out of beta this one will as well. However, this is also, the most stable of the project. I am trying not to change things that would break from version to version. So if you would like to use something here, it should be relatively safe. I will try to call out breaking changes. The connection for both AWS and Azure does currently work. So if you have issues please create an issue.



# Install

## pip

The latest version of this project is currently being pushed to
https://pypi.org/project/threemystic-cloud-client/

pip install threemystic-cloud-client

If you would prefer to install directly from GitHub you need to install Hatch.
Please refer to the section below for that.

Once hatch is installed you can use pip

pip install https://github.com/3MysticApes/3mystic_cloud_client

## Hatch
This project is packaged using Hatch. If you need to install Hatch please refer to their documentation
https://hatch.pypa.io/latest/install/

# Setup

Once installed please run 
3mystic_cloud_client -c

# Usage

## Base 3mystic_cloud_client
usage: 3mystic_cloud_client [--version] [--config] [--test] [--token] [--generate]
 [--provider {aws,azure}]

One Action is required

options:</br>
  -v, --verbose         Verbose output</br>
  --help, -h            Display Help</br>
  --version             Action: outputs the versions of the app being used.</br>
  --config, -c          Action: This is so you can setup the cloud client to work with various providers</br>
  --test, -t            Action: This is so you can test the config setup to ensure the base connection is good</br>
  --token               Action: This is so that you can generate the required token.</br>
  --generate, -g        Action: For providers like aws it is easier to have a profile when interacting with the accounts. This will help generate the various profiles.</br>
  --provider {aws,azure}, -p {aws,azure} Provider: This is to set the provider that should be used</br>

## Base 3mystic_cloud_client - AWS Token


usage: 3mystic_cloud_client --token -p aws [--account TOKEN_ACCOUNT] [--profile TOKEN_PROFILE] [--format {cli,raw,export}]

Requires additional settings.</br>
  --account is required"</br>

options:</br>
  -v, --verbose         Verbose output</br>
  --help, -h            Display Help</br>
  --account TOKEN_ACCOUNT - The AWS Account ID to generate access token information for</br>
  --profile TOKEN_PROFILE - The 3Mystic AWS Profile to use. If not provided the default will be used</br>
  --format TOKEN_FORMAT - The format the token will be returned in the options are export, cli, raw. The default is cli</br>

This command generates a token in various formats. This can be used for aws cli profiles to auto generate credentials.

## Base 3mystic_cloud_client - AWS Generate

usage: 3mystic_cloud_client --generate -p aws 

This will auto generate aws cli config profiles.

## Base 3mystic_cloud_client - AWS Test

usage: 3mystic_cloud_client --test -p aws 

This will help test the config to make sure its communicating with the settings

## Base 3mystic_cloud_client - AWS Config

usage: 3mystic_cloud_client --config -p aws 

This is used to setup the configuration for the provider

## Base 3mystic_cloud_client - Azure Token


usage: 3mystic_cloud_client --token -p azure [-v] [--resource TOKEN_RESOURCE] [--tenant TOKEN_TENANT]

Requires additional settings.
  --tenant is required
  --resource is required

  To learn more please see: https://learn.microsoft.com/en-us/cli/azure/account?view=azure-cli-latest#az-account-get-access-token

options:
  -v, --verbose         Verbose output
  --resource TOKEN_RESOURCE - Azure resource endpoints in AAD v1.0.
  --tenant TOKEN_TENANT - Tenant ID for which the token is acquired.


This command will generate tokens you can use for various things like ms-graph

## Base 3mystic_cloud_client - Azure Generate

usage: 3mystic_cloud_client --generate -p azure 

This currently doesn't do anything, as its not needed in Azure with the current setup.

## Base 3mystic_cloud_client - AWS Test

usage: 3mystic_cloud_client --test -p azure 

This will help test the config to make sure its communicating with the settings

## Base 3mystic_cloud_client - AWS Config

usage: 3mystic_cloud_client --config -p azure 

This is used to setup the configuration for the provider


# Contribute
You need to install Hatch. Please see the previous Hatch section under install.

Once you download the project you can do the following
You should be able to run the following command in the root directory for a general status
hatch status

Then from the root directory you can run
pip install ./

I would suggest while you are debugging issues to install it with the command below. Once you are done with your development you can uninstall. This allows you to make edits and test easier.
pip install -e ./
https://pip.pypa.io/en/stable/cli/pip_install/#cmdoption-e

