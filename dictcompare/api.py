from .comparer import DictionaryComparer


def compare_dicts(
    dict1: dict, dict2: dict, strict_types: bool = True, ignore_keys: list[str] = None, numeric_tolerance: float = 0.0
) -> dict:
    """
    Functional API to compare two dictionaries in detail, including added, removed, and modified values.

    :param dict1: The first dictionary to compare.
    :param dict2: The second dictionary to compare.
    :param strict_types: Whether to enforce strict type checking.
    :param ignore_keys: List of keys (or key paths) to ignore during the comparison. Defaults to None.
    :return: A dictionary summarizing differences (added, removed, modified).
    """
    comparer = DictionaryComparer(strict_types, ignore_keys, numeric_tolerance)
    return comparer.compare(dict1, dict2)


def compare_keys(dict1: dict, dict2: dict, strict_types: bool = True, ignore_keys: list[str] = None) -> dict:
    """
    Functional API to compare only the keys of two dictionaries, including nested keys.

    :param dict1: The first dictionary to compare.
    :param dict2: The second dictionary to compare.
    :param strict_types: Whether to enforce strict type checking (not relevant for key comparison but kept for symmetry).
    :param ignore_keys: List of keys (or key paths) to ignore during the comparison. Defaults to None.
    :return: A dictionary summarizing key differences (added, removed, common).
    """
    comparer = DictionaryComparer(strict_types, ignore_keys)
    return comparer.compare_keys(dict1, dict2)


def compare_lists(list1: list, list2: list, numeric_tolerance: float = 0.0) -> dict:
    """
    Functional API to compare two lists and return their differences.

    :param list1: The first list to compare.
    :param list2: The second list to compare.
    :param numeric_tolerance: numeric_tolerance level for numeric comparisons.
    :return: A dictionary summarizing list differences (added, removed).
    """
    comparer = DictionaryComparer()
    return comparer.compare_lists(list1, list2, numeric_tolerance)
