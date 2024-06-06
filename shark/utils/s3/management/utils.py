import json


def get_public_resource_policy(path=None):
    resource_path = f"{path}/*" if path else "*"
    return json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "PublicReadGetObject",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": ["s3:GetObject"],
                    "Resource": [f"arn:aws:s3:::{resource_path}"],
                }
            ],
        }
    )
