import os
from dotenv import load_dotenv

def load_environment(mode):
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    # Read the value of MODE set at server start
    
    print("LOADING ", mode, " ENV")
 

    # Determine which .env file to load based on MODE
    
    env_file = os.path.join(script_dir, 'envs', 'staging.env')


    print("Loading environment file from:", env_file)

    # Capture the current environment
    before_env = set(os.environ.keys())

    # Load the .env file
    load_dotenv(env_file)

    # Capture the environment after loading the .env file
    after_env = set(os.environ.keys())

    # Determine which keys were added
    new_keys = after_env - before_env

    # Print the new keys
    print("Newly loaded environment variables:")
    for key in new_keys:
        print(key)
