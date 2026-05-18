================
pytest-item-dict
================

.. image:: https://img.shields.io/pypi/v/pytest-item-dict.svg
    :target: https://pypi.org/project/pytest-item-dict
    :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/pytest-item-dict.svg
    :target: https://pypi.org/project/pytest-item-dict
    :alt: Python versions

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

  * ``collect_dict`` — pure structure populated after collection, with optional marker annotations
  * ``test_dict`` — populated incrementally during the run; records outcomes, durations, markers, and aggregated ``@counts``

* Every parent node automatically receives a ``@counts`` dict that sums the outcomes of all leaf tests beneath it (``passed``, ``failed``, ``skipped``, ``unexecuted``, ``executed``, ``total``) and a ``@total_duration`` float
* Configurable via ``pytest.ini`` / ``pyproject.toml`` options:

  * ``create_item_dict`` — enable/disable the plugin entirely (default: ``true``)
  * ``set_collect_dict_markers`` — annotate ``collect_dict`` nodes with marker names (default: ``false``)
  * ``set_test_dict_markers`` — annotate ``test_dict`` nodes with marker names (default: ``false``)
  * ``set_test_dict_outcomes`` — record ``@outcome`` on each test node (default: ``true``)
  * ``set_test_dict_durations`` — record ``@duration`` per test and ``@total_duration`` on parent nodes (default: ``false``)
  * ``update_dict_on_test`` — update ``test_dict`` after every individual test in real-time (default: ``true``)
  * ``set_test_dict_setup_teardown`` — record setup/teardown phase outcomes as separate nodes in ``test_dict`` (default: ``false``)

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

* TODO

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
