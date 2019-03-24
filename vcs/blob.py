class Blob:
    """
    Объект представления файла, находящегося в репозитории, в контексте коммита
    """
    def __init__(self, name, sha, size, changes=None):
        """
        :param name: Имя файла
        :param sha: sha-1 хэш
        :param size: Размер файла в байтах
        :param changes: Объект Changes - изменения, произошедшие в файле
        """
        self.name = name
        self.sha = sha
        self.size = size
        self.changes = changes
        self._data = None

    @property
    def data(self):
        return self._data

    def apply(self, blob=None):
        """
        Данные после применения изменений
        :param blob: Данные до применения изменений
        :return: Данные после применения изменений
        """
        if self._data is not None:
            return self._data
        if blob is not None:
            self._data = self.changes.apply(blob.data)
        else:
            self._data = self.changes.apply(None)
        return self._data

    def save(self):
        return {'name': self.name,
                'sha': self.sha,
                'size': self.size,
                'changes': self.changes.save()}
