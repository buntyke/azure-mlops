# aml_train.py: AML training script for sklearn
# Author: Nishanth Koganti
# Date: 2019/09/28

# import modules
import os
import argparse
import numpy as np

# aml imports
from azureml.core import Experiment
from azureml.core.dataset import Dataset
from azureml.train.sklearn import SKLearn
from azureml.core.environment import Environment
from azureml.core.conda_dependencies import CondaDependencies

# relative imports
from utils import set_env_vars, get_svc_pr, get_ws, get_compute_target


def main():
    # argument parsing
    parser = argparse.ArgumentParser(description='Script to connect to workspace')
    parser.add_argument('--experiment', type=str, default='classification',
                        help='experiment name for workspace')
    parser.add_argument('--config', type=str, default='.aml_config/config.json',
                        help='config path for variables')
    parser.add_argument('--compute_name', type=str, default='train-classify',)
    parser.add_argument('--compute_nodes', type=int, default=4,
                        help='number of nodes in compute cluster')
    parser.add_argument('--compute_type', type=str, default='STANDARD_D2_V2',
                        help='type of compute in cluster')
    parser.add_argument('--compute_priority', type=str, default='dedicated',
                        help='compute priority in compute cluster')
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

    # create classification experiment
    exp = Experiment(workspace=ws, name=args.experiment)

    # create compute target
    compute_target = get_compute_target(ws, args.compute_name, args.compute_type,
                                        args.compute_nodes, args.compute_priority)

    # register dataset to be used in compute
    web_paths = ['http://yann.lecun.com/exdb/mnist/train-images-idx3-ubyte.gz',
                 'http://yann.lecun.com/exdb/mnist/train-labels-idx1-ubyte.gz',
                 'http://yann.lecun.com/exdb/mnist/t10k-images-idx3-ubyte.gz',
                 'http://yann.lecun.com/exdb/mnist/t10k-labels-idx1-ubyte.gz']
    dataset = Dataset.File.from_files(path=web_paths)

    dataset = dataset.register(workspace=ws,
                               name='classification dataset',
                               description='training and test dataset',
                               create_new_version=True)

    # create directory for training scripts
    train_folder = os.path.join('..', 'classification', 'training')

    # create environment for classification
    env = Environment('classification_env')
    cd = CondaDependencies.create(pip_packages=['azureml-sdk', 'scikit-learn',
                                                'azureml-dataprep[pandas,fuse]>=1.1.14'])
    env.python.conda_dependencies = cd
    env.docker.enabled = True

    # setup hyper parameter values to tune
    regularizations = np.linspace(0.05, 0.95, 10)

    # loop over the parameter values
    for reg in regularizations:
        # create sklearn estimator
        train_params = {
            '--data-folder': dataset.as_named_input('data').as_mount(),
            '--regularization': reg
        }

        est = SKLearn(
            source_directory=train_folder, script_params=train_params,
            compute_target=compute_target, environment_definition=env,
            entry_script='train.py')

        # submit run for execution
        _ = exp.submit(config=est)


if __name__ == '__main__':
    main()
