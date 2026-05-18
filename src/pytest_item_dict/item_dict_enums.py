#############################################
#	Dual License: BSD-3-Clause AND MPL-2.0	#
#	Copyright (c) 2024, Adam Nogowski		#
#############################################
"""Enumeration types for the pytest-item-dict plugin.

This module defines :class:`INIOptions`, :class:`CollectTypes`, and
:class:`TestProperties`, which centralise every string constant used by the
plugin, eliminating hard-coded literals and making future refactors safer.

Attributes
----------
INIOptions : StrEnum
    Keys for pytest ini-file configuration options.
CollectTypes : StrEnum
    String names of pytest collector node types.
TestProperties : StrEnum
    Attribute names used to annotate :class:`pytest.Item` objects and
    hierarchy dict nodes during a test run.
"""

from enum import StrEnum


class INIOptions(StrEnum):
	"""Pytest ini-file option keys recognised by the plugin.

	Attributes
	----------
	CREATE_ITEM_DICT : str
	    Master switch; when ``False`` the plugin is not registered.
	UPDATE_DICT_ON_TEST : str
	    Update the test-outcome hierarchy dict after every individual test.
	SET_COLLECT_MARKERS : str
	    Persist pytest markers into the *collection* hierarchy dict.
	SET_TEST_OUTCOMES : str
	    Persist test outcomes (passed/failed/skipped/unexecuted) into the
	    test-run hierarchy dict.
	SET_TEST_DURATIONS : str
	    Persist individual and aggregated durations into the test-run dict.
	SET_TEST_MARKERS : str
	    Persist pytest markers into the *test-run* hierarchy dict.
	"""

	CREATE_ITEM_DICT = "create_item_dict"
	UPDATE_DICT_ON_TEST = "update_dict_on_test"
	SET_COLLECT_MARKERS = "set_collect_dict_markers"
	SET_TEST_OUTCOMES = "set_test_dict_outcomes"
	SET_TEST_DURATIONS = "set_test_dict_durations"
	SET_TEST_MARKERS = "set_test_dict_markers"


class CollectTypes(StrEnum):
	"""String representations of pytest collector node ``type().__name__`` values.

	Attributes
	----------
	DIR : str
	    A plain directory node (``pytest.Dir``).
	PACKAGE : str
	    A Python package directory (``pytest.Package``).
	MODULE : str
	    A ``.py`` test module (``pytest.Module``).
	CLASS : str
	    A test class (``pytest.Class``).
	TEST : str
	    An individual test function/method (``pytest.Function``).
	"""

	DIR = "Dir"
	PACKAGE = "Package"
	MODULE = "Module"
	CLASS = "Class"
	TEST = "Test"


class TestProperties(StrEnum):
	"""Attribute names stored on :class:`pytest.Item` objects and in hierarchy dicts.

	Keys prefixed with ``@`` in the hierarchy dict correspond to these values
	via :meth:`~pytest_item_dict.collect_dict.CollectionDict.set_attribute`.

	Attributes
	----------
	OUTCOME : str
	    Test execution result: ``"passed"``, ``"failed"``, ``"skipped"``,
	    or ``"unexecuted"``.
	NODEID : str
	    Full pytest node identifier (e.g. ``suite/test_mod.py::Cls::test_fn``).
	NAME : str
	    Short test name without path information.
	ORIGINAL_NAME : str
	    Original test name before any parametrize renaming.
	MARKERS : str
	    List of marker names attached to the test.
	DURATION : str
	    Individual test duration in seconds (``float``).
	COUNTS : str
	    Aggregated outcome counts at a parent node; stored as
	    ``{"passed": N, "failed": N, "skipped": N, "unexecuted": N, "total": N}``.
	TOTAL_DURATION : str
	    Aggregated sum of child-node durations at a parent node (``float``, seconds).
	"""

	OUTCOME = "outcome"
	NODEID = "nodeid"
	NAME = "name"
	ORIGINAL_NAME = "original_name"
	MARKERS = "markers"
	DURATION = "duration"
	COUNTS = "counts"
	TOTAL_DURATION = "total_duration"
