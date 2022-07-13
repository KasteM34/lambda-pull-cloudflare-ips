import boto3
import json
import urllib3
import os

def lambda_handler(event, context):
    # CloudFlare connection
    http = urllib3.PoolManager()
    r = http.request('GET', 'https://api.cloudflare.com/client/v4/ips')
    json_content = json.loads(r.data)
    ipv4 = json_content["result"]["ipv4_cidrs"]
    ipv6 = json_content["result"]["ipv6_cidrs"]
    ip_list = ipv4 + ipv6
    # S3 connection
    s3 = boto3.client('s3')
    bucket_name = os.environ['BUCKET_NAME']
    bucket_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "PublicReadForGetBucketObjects",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{bucket_name}/*",
                "Condition": {
                    "IpAddress": {
                        "aws:SourceIp": ip_list
                    }
                }
            }
        ]
    }
    bucket_policy = json.dumps(bucket_policy)
    s3.put_bucket_policy(Bucket=bucket_name, Policy=bucket_policy)
