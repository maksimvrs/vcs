class ChangeType:
    insert = 0
    delete = 1
    replace = 2


class Change:
    def __init__(self, change_type: ChangeType, index: int, data_before: str, data_after: str):
        self._type = change_type
        self._index = index
        self._data_before = data_before
        self._data_after = data_after

    @property
    def type(self):
        return self._type

    @property
    def index(self):
        return self._index

    @property
    def data_before(self):
        return self._data_before

    @property
    def data_after(self):
        return self._data_after


class Changes:
    """
    Изменения, внесенные в объект.
    """

    def __init__(self):
        # Новые фрагменты: (ChangeType.insert, индекс начала нового фрагмента, данные)
        # Удаленные фрагменты: (ChangeType.delete, индекс начала фрагмента, размер фрагмента)
        # Измененные фрагменты: (ChangeType.replace, индекс начала фрагмента, данные)
        self._changes = list()

    def add(self, change):
        self._changes.append(change)

    def apply(self, data):
        """
        Применить изменения к данным
        :param data: Данные, к которым нужно применить изменения
        :return: Измененные данные
        """
        if data is None:
            data = ""
        result = list(data)
        for change in reversed(self._changes):
            if change.type == ChangeType.insert:
                result[change.index:change.index] = list(change.data_after)
            elif change.type == ChangeType.delete:
                del result[change.index:len(change.data_before)+change.index]
            elif change.type == ChangeType.replace:
                result[change.index:len(change.data_before)+change.index] = list(change.data_after)
        return ''.join(result)

    def roll_back(self, data):
        """
        Откатить изменения
        :param data: Данные, изменения для которыз нужно откатить
        :return: Предыдущая версия данных, с отмененными изменениями
        """
        if data is None:
            data = ""
        result = list(data)
        for change in self._changes:
            if change.type == ChangeType.insert:
                del result[change.index:len(change.data_after)+change.index]
            elif change.type == ChangeType.delete:
                result[change.index: change.index] = list(change.data_before)
            elif change.type == ChangeType.replace:
                result[change.index:len(change.data_after)+change.index] = list(change.data_before)
        return ''.join(result)

    def load(self, data):
        for change in data:
            self.add(Change(change['type'], change['index'],
                            change['data_before'], change['data_after']))

    def save(self):
        return [{'type': change.type,
                 'index': change.index,
                 'data_before': change.data_before,
                 'data_after': change.data_after} for change in self._changes]
