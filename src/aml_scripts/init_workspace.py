# main script to connect to workspace
# Author: Nishanth Koganti
# Date: 2020/3/15

# import modules
import argparse

# relative imports
from utils import set_env_vars, get_svc_pr, get_ws


def main():
    # argument parsing
    parser = argparse.ArgumentParser(description='Script to connect to workspace')
    parser.add_argument('--config', type=str, default='.aml_config/config.json',
                        help='config path for variables')
    parser.add_argument('--env', type=str, default='local',
                        help='env argument to get variables')
    args = parser.parse_args()

    # set config path
    env = args.env
    config_path = args.config

    # set env variables
    if env == 'local':
        status = set_env_vars(config_path)

        # check for error
        if not status:
            print('Setting env variables failed')
            return -1
        else:
            print('\nEnvironment variables set')

    # perform service principal auth
    svc_pr = get_svc_pr()

    # check for error with service principal auth
    if not svc_pr:
        print('Service principal auth failed')
        return -1
    else:
        print('\nAuthentication succeded')
    # connect to ws
    ws = get_ws(svc_pr)

    # check for error with connection to ws
    if not ws:
        print('Workspace connection failed')
        return -1
    else:
        print(f'\nFound workspace {ws.name} at location {ws.location}')

    return 0


if __name__ == '__main__':
    main()
