import pytest
from dictcompare import DictionaryComparer


@pytest.fixture
def comparer():
    return DictionaryComparer(strict_types=True)


# Basic Comparisons
def test_compare_dicts_added(comparer):
    dict1 = {"name": "John"}
    dict2 = {"name": "John", "age": 30}
    result = comparer.compare(dict1, dict2)
    assert result["added"] == ["age"]
    assert result["removed"] == []
    assert result["modified"] == []


def test_compare_dicts_removed(comparer):
    dict1 = {"name": "John", "age": 30}
    dict2 = {"name": "John"}
    result = comparer.compare(dict1, dict2)
    assert result["added"] == []
    assert result["removed"] == ["age"]
    assert result["modified"] == []


def test_compare_dicts_modified(comparer):
    dict1 = {"name": "John", "age": 30}
    dict2 = {"name": "John", "age": "30"}  # Type mismatch
    result = comparer.compare(dict1, dict2)
    assert result["added"] == []
    assert result["removed"] == []
    assert result["modified"] == [{"key": "age", "change_type": "type", "old_type": "int", "new_type": "str"}]


# Nested Comparisons
def test_compare_keys_nested(comparer):
    dict1 = {"name": "John", "address": {"city": "Springfield"}}
    dict2 = {"name": "John", "address": {"city": "Springfield", "zip": "12345"}}
    result = comparer.compare(dict1, dict2)
    assert result["added"] == ["address.zip"]
    assert result["removed"] == []
    assert "address.city" in result["common"]


def test_compare_keys_nested_modified(comparer):
    dict1 = {"name": "John", "address": {"city": "Springfield"}}
    dict2 = {"name": "John", "address": {"city": "Shelbyfield", "zip": "12345"}}

    result = comparer.compare(dict1, dict2)
    assert result["added"] == ["address.zip"], "Expected added key: 'address.zip'"
    assert result["removed"] == [], "No keys should be removed"
    assert any(diff["key"] == "address.city" and diff["change_type"] == "value" for diff in result["modified"])


def test_ignore_keys_internal(comparer):
    comparer.ignore_keys = ["age"]
    dict1 = {"name": "John", "age": 30}
    dict2 = {"name": "John", "age": 31}
    result = comparer.compare(dict1, dict2)
    assert result["added"] == []
    assert result["removed"] == []
    assert result["modified"] == []


# Complex Scenarios
def test_nested_dict_comparison(comparer):
    dict1 = {"user": {"name": "John", "details": {"age": 30, "city": "Springfield"}}}
    dict2 = {"user": {"name": "John", "details": {"age": 31, "state": "IL"}}}
    result = comparer.compare(dict1, dict2)
    assert result["added"] == ["user.details.state"]
    assert result["removed"] == ["user.details.city"]
    assert result["modified"] == [{"key": "user.details.age", "change_type": "value", "old_value": 30, "new_value": 31}]


def test_empty_dicts(comparer):
    dict1 = {}
    dict2 = {}
    result = comparer.compare(dict1, dict2)
    assert result["added"] == []
    assert result["removed"] == []
    assert result["modified"] == []


def test_empty_vs_non_empty_dict(comparer):
    dict1 = {}
    dict2 = {"name": "John"}
    result = comparer.compare(dict1, dict2)
    assert result["added"] == ["name"]
    assert result["removed"] == []
    assert result["modified"] == []


# Ignore Keys with Nested Structures
def test_ignore_nested_keys(comparer):
    comparer.ignore_keys = ["user.details.city"]
    dict1 = {"user": {"details": {"city": "Springfield", "age": 30}}}
    dict2 = {"user": {"details": {"city": "Shelbyville", "age": 30}}}
    result = comparer.compare(dict1, dict2)
    assert result["added"] == []
    assert result["removed"] == []
    assert result["modified"] == []  # City is ignored


def test_compare_numeric_with_tolerance_default(comparer):
    dict1 = {"value": 100.0}
    dict2 = {"value": 100.4}  # Difference within default tolerance (0.0)
    result = comparer.compare(dict1, dict2, tolerance=0.5)
    assert result["added"] == []
    assert result["removed"] == []
    assert result["modified"] == []  # Within tolerance, no modification detected


def test_compare_numeric_with_tolerance_override(comparer):
    dict1 = {"value": 100}
    dict2 = {"value": 101}  # Difference outside tolerance
    result = comparer.compare(dict1, dict2, tolerance=0.5)
    assert result["added"] == []
    assert result["removed"] == []
    assert result["modified"] == [{"key": "value", "change_type": "value", "old_value": 100, "new_value": 101}]


def test_compare_nested_lists_and_tolerance(comparer):
    dict1 = {"numbers": [1, 2, 3], "nested": {"list": [1.0, 2.0, 3.0]}}
    dict2 = {"numbers": [2, 3, 4], "nested": {"list": [1.0, 2.1, 3.0]}}  # Within tolerance for nested list
    result = comparer.compare(dict1, dict2, tolerance=0.2)
    assert result["added"] == []
    assert result["removed"] == []
    assert result["modified"] == [
        {"key": "numbers", "change_type": "list", "added": [4], "removed": [1]}
    ]  # No modification for "nested.list" because of tolerance
