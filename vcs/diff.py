from difflib import SequenceMatcher

from vcs.changes import Changes, Change, ChangeType
from vcs.merge import Merge, MergeUnit, MergeUnitStatus


class Diff:
    """
    Поиск изменений в двух объектах.
    """
    @staticmethod
    def diff(data_before, data_after):
        """
        Поиск изменений в двух объектах.
        :param data_before: Данные до изменений
        :param data_after: Данные после изменений
        :return: Объект Changes
        """
        if data_before is None:
            data_before = ""
        changes = Changes()
        matcher = SequenceMatcher(None,
                                  data_before,
                                  data_after,
                                  autojunk=False)
        offset = 0
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'delete':
                changes.add(Change(ChangeType.delete,
                                   i1 + offset,
                                   i2 + offset))
                offset -= i2 - i1
            elif tag == 'insert':
                changes.add(Change(ChangeType.insert,
                                   i1 + offset,
                                   data_after[j1:j2]))
                offset += j2 - j1
            elif tag == 'replace':
                changes.add(Change(ChangeType.delete,
                                   i1 + offset, i2 + offset))
                changes.add(Change(ChangeType.insert,
                                   i1 + offset,
                                   data_after[j1:j2]))
                offset += (j2 - j1) - (i2 - i1)
        return changes

    @staticmethod
    def diff3(original, first, second):
        # original = original.splitlines()
        # first = first.splitlines()
        # second = second.splitlines()
        result = Merge()
        match = Diff.max_match(original, first, second)
        if match[0] is not None:
            result.add(MergeUnit(original[match[0][0]:match[0][0] + match[1]],
                                 first[match[0][1]:match[0][1] + match[1]],
                                 second[match[0][2]:match[0][2] + match[1]],
                                 MergeUnitStatus.Stable))
            del original[match[0][0]:match[0][0] + match[1]]
            del first[match[0][1]:match[0][1] + match[1]]
            del second[match[0][2]:match[0][2] + match[1]]

            result.add_left(Diff.diff3(original[0:match[0][0]],
                                       first[0:match[0][1]],
                                       second[0:match[0][2]]))
            result.add_right(Diff.diff3(
                original[match[0][0]:match[0][0] + len(original)],
                first[match[0][1]:match[0][1] + len(first)],
                second[match[0][2]:match[0][2] + len(second)]))
        elif not len(original) == len(first) == len(second) == 0:
            result.add(MergeUnit(original,
                                 first,
                                 second,
                                 MergeUnitStatus.Conflict))
        return result

    @staticmethod
    def max_match(original, first, second):
        """
        Find maximum matching in 3 string.
        :return: (index in original, index in first, index in second), length
        """
        if len(original) == len(first) == len(second):
            return None, 0
        if isinstance(original, str):
            original += '\u000D'
        elif isinstance(original, list):
            original.append('\u000D')
        else:
            raise ValueError('Arguments type error')
        if isinstance(first, str):
            first += '\u000D'
        elif isinstance(first, list):
            first.append('\u000D')
        else:
            raise ValueError('Arguments type error')
        if isinstance(second, str):
            second += '\u000D'
        elif isinstance(original, list):
            second.append('\u000D')
        else:
            raise ValueError('Arguments type error')
        substrings = [[[None for _ in second]
                       for _ in first] for _ in original]
        max_match = None
        max_match_len = 0
        for original_index, original_value in enumerate(original):
            for first_index, first_value in enumerate(first):
                for second_index, second_value in enumerate(second):
                    if original_value == first_value == second_value:
                        if original_index == 0 or \
                           first_index == 0 or \
                           second_index == 0:
                            substrings[
                                original_index][
                                first_index][
                                    second_index] = 1
                        else:
                            substrings[
                                original_index][
                                    first_index][
                                        second_index] = substrings[
                                            original_index - 1
                            ][first_index - 1
                              ][second_index - 1
                                ] + 1
                    else:
                        if original_index != 0 and \
                           first_index != 0 and \
                           second_index != 0 and \
                           substrings[
                                original_index - 1][
                                    first_index - 1][
                                        second_index - 1] > max_match_len:
                            max_match_len = substrings[
                                original_index - 1][
                                    first_index - 1][
                                        second_index - 1]
                            max_match = (original_index - max_match_len,
                                         first_index - max_match_len,
                                         second_index - max_match_len)
                        substrings[
                            original_index][
                                first_index][
                                    second_index] = 0
        return max_match, max_match_len
