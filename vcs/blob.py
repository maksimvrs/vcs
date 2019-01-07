class Blob:
    """
    Объект представления файла, находящегося в репозитории, в контексте коммита
    """
    def __init__(self, name, sha, size, changes=None, data=None):
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
        self._data = data

    def data(self, data=None):
        """
        Данные после применения изменений
        :param data: Данные до применения изменений
        :return: Данные после применения изменений
        """
        if self._data is None:
            return self.changes.apply(data)
        return self._data

    def reset(self, data=None):
        """
        Откатить изменения данных
        :param data: Данные до отмены изменений
        :return: Данные после отмены изменений
        """
        if self._data is None:
            return self.changes.roll_back(data)
        return self.changes.roll_back(self._data)

    def clear(self):
        self._data = None
