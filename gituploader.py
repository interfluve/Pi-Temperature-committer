from pprint import pprint


import git
import os

import datetime

class GitUploader:

    def __init__(self, dir):
        self.dir = dir
        self.author = self.committer = git.Actor("Rasberry PI Temperature sensor", "info@darpa.mil")

    def commit(self):
        if not self.is_git_repo(self.dir):
            self.init_repo(self.dir)

        r = git.Repo(self.dir)
        r.git.add(A=True)
        r.index.commit('Temperature on ' + datetime.datetime.today().strftime('%d.%m.%Y - %H:%M'), author=self.author, committer=self.committer)
        r.remotes.origin.push(refspec='master')


    def init_repo(self, path):
        r = git.Repo.init(path)
        r.create_remote('origin', os.environ.get("SENSOR_DATA_REPO"))

    def is_git_repo(self, path):
        try:
            _ = git.Repo(path).git_dir
            return True
        except git.exc.InvalidGitRepositoryError:
            return False