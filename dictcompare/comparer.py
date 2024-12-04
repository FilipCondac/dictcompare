class DictionaryComparer:
    def __init__(self, strict_types: bool = True, ignore_keys: list[str] = None):
        self.strict_types = strict_types
        self.ignore_keys = ignore_keys or []

    def _should_ignore(self, full_key: str) -> bool:
        return full_key in self.ignore_keys

    def compare(self, dict1: dict, dict2: dict) -> dict:
        return self._compare_dicts(dict1, dict2, ignore_keys=self.ignore_keys)

    def compare_keys(self, dict1: dict, dict2: dict, ignore_keys: list[str] = None) -> dict:
        effective_ignore_keys = ignore_keys or self.ignore_keys
        return self._compare_keys(dict1, dict2, ignore_keys=effective_ignore_keys)

    def _compare_dicts(self, dict1: dict, dict2: dict, parent_key: str = "", ignore_keys: list[str] = None) -> dict:
        """
        Recursive helper to compare nested dictionaries. This gives a detailed summary of all differences.
        
        :param dict1: First dictionary to compare.
        :param dict2: Second dictionary to compare.
        :param parent_key: Key path for tracking nested comparisons.
        :param ignore_keys: List of keys to ignore for this comparison.
        :return: A dictionary summarizing differences.
        """
        differences = {"added": [], "removed": [], "modified": []}

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
                nested_diff = self._compare_dicts(value1, value2, full_key, ignore_keys)
                for diff_type in nested_diff:
                    differences[diff_type].extend(nested_diff[diff_type])
            elif self.strict_types and type(value1) != type(value2):
                # Type mismatch
                differences["modified"].append({
                    "key": full_key,
                    "change_type": "type",
                    "old_type": type(value1).__name__,
                    "new_type": type(value2).__name__
                })
            elif value1 != value2:
                # Value mismatch
                differences["modified"].append({
                    "key": full_key,
                    "change_type": "value",
                    "old_value": value1,
                    "new_value": value2
                })

        return differences

    def _compare_keys(self, dict1: dict, dict2: dict, parent_key: str = "", ignore_keys: list[str] = None) -> dict:
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
