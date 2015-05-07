import collections
from django.contrib.staticfiles.finders import FileSystemFinder
from django.core.files.storage import FileSystemStorage
from . import conf
import os

class BowerFileSystemStorage(FileSystemStorage):
    def __init__(self, location=None, base_url=None, file_permissions_mode=None, directory_permissions_mode=None):
        print location, base_url, file_permissions_mode, directory_permissions_mode
        super(BowerFileSystemStorage, self).__init__(location, base_url, file_permissions_mode,
                                                     directory_permissions_mode)

    def listdir(self, path):
        _path = filter(None, path.split(os.path.sep))
        try:
            r = super(BowerFileSystemStorage, self).listdir(path)
            if len(_path) == 1 and 'dist' in r[0]:
                return self.listdir(os.path.join(_path[0], 'dist'))
        except OSError as e:
            if len(_path) <= 1: raise
            r = super(BowerFileSystemStorage, self).listdir(os.path.join(_path[0], 'dist', *_path[1:]))
        return r

    def path(self, name):
        _name = name.split(os.path.sep)
        path = None
        if len(_name) > 1 and _name[1] != 'dist':
            path = self.path(os.path.join(_name[0], 'dist', *_name[1:]))
        if not path or not os.path.exists(path):
            path = super(BowerFileSystemStorage, self).path(name)
        return path


class BowerFinder(FileSystemFinder):
    """Find static files installed with bower"""

    def __init__(self, apps=None, *args, **kwargs):
        self.locations = [
            ('', self._get_bower_components_location()),
        ]
        try:
            self.storages = collections.OrderedDict()
        except AttributeError:
            from ordereddict import OrderedDict
            self.storages = OrderedDict()


        filesystem_storage = BowerFileSystemStorage(location=self.locations[0][1])
        filesystem_storage.prefix = self.locations[0][0]
        self.storages[self.locations[0][1]] = filesystem_storage

    def _get_bower_components_location(self):
        """Get bower components location"""
        path = os.path.join(conf.COMPONENTS_ROOT, 'bower_components')

        # for old bower versions:
        if not os.path.exists(path):
            path = os.path.join(conf.COMPONENTS_ROOT, 'components')
        return path
