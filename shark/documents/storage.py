from storages.backends.s3 import S3Storage


class DocumentStorage(S3Storage):
    location = "documents"
