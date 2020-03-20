# main script to connect to workspace
# Author: Nishanth Koganti
# Date: 2020/3/15

# relative imports
from utils import set_env_vars, get_svc_pr, get_ws


def init_ws():
    # set config path
    config_path = '../.aml_config/config.json'

    # set env variables
    status = set_env_vars(config_path)

    # check for error
    if not status:
        print('Setting env variables failed')
        return None
    else:
        print('\nEnvironment variables set')

    # perform service principal auth
    svc_pr = get_svc_pr()

    # check for error with service principal auth
    if not svc_pr:
        print('Service principal auth failed')
        return None
    else:
        print('\nAuthentication succeded')
    # connect to ws
    ws = get_ws(svc_pr)

    # check for error with connection to ws
    if not ws:
        print('Workspace connection failed')
        return None
    else:
        print(f'\nFound workspace {ws.name} at location {ws.location}')
        return ws


def main():
    _ = init_ws()


if __name__ == '__main__':
    main()
