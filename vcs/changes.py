class ChangeType:
    insert = 0
    delete = 1


class Change:
    def __init__(self, change_type, index, data):
        self._type = change_type
        self._index = index
        self._data = data

    @property
    def type(self):
        return self._type

    @property
    def index(self):
        return self._index

    @property
    def data(self):
        return self._data


class Changes:
    """
    Изменения, внесенные в объект.
    """

    def __init__(self):
        # Новые фрагменты: (ChangeType.insert, индекс начала нового фрагмента,
        #                   данные)
        # Удаленные фрагменты: (ChangeType.delete, индекс начала фрагмента,
        #                       размер фрагмента)
        # Измененные фрагменты: (ChangeType.replace, индекс начала фрагмента,
        #                        данные)
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
        for change in self._changes:
            if change.type == ChangeType.insert:
                result[change.index:change.index] = list(change.data)
            elif change.type == ChangeType.delete:
                del result[change.index:change.data]
        return ''.join(result)

    def load(self, data):
        for change in data:
            self.add(Change(change['type'], change['index'],
                            change['data']))

    def save(self):
        return [{'type': change.type,
                 'index': change.index,
                 'data': change.data} for change in self._changes]
