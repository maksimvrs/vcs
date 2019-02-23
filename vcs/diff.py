from difflib import SequenceMatcher
from string import whitespace

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
        matcher = SequenceMatcher(None, data_before, data_after, autojunk=False)
        offset = 0
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'delete':
                changes.add(Change(ChangeType.delete, i1 + offset, i2 + offset))
                offset -= i2 - i1
            elif tag == 'insert':
                changes.add(Change(ChangeType.insert, i1 + offset, data_after[j1:j2]))
                offset += j2 - j1
            elif tag == 'replace':
                changes.add(Change(ChangeType.delete, i1 + offset, i2 + offset))
                changes.add(Change(ChangeType.insert, i1 + offset, data_after[j1:j2]))
                offset += (j2 - j1) - (i2 - i1)
        return changes
