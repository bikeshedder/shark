# This code is inspired by StackOverflow Question "Django uploads: Discard
# uploaded duplicates, use existing file (md5 based check)":
# http://stackoverflow.com/questions/15885201


class DocumentStorage(FileSystemStorage)

    def get_available_name(self, name):
        '''
        All names are available since we make sure that the content is
        hashed and used as filename. Thus an identical filename means
        that the file is duplicate. In this case the _save function does
        nothing.
        '''
        return name

    def _save(self, name, content):
        '''
        Only write the file if does not already exists.
        '''
        if self.exists(name):
            return name
        return super(HashedFileSystemStorage, self)._save(name, content)
