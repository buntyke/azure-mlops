# main script to submit sample run
# Author: Nishanth Koganti
# Date: 2020/3/15

# relative imports
from init_workspace import init_ws


def submit_run():
    # initialize workspace
    ws = init_ws()

    if not ws:
        print('Workspace initialization failed')
        return None


def main():
    _ = submit_run()


if __name__ == '__main__':
    main()
