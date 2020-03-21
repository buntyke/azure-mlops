# util functions to perform workspace connection
# Author: Nishanth Koganti
# Date: 2020/3/15

# import modules
import os
import json
from azureml.core.compute import AmlCompute
from azureml.core.workspace import Workspace
from azureml.core.compute import ComputeTarget
from azureml.core.authentication import ServicePrincipalAuthentication


def set_env_vars(config_path):
    # read config json file
    try:
        with open(config_path, 'r') as f:
            config_dict = json.load(f)
    except Exception as e:
        print('Error reading config json')
        print('Exception: ', e)
        return False

    # set authentication variables
    try:
        os.environ['TENANT_ID'] = config_dict['auth']['tenant_id']
        os.environ['CLIENT_ID'] = config_dict['auth']['client_id']
        os.environ['CLIENT_SECRET'] = config_dict['auth']['client_secret']
    except Exception as e:
        print('Error setting auth variables')
        print('Exception: ', e)
        return False

    # set workspace variables
    try:
        os.environ['SUBSCRIPTION_ID'] = config_dict['workspace']['subscription_id']
        os.environ['RESOURCE_GROUP'] = config_dict['workspace']['resource_group']
        os.environ['WORKSPACE'] = config_dict['workspace']['workspace']
    except Exception as e:
        print('Error setting workspace variables')
        print('Excpetion: ', e)
        return False

    # success return
    return True


def get_svc_pr():
    # obtain auth env variables
    try:
        tenant_id = os.environ.get('TENANT_ID')
        client_id = os.environ.get('CLIENT_ID')
        client_secret = os.environ.get('CLIENT_SECRET')
    except Exception as e:
        print('Error fetching auth variables')
        print('Exception: ', e)
        return None

    # perform svc connection
    try:
        svc_pr = ServicePrincipalAuthentication(
            tenant_id=tenant_id,
            service_principal_id=client_id,
            service_principal_password=client_secret)
    except Exception as e:
        print('Error with service principal auth')
        print('Excpetion: ', e)
        return None
    else:
        return svc_pr


def get_ws(svc_pr):
    # obtain ws env variables
    try:
        workspace = os.environ.get('WORKSPACE')
        resource_group = os.environ.get('RESOURCE_GROUP')
        subscription_id = os.environ.get('SUBSCRIPTION_ID')
    except Exception as e:
        print('Error fetching ws variables')
        print('Exception: ', e)
        return None

    # connect to workspace
    try:
        ws = Workspace(
            subscription_id=subscription_id,
            resource_group=resource_group,
            workspace_name=workspace,
            auth=svc_pr)
    except Exception as e:
        print('Error connecting to ws')
        print('Exception: ', e)
        return None
    else:
        return ws


def get_compute_target(ws, compute_name, compute_type, compute_nodes, compute_priority):
    # choose a name for your cluster and node limits
    compute_min_nodes = 0
    compute_name = compute_name
    compute_max_nodes = compute_nodes
    compute_priority = compute_priority

    # setup cpu based vm for computation
    vm_size = compute_type

    if compute_name in ws.compute_targets:
        compute_target = ws.compute_targets[compute_name]
        if compute_target and type(compute_target) is AmlCompute:
            print('Found compute target. Using: ' + compute_name)
    else:
        print('Create compute target. Using: ' + compute_name)

        # setup provisioning configuration
        provisioning_config = AmlCompute.provisioning_configuration(vm_size=vm_size,
                                                                    min_nodes=compute_min_nodes,
                                                                    max_nodes=compute_max_nodes,
                                                                    vm_priority=compute_priority)

        # create the cluster
        compute_target = ComputeTarget.create(
            ws, compute_name, provisioning_config)

        # can poll for a minimum number of nodes and for a specific timeout.
        compute_target.wait_for_completion(
            show_output=True, min_node_count=None, timeout_in_minutes=20)

        # for a more detailed view of current AmlCompute status, use get_status()
        print(compute_target.get_status().serialize())

    return compute_target
