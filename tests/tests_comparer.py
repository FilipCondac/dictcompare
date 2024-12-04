import pytest
from dictcompare import DictionaryComparer


@pytest.fixture
def comparer():
    return DictionaryComparer(strict_types=True)

# Basic Comparisons
def test_compare_dicts_added(comparer):
    dict1 = {"name": "John"}
    dict2 = {"name": "John", "age": 30}
    result = comparer._compare_dicts(dict1, dict2)
    assert result["added"] == ["age"]
    assert result["removed"] == []
    assert result["modified"] == []

def test_compare_dicts_removed(comparer):
    dict1 = {"name": "John", "age": 30}
    dict2 = {"name": "John"}
    result = comparer._compare_dicts(dict1, dict2)
    assert result["added"] == []
    assert result["removed"] == ["age"]
    assert result["modified"] == []

def test_compare_dicts_modified(comparer):
    dict1 = {"name": "John", "age": 30}
    dict2 = {"name": "John", "age": "30"}  # Type mismatch
    result = comparer._compare_dicts(dict1, dict2)
    assert result["added"] == []
    assert result["removed"] == []
    assert result["modified"] == [
        {"key": "age", "change_type": "type", "old_type": "int", "new_type": "str"}
    ]

# Nested Comparisons
def test_compare_keys_nested(comparer):
    dict1 = {"name": "John", "address": {"city": "Springfield"}}
    dict2 = {"name": "John", "address": {"city": "Shelbyville", "zip": "12345"}}
    result = comparer._compare_keys(dict1, dict2)
    assert result["added"] == ["address.zip"]
    assert result["removed"] == []
    assert "address.city" in result["common"]

def test_ignore_keys_internal(comparer):
    comparer.ignore_keys = ["age"]
    dict1 = {"name": "John", "age": 30}
    dict2 = {"name": "John", "age": 31}
    result = comparer._compare_dicts(dict1, dict2)
    assert result["added"] == []
    assert result["removed"] == []
    assert result["modified"] == []

# Complex Scenarios
def test_nested_dict_comparison(comparer):
    dict1 = {"user": {"name": "John", "details": {"age": 30, "city": "Springfield"}}}
    dict2 = {"user": {"name": "John", "details": {"age": 31, "state": "IL"}}}
    result = comparer._compare_dicts(dict1, dict2)
    assert result["added"] == ["user.details.state"]
    assert result["removed"] == ["user.details.city"]
    assert result["modified"] == [
        {"key": "user.details.age", "change_type": "value", "old_value": 30, "new_value": 31}
    ]

def test_empty_dicts(comparer):
    dict1 = {}
    dict2 = {}
    result = comparer._compare_dicts(dict1, dict2)
    assert result["added"] == []
    assert result["removed"] == []
    assert result["modified"] == []

def test_empty_vs_non_empty_dict(comparer):
    dict1 = {}
    dict2 = {"name": "John"}
    result = comparer._compare_dicts(dict1, dict2)
    assert result["added"] == ["name"]
    assert result["removed"] == []
    assert result["modified"] == []

# Ignore Keys with Nested Structures
def test_ignore_nested_keys(comparer):
    comparer.ignore_keys = ["user.details.city"]
    dict1 = {"user": {"details": {"city": "Springfield", "age": 30}}}
    dict2 = {"user": {"details": {"city": "Shelbyville", "age": 30}}}
    result = comparer._compare_dicts(dict1, dict2)
    assert result["added"] == []
    assert result["removed"] == []
    assert result["modified"] == []  # City is ignored
