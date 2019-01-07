from difflib import SequenceMatcher

from vcs.changes import Changes, Change, ChangeType


class Diff:
    """
    Поиск изменений в двух объектах.
    """
    @classmethod
    def diff(cls, data_before, data_after):
        """
        Поиск изменений в двух объектах.
        :param data_before: Данные до изменений
        :param data_after: Данные после изменений
        :return: Объект Changes
        """
        if data_before is None:
            data_before = ""
        changes = Changes()
        matcher = SequenceMatcher(None, data_before, data_after)
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'delete':
                changes.add(Change(ChangeType.delete, i1, data_before[i1:i2], None))
            elif tag == 'insert':
                changes.add(Change(ChangeType.insert, i1, None, data_after[j1:j2]))
            elif tag == 'replace':
                changes.add(Change(ChangeType.replace, i1, data_before[i1:i2], data_after[j1:j2]))
        return changes
