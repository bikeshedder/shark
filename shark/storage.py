from urllib.parse import urlencode

from django.contrib.staticfiles.storage import ManifestFilesMixin
from django.utils.encoding import filepath_to_uri
from storages.backends.s3 import S3Storage as BaseS3Storage
from storages.utils import (
    clean_name,
    setting,
)


class S3Storage(BaseS3Storage):
    def url(self, name, parameters=None, expire=None, http_method=None):
        if not self.public_url:
            return super().url(name, parameters, expire, http_method)
        name = self._normalize_name(clean_name(name))
        params = parameters.copy() if parameters else {}
        url = "{}/{}/{}{}".format(
            self.public_url.rstrip("/"),
            self.bucket_name,
            filepath_to_uri(name),
            f"?{urlencode(params)}" if params else "",
        )
        return url

    def get_default_settings(self):
        return {
            **super().get_default_settings(),
            "public_url": setting("S3_PUBLIC_URL"),
        }


class S3ManifestStaticStorage(ManifestFilesMixin, S3Storage):
    pass
