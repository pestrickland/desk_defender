"""`temgimg` creates and destroys temporary images."""
import uuid
import os


class TempImage:
    """The temporary image class."""

    def __init__(self, base_path="./", ext=".jpg"):
        """Construct the file path."""
        self.path = "{base_path}/{rand}{ext}".format(base_path=base_path,
                                                     rand=str(uuid.uuid4()),
                                                     ext=ext)

    def cleanup(self):
        """Remove the file."""
        os.remove(self.path)
