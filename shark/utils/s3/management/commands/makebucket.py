from botocore.client import ClientError
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.management.base import BaseCommand

from ..utils import get_public_resource_policy


class Command(BaseCommand):
    def handle(self, *args, **options):
        bucket = staticfiles_storage.bucket
        try:
            bucket.meta.client.head_bucket(Bucket=bucket.name)
        except ClientError:
            try:
                bucket.create()
            except ClientError:
                print(
                    (
                        f"Error creating S3 bucket {bucket.name}. "
                        "Likely insufficient rights. Either grant necessary rights "
                        "or create Bucket manually."
                    )
                )
                exit()

        public_resource_path = (
            bucket.name
            if not staticfiles_storage.location
            else f"{bucket.name}/{staticfiles_storage.location}"
        )

        bucket.Policy().put(Policy=get_public_resource_policy(public_resource_path))
