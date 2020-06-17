import os
import random
import string

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    """Init ensures there are uploads, data and demo folders.
    generate_paths creates subfolders from a random ID"""

    def generate_ID(self, length=10):
        return ''.join(random.choice(string.ascii_lowercase) for i in range(length))

    def generate_paths(self):
        if self.SESSION_ID is None:
            self.SESSION_ID = self.generate_ID(10)
        self.UPLOAD_FOLDER = os.path.join(self.UPLOAD_BASE, self.SESSION_ID)
        self.DATA_FOLDER = os.path.join(self.DATA_BASE, self.SESSION_ID)
        for path in [self.UPLOAD_FOLDER, self.DATA_FOLDER]:
            if not os.path.exists(path):
                os.makedirs(path)

    def teardown(self):
        for directory in os.listdir(self.UPLOAD_BASE):
            for file in os.listdir(os.path.join(self.UPLOAD_BASE, directory)):
                os.remove(os.path.join(self.UPLOAD_BASE, directory, file))
            os.rmdir(os.path.join(self.UPLOAD_BASE, directory))
        for directory in os.listdir(self.DATA_BASE):
            for file in os.listdir(os.path.join(self.DATA_BASE, directory)):
                os.remove(os.path.join(self.DATA_BASE, directory, file))
            os.rmdir(os.path.join(self.DATA_BASE, directory))

    def __init__(self):
        self.UPLOAD_BASE = os.path.join(basedir, "uploads")
        self.DATA_BASE = os.path.join(basedir, "data")
        self.DEMO_FOLDER = os.path.join(basedir, "demo")
        self.SESSION_ID = self.generate_ID(10)
        for path in [self.UPLOAD_BASE, self.DATA_BASE, self.DEMO_FOLDER]:
            if not os.path.exists(path):
                os.makedirs(path)
        self.teardown()
        self.generate_paths()
        print("Generated new session {}".format(self.SESSION_ID))
