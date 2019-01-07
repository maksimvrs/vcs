class Blob:
    """
    Объект представления файла, находящегося в репозитории
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
