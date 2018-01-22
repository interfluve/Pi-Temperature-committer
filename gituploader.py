from pprint import pprint


import git
import os
import time
import datetime
from shutil import rmtree

class GitUploader:

    def __init__(self, dir):
        self.dir = dir
        self.author = self.committer = git.Actor("Rasberry PI Temperature sensor", "info@darpa.mil")

    def commit(self):
        self.check_repo_flush(self.dir)

        if not self.is_git_repo(self.dir):
            self.init_repo(self.dir)

        r = git.Repo(self.dir)
        r.git.add(A=True)
        r.index.commit('Temperature on ' + datetime.datetime.today().strftime('%d.%m.%Y - %H:%M'), author=self.author, committer=self.committer)
        r.remotes.origin.push(refspec='master', force=True)


    def check_repo_flush(self, path):
        path = os.path.join(path, '.git')
        days_to_flush = int(os.environ.get("GIT_FLUSH_PERIOD_DAYS"))
        if not os.path.exists(path) or days_to_flush == 0:
            return True

        days_to_flush = (days_to_flush * 86400) # Convert days to seconds

        flush_before = int(time.time()) - days_to_flush
        dir_time = int(os.path.getctime(path)) - days_to_flush

        if dir_time > flush_before:
            rmtree(path)

        return True




    def init_repo(self, path):
        r = git.Repo.init(path)
        r.create_remote('origin', os.environ.get("SENSOR_DATA_REPO"))

    def is_git_repo(self, path):
        try:
            _ = git.Repo(path).git_dir
            return True
        except git.exc.InvalidGitRepositoryError:
            return False