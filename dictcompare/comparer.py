class DictionaryComparer:
    def __init__(self, strict_types: bool = True, ignore_keys: list[str] = None, numeric_tolerance: float = 0.0):
        """
        Initialize the comparer with optional configurations.

        :param strict_types: Whether to enforce strict type checking.
        :param ignore_keys: List of keys (or key paths) to ignore during comparison.
        :param numeric_tolerance: numeric_tolerance level for numeric comparisons.
        """
        self.strict_types = strict_types
        self.ignore_keys = ignore_keys or []
        self.numeric_tolerance = numeric_tolerance or 0.0

    def compare(self, dict1: dict, dict2: dict, ignore_keys: list[str] = None, numeric_tolerance: float = 0.0) -> dict:
        """
        Public method to compare two dictionaries and return their differences.
        """

        effective_ignore_keys = ignore_keys or self.ignore_keys
        effective_numeric_tolerance = numeric_tolerance or self.numeric_tolerance
        return self._compare_dicts(
            dict1, dict2, ignore_keys=effective_ignore_keys, numeric_tolerance=effective_numeric_tolerance
        )

    def compare_keys(self, dict1: dict, dict2: dict, ignore_keys: list[str] = None) -> dict:
        """
        Public method to compare the keys of two dictionaries.
        """
        effective_ignore_keys = ignore_keys or self.ignore_keys
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
        added = []
        removed = []

        for item in list2:
            if item not in list1:
                if isinstance(item, (int, float)):
                    # Check if any item in list1 is within the numeric_tolerance range
                    if not any(isinstance(x, (int, float)) and abs(item - x) <= numeric_tolerance for x in list1):
                        added.append(item)
                else:
                    added.append(item)

        for item in list1:
            if item not in list2:
                if isinstance(item, (int, float)):
                    # Check if any item in list2 is within the numeric_tolerance range
                    if not any(isinstance(x, (int, float)) and abs(item - x) <= numeric_tolerance for x in list2):
                        removed.append(item)
                else:
                    removed.append(item)

        return {"added": added, "removed": removed}

    def _compare_dicts(
        self,
        dict1: dict,
        dict2: dict,
        parent_key: str = "",
        ignore_keys: list[str] = None,
        numeric_tolerance: float = 0.0,
    ) -> dict:
        """
        Recursive helper to compare nested dictionaries with detailed diffs.
        """
        differences = {"added": [], "removed": [], "modified": [], "common": []}

        keys1 = set(dict1.keys())
        keys2 = set(dict2.keys())

        # Check added keys
        for key in keys2 - keys1:
            full_key = f"{parent_key}.{key}".strip(".")
            if full_key not in ignore_keys:
                differences["added"].append(full_key)

        # Check removed keys
        for key in keys1 - keys2:
            full_key = f"{parent_key}.{key}".strip(".")
            if full_key not in ignore_keys:
                differences["removed"].append(full_key)

        # Check common keys
        for key in keys1 & keys2:
            full_key = f"{parent_key}.{key}".strip(".")
            if full_key in ignore_keys:
                continue

            value1, value2 = dict1[key], dict2[key]

            if isinstance(value1, dict) and isinstance(value2, dict):
                # Recurse for nested dictionaries
                nested_diff = self._compare_dicts(value1, value2, full_key, ignore_keys, numeric_tolerance)
                for diff_type in nested_diff:
                    differences[diff_type].extend(nested_diff[diff_type])
            elif isinstance(value1, list) and isinstance(value2, list):
                # Compare lists
                list_diff = self._compare_lists(value1, value2, numeric_tolerance)
                if list_diff["added"] or list_diff["removed"]:
                    differences["modified"].append(
                        {
                            "key": full_key,
                            "change_type": "list",
                            "added": list_diff["added"],
                            "removed": list_diff["removed"],
                        }
                    )
                else:
                    differences["common"].append(full_key)
            elif self.strict_types and type(value1) != type(value2):
                # Type mismatch
                differences["modified"].append(
                    {
                        "key": full_key,
                        "change_type": "type",
                        "old_type": type(value1).__name__,
                        "new_type": type(value2).__name__,
                    }
                )
            elif isinstance(value1, (int, float)) and isinstance(value2, (int, float)):
                # Compare numbers with numeric_tolerance
                if abs(value1 - value2) > numeric_tolerance:
                    differences["modified"].append(
                        {
                            "key": full_key,
                            "change_type": "value",
                            "old_value": value1,
                            "new_value": value2,
                        }
                    )
                else:
                    differences["common"].append(full_key)
            elif value1 != value2:
                # Value mismatch
                differences["modified"].append(
                    {
                        "key": full_key,
                        "change_type": "value",
                        "old_value": value1,
                        "new_value": value2,
                    }
                )
            else:
                # Values are identical
                differences["common"].append(full_key)

        return differences

    def _compare_keys(self, dict1: dict, dict2: dict, parent_key: str = "", ignore_keys: list[str] = None) -> dict:
        """
        Recursive function to compare keys of nested dictionaries.
        """
        differences = {"added": [], "removed": [], "common": []}

        keys1 = set(dict1.keys())
        keys2 = set(dict2.keys())

        for key in keys2 - keys1:
            full_key = f"{parent_key}.{key}".strip(".")
            if full_key not in ignore_keys:
                differences["added"].append(full_key)
        for key in keys1 - keys2:
            full_key = f"{parent_key}.{key}".strip(".")
            if full_key not in ignore_keys:
                differences["removed"].append(full_key)

        for key in keys1 & keys2:
            full_key = f"{parent_key}.{key}".strip(".")
            if full_key in ignore_keys:
                continue
            differences["common"].append(full_key)

            if isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
                nested_diff = self._compare_keys(dict1[key], dict2[key], full_key, ignore_keys)
                differences["added"].extend(nested_diff["added"])
                differences["removed"].extend(nested_diff["removed"])
                differences["common"].extend(nested_diff["common"])

        return differences
