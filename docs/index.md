# pytest-item-dict

[![PyPI version](https://img.shields.io/pypi/v/pytest-item-dict.svg)](https://pypi.org/project/pytest-item-dict)
[![Python versions](https://img.shields.io/pypi/pyversions/pytest-item-dict.svg)](https://pypi.org/project/pytest-item-dict)

Get a **hierarchical dict of `session.items`** — a pytest plugin that mirrors your test collection tree into two live Python dicts.
Outputs in `json` and `xml`

## How it works

After collection, the plugin builds a nested dict keyed by the parts of each test's `nodeid` (directory → module → class → test function).  Two dicts are maintained:

| Dict | When populated | Contents |
|---|---|---|
| `collect_dict` | After `pytest_collection_modifyitems` | Pure structure with optional markers |
| `test_dict` | Incrementally during the run, finalised at `pytest_sessionfinish` | Outcomes, durations, markers, and aggregated `@counts` |

Every **parent node** automatically receives a `@counts` dict that sums the outcomes of all leaf tests beneath it:

```json
{
  "@counts": {"passed": 2, "failed": 1, "skipped": 0, "unexecuted": 0, "executed": 3, "total": 3},
  "@total_duration": 0.005,
  "suites": {
    "@counts": {"passed": 2, "failed": 1, "skipped": 0, "unexecuted": 0, "executed": 3, "total": 3},
    "@total_duration": 0.005,
    "test_api.py": {
      "@counts": {"passed": 1, "failed": 1, "skipped": 0, "unexecuted": 0, "executed": 2, "total": 2},
      "@total_duration": 0.003,
      "TestEndpoints": {
        "@counts": {"passed": 1, "failed": 1, "skipped": 0, "unexecuted": 0, "executed": 2, "total": 2},
        "@total_duration": 0.003,
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
| `set_test_dict_setup_teardown` | `false` | Record setup/teardown phase outcomes as separate nodes in `test_dict` |

## Accessing the dicts

Retrieve the plugin instance from any hook via the plugin manager:

```python
from pytest_item_dict.plugin import ItemDictPlugin, ITEM_DICT_PLUGIN_NAME

def pytest_sessionfinish(session):
    plugin: ItemDictPlugin = session.config.pluginmanager.get_plugin(ITEM_DICT_PLUGIN_NAME)
    print(plugin.collect_dict.hierarchy)
    print(plugin.test_dict.hierarchy)
```

## Setup / teardown reporting

Enable `set_test_dict_setup_teardown = true` to record the outcome of each
test's setup and teardown phases as separate nodes in `test_dict`.

### Node placement

| Node key | Location in hierarchy | Condition |
|---|---|---|
| `setup_method` | inside each test node | always, for class-based tests |
| `teardown_method` | inside each test node | always, for class-based tests |
| `setup_function` | inside each test node | always, for module-level functions |
| `teardown_function` | inside each test node | always, for module-level functions |
| `setup_class` | at the class node (sibling of test methods) | only when the class defines `setup_class` |
| `teardown_class` | at the class node (sibling of test methods) | only when the class defines `teardown_class` |

Each node contains a single `@outcome` key whose value is one of
`"passed"`, `"failed"`, `"skipped"`, or `"error"`.

None of these nodes are counted by `@counts` aggregation — they are
purely informational and never inflate test totals.

### Example output

```json
{
  "test_api.py": {
    "TestEndpoints": {
      "setup_class":    { "@outcome": "passed" },
      "test_get_users": {
        "@outcome": "passed",
        "setup_method":    { "@outcome": "passed" },
        "teardown_method": { "@outcome": "passed" }
      },
      "test_post_user": {
        "@outcome": "failed",
        "setup_method":    { "@outcome": "passed" },
        "teardown_method": { "@outcome": "passed" }
      },
      "teardown_class": { "@outcome": "passed" }
    },
    "test_standalone": {
      "@outcome": "passed",
      "setup_function":    { "@outcome": "passed" },
      "teardown_function": { "@outcome": "passed" }
    }
  }
}
```

> **Note** — `setup_class` records the setup-phase outcome of the *first*
> test in the class (which includes the `setup_class` call).  Similarly,
> `teardown_class` records the teardown-phase outcome of the *last* test
> in the class.
