import os
from app.environment import load_environment
mode = os.getenv('MODE','staging')
load_environment(mode)

import boto3

s3 = boto3.client('s3')
