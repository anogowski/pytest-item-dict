# pytest-item-dict

[![PyPI version](https://img.shields.io/pypi/v/pytest-item-dict.svg)](https://pypi.org/project/pytest-item-dict)
[![Python versions](https://img.shields.io/pypi/pyversions/pytest-item-dict.svg)](https://pypi.org/project/pytest-item-dict)

Get a **hierarchical dict of `session.items`** — a pytest plugin that mirrors your test collection tree into two live Python dicts.

## How it works

After collection, the plugin builds a nested dict keyed by the parts of each test's `nodeid` (directory → module → class → test function).  Two dicts are maintained:

| Dict | When populated | Contents |
|---|---|---|
| `collect_dict` | After `pytest_collection_modifyitems` | Pure structure with optional markers |
| `test_dict` | Incrementally during the run, finalised at `pytest_sessionfinish` | Outcomes, durations, markers, and aggregated `@counts` |

Every **parent node** automatically receives a `@counts` dict that sums the outcomes of all leaf tests beneath it:

```json
{
  "@counts": {"passed": 2, "failed": 1, "skipped": 0, "unexecuted": 0, "total": 3},
  "suites": {
    "test_api.py": {
      "@counts": {"passed": 1, "failed": 1, "skipped": 0, "unexecuted": 0, "total": 2},
      "TestEndpoints": {
        "@counts": {"passed": 1, "failed": 1, "skipped": 0, "unexecuted": 0, "total": 2},
        "test_get_users": {"@outcome": "passed"},
        "test_post_user":  {"@outcome": "failed"}
      }
    }
  }
}
```

## Installation

```shell
pip install pytest-item-dict
```

The plugin self-registers via the `pytest11` entry point — no `conftest.py` changes required for basic use.

## INI options

| Option | Default | Description |
|---|---|---|
| `create_item_dict` | `true` | Enable/disable the plugin entirely |
| `set_collect_dict_markers` | `false` | Annotate `collect_dict` nodes with marker names |
| `set_test_dict_markers` | `false` | Annotate `test_dict` nodes with marker names |
| `set_test_dict_outcomes` | `true` | Record `@outcome` on each test node |
| `set_test_dict_durations` | `false` | Record `@duration` (float seconds) per test and `@total_duration` on parent nodes |
| `update_dict_on_test` | `true` | Update `test_dict` after every individual test (real-time) |

## Accessing the dicts

Retrieve the plugin instance from any hook via the plugin manager:

```python
from pytest_item_dict.plugin import ItemDictPlugin, ITEM_DICT_PLUGIN_NAME

def pytest_sessionfinish(session):
    plugin: ItemDictPlugin = session.config.pluginmanager.get_plugin(ITEM_DICT_PLUGIN_NAME)
    print(plugin.collect_dict.hierarchy)
    print(plugin.test_dict.hierarchy)
```
