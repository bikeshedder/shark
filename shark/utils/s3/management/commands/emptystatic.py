import time
from concurrent.futures import ThreadPoolExecutor

from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.management.base import BaseCommand
from supercollect.utils import get_all_files


class Command(BaseCommand):
    def handle(self, *args, **options):
        start = time.time()
        print("Starting to empty static bucket...")
        with ThreadPoolExecutor(max_workers=32) as executor:
            for file in get_all_files(staticfiles_storage):
                executor.submit(staticfiles_storage.delete, file)

        print("Finished in", time.time() - start)
