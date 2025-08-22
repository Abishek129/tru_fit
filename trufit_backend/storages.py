from storages.backends.s3boto3 import S3StaticStorage, S3Boto3Storage

class StaticRootS3Boto3Storage(S3StaticStorage):
    location = "static"

class MediaRootS3Boto3Storage(S3Boto3Storage):
    location = "media"
    file_overwrite = False
