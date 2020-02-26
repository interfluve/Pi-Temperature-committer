import git
import os
from datetime import datetime
from shutil import rmtree

class GitPusher:

    def __init__(self, dir):
        self.dir = dir
        self.author = self.committer = git.Actor("Temperature sensor", "info@darpa.mil")

    def commit(self):
        self.check_repo_flush(self.dir)

        if not self.is_git_repo(self.dir):
            self.init_repo(self.dir)
        repo = git.Repo(self.dir)
        repo.git.add(A=True)
        repo.index.commit('Temperature on ' + datetime.today().strftime('%d.%m.%Y - %H:%M'), author=self.author,
                       committer=self.committer)
        repo.remotes.origin.push(refspec='master', force=True)

    def check_repo_flush(self, path):
        path = os.path.join(path, '.git')

        days_to_flush = int(os.environ.get("GIT_REPO_CLEANUP_PERIOD"))
        if not os.path.exists(path) or not days_to_flush:
            return True

        days_to_flush = (days_to_flush * 86400)  # Convert days to seconds

        flush_before = int(datetime.now().timestamp()) - days_to_flush
        dir_time = int(os.path.getctime(path)) - days_to_flush

        if dir_time > flush_before:
            os.system('rm -rf ' + path)

        return True

    def is_git_repo(self, path):
        try:
            git.Repo(path)
            return True
        except git.exc.InvalidGitRepositoryError:
            return False

    def init_repo(self, path):
        r = git.Repo.init(path)
        r.create_remote('origin', "https://" + os.getenv("GIT_USERNAME") + ':' + os.getenv("GIT_PASSWORD") + '@' + os.getenv("GIT_REPO"))