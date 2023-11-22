import os
import boto3

def get_s3_client():
    # Retrieve AWS credentials from environment variables
    aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    aws_region = os.getenv('AWS_REGION')

    # Check if all necessary environment variables are set
    if not all([aws_access_key_id, aws_secret_access_key, aws_region]):
        raise EnvironmentError("Missing AWS credentials or region in environment variables")

    # Create an S3 client
    s3_client = boto3.client(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=aws_region
    )
    print('aquired s3 client', s3_client)

    return s3_client