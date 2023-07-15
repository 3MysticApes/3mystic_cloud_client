# 3mystic_cloud_client
A tool to help uniform the connection to the cloud providers.
Currently supports AWS/Azure



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


# Usage

## Base 3mystic_cloud_client
usage: 3mystic_cloud_client [-v] [--help] [--version] [--config] [--test] [--token] [--generate]
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

usage: 3mystic_cloud_client --token -p aws [-v] [--help] [--account TOKEN_ACCOUNT] [--profile TOKEN_PROFILE] [--format TOKEN_FORMAT]

Requires additional settings.</br>
  --account is required"</br>

options:</br>
  -v, --verbose         Verbose output</br>
  --help, -h            Display Help</br>
  --account TOKEN_ACCOUNT - The AWS Account ID to generate access token information for</br>
  --profile TOKEN_PROFILE - The 3Mystic AWS Profile to use. If not provided the default will be used</br>
  --format TOKEN_FORMAT - The format the token will be returned in the options are export, cli, raw. The default is cli</br>

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

