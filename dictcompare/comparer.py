from typing import Any
class DictionaryComparer:
    def __init__(self, strict_types: bool = True, ignore_keys: list[str] | None = None, numeric_tolerance: float = 0.0):
        """
        Initialize the comparer with optional configurations.

        :param strict_types: Whether to enforce strict type checking.
        :param ignore_keys: List of keys (or key paths) to ignore during comparison.
        :param numeric_tolerance: numeric_tolerance level for numeric comparisons.
        """
        self.strict_types: bool = strict_types
        self.ignore_keys: list[str] | None = ignore_keys or []
        self.numeric_tolerance: float = numeric_tolerance or 0.0

    def compare(self, dict1: dict, dict2: dict, ignore_keys: list[str] | None = None, numeric_tolerance: float = 0.0) -> dict:
        """
        Public method to compare two dictionaries and return their differences.
        """
        effective_ignore_keys = ignore_keys or self.ignore_keys
        effective_numeric_tolerance = numeric_tolerance or self.numeric_tolerance
        return self._compare_dicts(
            dict1, dict2, ignore_keys=effective_ignore_keys, numeric_tolerance=effective_numeric_tolerance
        )

    def compare_keys(self, dict1: dict, dict2: dict, ignore_keys: list[str] | None = None) -> dict:
        """
        Public method to compare the keys of two dictionaries.
        """
        effective_ignore_keys : list[str] | None = ignore_keys or self.ignore_keys
        return self._compare_keys(dict1, dict2, ignore_keys=effective_ignore_keys)

    def compare_lists(self, list1: list, list2: list, numeric_tolerance: float = 0.0) -> dict:
        """
        Public method to compare two lists and return their differences.
        """
        return self._compare_lists(list1, list2, numeric_tolerance)

    def _compare_lists(self, list1: list, list2: list, numeric_tolerance: float = 0.0) -> dict:
        """
        Compare two lists and return added and removed items, considering numeric_tolerance for numeric values.
        """
        added: list = []
        removed: list = []
        queue = [(list1, list2)]  # Use a queue for iterative comparison

        while queue:
            current_list1, current_list2 = queue.pop()

            for item in current_list2:
                if item not in current_list1:
                    if isinstance(item, (int, float)):
                        # Check for numeric tolerance
                        if not any(isinstance(x, (int, float)) and abs(item - x) <= numeric_tolerance for x in current_list1):
                            added.append(item)
                    else:
                        added.append(item)

            for item in current_list1:
                if item not in current_list2:
                    if isinstance(item, (int, float)):
                        # Check for numeric tolerance
                        if not any(isinstance(x, (int, float)) and abs(item - x) <= numeric_tolerance for x in current_list2):
                            removed.append(item)
                    else:
                        removed.append(item)

        return {"added": added, "removed": removed}

    def _compare_dicts(
        self,
        dict1: dict,
        dict2: dict,
        parent_key: str = "",
        ignore_keys: list[str] | None = None,
        numeric_tolerance: float = 0.0,
    ) -> dict:
        """
        Iterative helper to compare nested dictionaries with detailed diffs.
        """
        ignore_keys = ignore_keys or []
        differences: dict[str, list[str | dict[str, Any]]] = {"added": [], "removed": [], "modified": [], "common": []}
        stack = [(dict1, dict2, parent_key)]

        while stack:
            current_dict1, current_dict2, current_parent = stack.pop()

            keys1: set = set(current_dict1.keys())
            keys2: set = set(current_dict2.keys())

            # Check added keys
            for key in keys2 - keys1:
                full_key = f"{current_parent}.{key}".strip(".")
                if full_key not in ignore_keys:
                    differences["added"].append(full_key)

            # Check removed keys
            for key in keys1 - keys2:
                full_key = f"{current_parent}.{key}".strip(".")
                if full_key not in ignore_keys:
                    differences["removed"].append(full_key)

            # Check common keys
            for key in keys1 & keys2:
                full_key = f"{current_parent}.{key}".strip(".")
                if full_key in ignore_keys:
                    continue

                value1, value2 = current_dict1[key], current_dict2[key]

                if isinstance(value1, dict) and isinstance(value2, dict):
                    # Add nested dictionaries to stack
                    stack.append((value1, value2, full_key))
                elif isinstance(value1, list) and isinstance(value2, list):
                    # Compare lists
                    list_diff = self._compare_lists(value1, value2, numeric_tolerance)
                    if list_diff["added"] or list_diff["removed"]:
                        differences["modified"].append(
                            {"key": full_key, "change_type": "list", "added": list_diff["added"], "removed": list_diff["removed"]}
                        )
                    else:
                        differences["common"].append(full_key)
                elif self.strict_types and type(value1) != type(value2):
                    # Type mismatch
                    differences["modified"].append(
                        {"key": full_key, "change_type": "type", "old_type": type(value1).__name__, "new_type": type(value2).__name__}
                    )
                elif isinstance(value1, (int, float)) and isinstance(value2, (int, float)):
                    # Compare numbers with numeric_tolerance
                    if abs(value1 - value2) > numeric_tolerance:
                        differences["modified"].append(
                            {"key": full_key, "change_type": "value", "old_value": value1, "new_value": value2}
                        )
                    else:
                        differences["common"].append(full_key)
                elif value1 != value2:
                    # Value mismatch
                    differences["modified"].append(
                        {"key": full_key, "change_type": "value", "old_value": value1, "new_value": value2}
                    )
                else:
                    # Values are identical
                    differences["common"].append(full_key)

        return differences

    def _compare_keys(self, dict1: dict, dict2: dict, parent_key: str = "", ignore_keys: list[str] | None = None) -> dict:
        """
        Iterative function to compare keys of nested dictionaries.
        """
        ignore_keys = ignore_keys or []
        differences: dict[str, list[str]] = {"added": [], "removed": [], "common": []}
        stack = [(dict1, dict2, parent_key)]

        while stack:
            current_dict1, current_dict2, current_parent = stack.pop()

            keys1: set = set(current_dict1.keys())
            keys2: set = set(current_dict2.keys())

            for key in keys2 - keys1:
                full_key = f"{current_parent}.{key}".strip(".")
                if full_key not in ignore_keys:
                    differences["added"].append(full_key)

            for key in keys1 - keys2:
                full_key = f"{current_parent}.{key}".strip(".")
                if full_key not in ignore_keys:
                    differences["removed"].append(full_key)

            for key in keys1 & keys2:
                full_key = f"{current_parent}.{key}".strip(".")
                if full_key in ignore_keys:
                    continue
                differences["common"].append(full_key)

                if isinstance(current_dict1[key], dict) and isinstance(current_dict2[key], dict):
                    stack.append((current_dict1[key], current_dict2[key], full_key))

        return differences
