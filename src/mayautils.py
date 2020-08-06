import logging

import pymel.core as pmc
from pymel.core.system import Path


log = logging.getLogger(__name__)


class SceneFile(object):
    """This class represents a DCC software scene file


    The class will be a convenient object that we can use to manipulate our scene files.
    Examples features include the ability to predefine our naming conventions and automatically increment our versions.

    Attributes:
        dir (Path, optional): Directory to the scene file. Defaults to ''.
        descriptor (str, optional): Short descriptor of the scene file. Defaults to "main".
            Defaults to "main".
        version (int, optional): Version number. Defaults to 1.
        ext (str, optional): Extension. Defaults to "ma"

    """

    def __init__(self, dir='', descriptor="main", version=1, ext="ma"):
        """Initialises our attributes when class is instantiated.

        If the scene has not been saved, initialise the attributes based on
        the defaults. Otherwise, if the scene is already saved, initialise
        attributes based on the file name of the opened scene

        """

        self._dir = Path(dir)
        self.descriptor = descriptor
        self.version = version
        self.ext = ext
        scene = pmc.system.sceneName()
        if scene:
            self._init_properties_from_path(scene)

    @property
    def dir(self):
        return self._dir

    @dir.setter
    def dir(self, val):
        self._dir = Path(val)

    def basename(self):
        """Returns a scene file name

        e.g. ship_001.ma, car_011.hip

        Returns:
            str: The name of the scene file.

        """
        name_pattern = "{descriptor}_{version:03d}.{ext}"
        name = name_pattern.format(descriptor=self.descriptor,
                                   version=self.version,
                                   ext=self.ext)
        return name

    def path(self):
        """The function returns a path to scene file.

        This includes the drive letter, any directionary path and the file name.

        Returns:
            Path: The path to the scene file.

        """
        return Path(self.dir) / self.basename()

    def _init_properties_from_path(self, path):
        """Sets the values of the properties from the basename"""
        self._dir = path.dirname()
        self.ext = path.ext[1:]
        self.descriptor, version = path.name.split("_")
        self.version = int(version.split(".")[0][1:])

    def save(self):
        """Saves the scene file.

        Returns:
            :obj:'Path': The path to the scene file if successful, None, otherwise.

        """
        try:
            pmc.system.saveAs(self.path())
        except RuntimeError:
            log.warning("Missing directories. Creating Directories.")
            self.dir.makedirs_p()
            pmc.system.saveAs(self.path())

    def next_avail_version(self):
        """Return the next available version"""
        pattern = "{descriptor}_v*.{ext}".format(descriptor = self.descriptor,
                                                 ext=self.ext)
        self.dir.files()
        matched_scenes =[file for file in self.dir.files()
                         if file.fnmatch(pattern)]
        versions = [int(scene.name.split("_v")[1].split(".")[0])
                    for scene in matched_scenes]
        versions = list(set(versions))
        versions.sort()
        return versions[-1] + 1

    def increment_and_save(self):
        """Increments the version and saves the scene file

        If existing versions of a file already exist, it should increment from
        the largest number available in the folder.

        Returns:
            Path: The path to the scene file if successful, None, otherwise.
        """
        self.version = self.next_avail_version()
        self.save()

