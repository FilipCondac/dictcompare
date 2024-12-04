from dictcompare import compare_dicts, compare_keys

# Basic Tests for Functional API
def test_compare_dicts_api():
    dict1 = {"name": "John"}
    dict2 = {"name": "John", "age": 30}
    result = compare_dicts(dict1, dict2)
    assert result["added"] == ["age"]
    assert result["removed"] == []
    assert result["modified"] == []

def test_compare_keys_api():
    dict1 = {"name": "John"}
    dict2 = {"name": "John", "age": 30}
    result = compare_keys(dict1, dict2)
    assert result["added"] == ["age"]
    assert result["removed"] == []
    assert result["common"] == ["name"]

# Test API with Ignore Keys
def test_compare_dicts_api_ignore_keys():
    dict1 = {"name": "John", "age": 30}
    dict2 = {"name": "John", "age": 31}
    result = compare_dicts(dict1, dict2, ignore_keys=["age"])
    assert result["added"] == []
    assert result["removed"] == []
    assert result["modified"] == []  # 'age' is ignored

def test_compare_keys_api_ignore_keys():
    dict1 = {"name": "John", "address": {"city": "Springfield"}}
    dict2 = {"name": "John", "address": {"city": "Shelbyville", "zip": "12345"}}
    result = compare_keys(dict1, dict2, ignore_keys=["address.zip"])
    assert sorted(result["added"]) == []
    assert sorted(result["removed"]) == []
    assert sorted(result["common"]) == sorted(["name", "address", "address.city"])

# Test Edge Cases for Functional API
def test_compare_dicts_api_empty_dicts():
    dict1 = {}
    dict2 = {}
    result = compare_dicts(dict1, dict2)
    assert result["added"] == []
    assert result["removed"] == []
    assert result["modified"] == []

def test_compare_keys_api_empty_dicts():
    dict1 = {}
    dict2 = {}
    result = compare_keys(dict1, dict2)
    assert result["added"] == []
    assert result["removed"] == []
    assert result["common"] == []
