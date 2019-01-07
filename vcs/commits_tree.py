class CommitsTree:
    def __init__(self):
        self.init = None
        self.head = None

    def add(self, commit):
        if self.head is not None:
            commit.parent = self.head
            self.head.childrens.append(commit)
        else:
            commit.parent = None
            self.head = commit
            self.init = self.head

    def back(self):
        if self.head is None or self.head.parent is None:
            return None
        self.head = self.head.parent
        return self.head

    def set_head(self, commit_sha, current=None):
        if self.init is None:
            return None
        if current is None:
            current = self.init
        for commit in current.cildrens:
            if commit.sha == commit_sha:
                self.head = commit
                return True
            else:
                for next_commit in commit.childrens:
                    if self.set_head(commit_sha, next_commit):
                        return True
        return False

    def get(self):
        return self.head
