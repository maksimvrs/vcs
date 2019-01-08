from functools import reduce


class CommitsTree:
    def __init__(self):
        self._init = None
        self._head = None

    def add(self, commit):
        if self._head is not None:
            commit.parent = self._head
            self._head.childrens.append(commit)
        else:
            commit.parent = None
            self._head = commit
            self._init = self._head

    def back(self):
        if self._head is None or self._head.parent is None:
            return None
        self._head = self._head.parent
        return self._head

    def set_head(self, commit_sha):
        commit = self.search_commit(commit_sha)
        if commit is not None:
            self._head = commit
        return commit

    def get_head(self):
        return self._head

    def get_data(self, commit_sha):
        commit = self.search_commit(commit_sha)
        if commit is None:
            return None
        commits = [self._init]
        while commit.parent is not None:
            commits.append(commit)
            commit = commit.parent
        if len(commits) == 0:
            return None
        commits[0] = commits[0].apply()
        return reduce(lambda a, x: x.apply(a), commits)

    def search_commit(self, commit_sha, current=None):
        if self._init is None:
            return None
        if current is None:
            current = self._init
        if self._init.sha.hexdigest() == commit_sha.hexdigest():
            return self._init
        for commit in current.childrens:
            if commit.sha.hexdigest() == commit_sha.hexdigest():
                return commit
            else:
                for next_commit in commit.childrens:
                    result = self.search_commit(commit_sha, next_commit)
                    if result is not None:
                        return result
        return None
