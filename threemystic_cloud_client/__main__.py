import sys


def main(*args, **kwargs):
  from threemystic_cloud_client.cli import cloud_client_cli
  cloud_client_cli().main(*args, **kwargs)
  

if __name__ == '__main__':   
  main(sys.argv[1:])