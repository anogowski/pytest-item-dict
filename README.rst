================
pytest-item-dict
================

.. image:: https://img.shields.io/pypi/v/pytest-item-dict.svg
    :target: https://pypi.org/project/pytest-item-dict
    :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/pytest-item-dict.svg
    :target: https://pypi.org/project/pytest-item-dict
    :alt: Python versions

.. image:: https://img.shields.io/pypi/l/pytest-item-dict.svg
    :target: https://pypi.org/project/pytest-item-dict
    :alt: License

.. image:: https://img.shields.io/pypi/dm/pytest-item-dict.svg
    :target: https://pypi.org/project/pytest-item-dict
    :alt: Monthly Downloads

.. image:: https://img.shields.io/pypi/wheel/pytest-item-dict.svg
    :target: https://pypi.org/project/pytest-item-dict
    :alt: Wheel

.. image:: https://img.shields.io/maintenance/yes/2026.svg
    :alt: Maintained

.. image:: https://github.com/anogowski/pytest-item-dict/actions/workflows/publish-to-test-pypi.yml/badge.svg
    :target: https://github.com/anogowski/pytest-item-dict/actions/workflows/publish-to-test-pypi.yml
    :alt: See Build Status on GitHub Actions

Get a hierarchical dict of session.items
Used code from `pytest-collect-formatter`_

----

This `pytest`_ plugin was generated with `Cookiecutter`_ along with `@hackebrot`_'s `cookiecutter-pytest-plugin`_ template.


Features
--------

* Builds a **hierarchical dict** mirroring the pytest collection tree (directory → module → class → test function) from ``session.items``
* Provides two live dicts:

  * ``collect_dict`` — pure structure populated after collection, with optional marker annotations; every non-leaf node carries a ``@tests`` count of collected tests beneath it
  * ``test_dict`` — populated incrementally during the run; records outcomes, durations, markers, and aggregated ``@counts``

* Every parent node in ``test_dict`` automatically receives a ``@counts`` dict that sums the outcomes of all leaf tests beneath it (``passed``, ``failed``, ``skipped``, ``unexecuted``, ``executed``, ``total``) and a ``@total_duration`` float
* Configurable via ``pytest.ini`` / ``pyproject.toml`` options:

  * ``create_item_dict`` — enable/disable the plugin entirely (default: ``true``)
  * ``set_collect_dict_markers`` — annotate ``collect_dict`` nodes with marker names (default: ``false``)
  * ``set_test_dict_markers`` — annotate ``test_dict`` nodes with marker names (default: ``false``)
  * ``set_test_dict_outcomes`` — record ``@outcome`` on each test node (default: ``true``)
  * ``set_test_dict_durations`` — record ``@duration`` per test and ``@total_duration`` on parent nodes (default: ``false``)
  * ``update_dict_on_test`` — update ``test_dict`` after every individual test in real-time (default: ``true``)
  * ``set_test_dict_setup_teardown`` — record setup/teardown phase outcomes as separate nodes in ``test_dict`` (default: ``false``)
  * ``set_test_hierarchy_dict_outcomes`` — bubble ``@counts`` up through all parent nodes (default: ``false``)
  * ``set_test_hierarchy_dict_durations`` — bubble ``@total_duration`` up through all parent nodes (default: ``false``)

* Self-registers via the ``pytest11`` entry point — no ``conftest.py`` changes required for basic use
* Dicts are accessible from any hook via the plugin manager


Requirements
------------

* Python >= 3.11
* pytest >= 8.3.0


Installation
------------

You can install "pytest-item-dict" via `pip`_ from `PyPI`_::

    $ pip install pytest-item-dict


Usage
-----

The plugin self-registers — no changes to your code are required for basic use.
Access the hierarchies from any pytest hook via the plugin manager.

**Accessing the dicts**

.. code-block:: python

    # conftest.py
    from pytest_item_dict.plugin import ItemDictPlugin, ITEM_DICT_PLUGIN_NAME

    def pytest_collection_finish(session):
        plugin: ItemDictPlugin = session.config.pluginmanager.get_plugin(name=ITEM_DICT_PLUGIN_NAME)
        if plugin:
            collect_hierarchy = plugin.collect_dict.hierarchy   # populated after collection
            total_tests = plugin.collect_dict._total_tests      # recursive count of all tests

    def pytest_sessionfinish(session, exitstatus):
        plugin: ItemDictPlugin = session.config.pluginmanager.get_plugin(name=ITEM_DICT_PLUGIN_NAME)
        if plugin:
            test_hierarchy = plugin.test_dict.hierarchy         # outcomes, durations, @counts

**Hierarchy structure**

Given ``suites/it/test_login.py::TestLogin::test_valid_credentials``, the hierarchy is::

    {
        "suites": {
            "@tests": 1,
            "it": {
                "@tests": 1,
                "test_login.py": {
                    "@tests": 1,
                    "TestLogin": {
                        "@tests": 1,
                        "test_valid_credentials": {}
                    }
                }
            }
        }
    }

After a full run with ``set_test_hierarchy_dict_outcomes = true``, parent nodes gain ``@counts``::

    "test_login.py": {
        "@counts": {"passed": 1, "failed": 0, "skipped": 0, "unexecuted": 0, "executed": 1, "total": 1},
        "TestLogin": {
            "test_valid_credentials": {"@outcome": "passed"}
        }
    }

**Writing reports from conftest.py**

.. code-block:: python

    # conftest.py
    import json
    from copy import deepcopy
    from pathlib import Path
    from pytest import Session
    from pytest_item_dict.plugin import ItemDictPlugin, ITEM_DICT_PLUGIN_NAME

    def pytest_collection_finish(session: Session) -> None:
        plugin: ItemDictPlugin = session.config.pluginmanager.get_plugin(name=ITEM_DICT_PLUGIN_NAME)
        if plugin:
            Path("output/collect_hierarchy.json").write_text(
                json.dumps(plugin.collect_dict.hierarchy, indent=2)
            )

    def pytest_sessionfinish(session: Session) -> None:
        plugin: ItemDictPlugin = session.config.pluginmanager.get_plugin(name=ITEM_DICT_PLUGIN_NAME)
        if plugin:
            Path("output/test_hierarchy.json").write_text(
                json.dumps(plugin.test_dict.hierarchy, indent=2)
            )

**pyproject.toml options**

.. code-block:: toml

    [tool.pytest.ini_options]
    create_item_dict                 = true   # enable/disable the plugin (default: true)
    set_collect_dict_markers         = false  # add @markers to collect_dict nodes
    set_test_dict_markers            = false  # add @markers to test_dict nodes
    set_test_dict_outcomes           = true   # record @outcome per test (default: true)
    set_test_dict_durations          = false  # record @duration per test
    update_dict_on_test              = true   # update test_dict after each test in real time
    set_test_dict_setup_teardown     = false  # record setup/teardown phase outcomes
    set_test_hierarchy_dict_outcomes = false  # bubble @counts up through all parent nodes
    set_test_hierarchy_dict_durations= false  # bubble @total_duration up through all parent nodes

**Counting tests**

``collect_dict.count_tests()`` is called automatically at the end of collection.
It sets ``@tests`` on every non-leaf node and caches the total in ``_total_tests``:

.. code-block:: python

    plugin.collect_dict._total_tests               # total collected (int)
    plugin.collect_dict.hierarchy["suite"]["@tests"]  # count scoped to a subtree

You can also call it manually on any subtree:

.. code-block:: python

    subtree = plugin.collect_dict.hierarchy["suites"]["it"]
    count = plugin.collect_dict.count_tests(node=subtree)

Contributing
------------
Contributions are very welcome. Tests can be run with `tox`_, please ensure
the coverage at least stays the same before you submit a pull request.

License
-------
Dual License:

Distributed under the terms of both the `BSD-3`_ AND `Mozilla Public License 2.0`_ licenses.

"pytest-item-dict" is free and open source software


Issues
------

If you encounter any problems, please `file an issue`_ along with a detailed description.

.. _`Cookiecutter`: https://github.com/audreyr/cookiecutter
.. _`@hackebrot`: https://github.com/hackebrot
.. _`MIT`: https://opensource.org/licenses/MIT
.. _`BSD-3`: https://opensource.org/licenses/BSD-3-Clause
.. _`GNU GPL v3.0`: https://www.gnu.org/licenses/gpl-3.0.txt
.. _`Apache Software License 2.0`: https://www.apache.org/licenses/LICENSE-2.0
.. _`Mozilla Public License 2.0`: https://opensource.org/license/mpl-2-0
.. _`cookiecutter-pytest-plugin`: https://github.com/pytest-dev/cookiecutter-pytest-plugin
.. _`pytest-collect-formatter`: https://github.com/LaserPhaser/pytest-collect-formatter
.. _`file an issue`: https://github.com/anogowski/pytest-item-dict/issues
.. _`pytest`: https://github.com/pytest-dev/pytest
.. _`tox`: https://tox.readthedocs.io/en/latest/
.. _`pip`: https://pypi.org/project/pip/
.. _`PyPI`: https://pypi.org/project
