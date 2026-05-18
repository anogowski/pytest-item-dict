#############################################
#	Dual License: BSD-3-Clause AND MPL-2.0	#
#	Copyright (c) 2024, Adam Nogowski		#
#############################################

import json
import pytest

from pytest_item_dict.collect_dict import CollectionDict
from pytest_item_dict.item_dict_enums import INIOptions

# ---------------------------------------------------------------------------
# Shared conftest snippets written into pytester sessions
# ---------------------------------------------------------------------------

_WRITE_COLLECT = """
import json
from pathlib import Path
from pytest_item_dict.plugin import ITEM_DICT_PLUGIN_NAME

def pytest_collection_finish(session):
	plugin = session.config.pluginmanager.get_plugin(name=ITEM_DICT_PLUGIN_NAME)
	if plugin:
		Path("collect.json").write_text(json.dumps(plugin.collect_dict.hierarchy))
"""

_WRITE_TEST = """
import json
from pathlib import Path
from pytest_item_dict.plugin import ITEM_DICT_PLUGIN_NAME

def pytest_sessionfinish(session, exitstatus):
	plugin = session.config.pluginmanager.get_plugin(name=ITEM_DICT_PLUGIN_NAME)
	if plugin:
		Path("test.json").write_text(json.dumps(plugin.test_dict.hierarchy))
"""

_WRITE_BOTH = _WRITE_COLLECT + _WRITE_TEST

# ---------------------------------------------------------------------------
# Unit tests – CollectionDict.get_key_path (no subprocess needed)
# ---------------------------------------------------------------------------


class TestGetKeyPath:
	"""Direct unit tests for CollectionDict.get_key_path."""

	@pytest.fixture()
	def cdict(self, pytester):
		pytester.makeini("[pytest]")
		config = pytester.parseconfig()
		return CollectionDict(config=config)

	def test_flat_file_and_function(self, cdict):
		assert cdict.get_key_path("test_foo.py::test_bar") == ["test_foo.py", "test_bar"]

	def test_nested_dir(self, cdict):
		assert cdict.get_key_path("a/b/test_foo.py::test_bar") == ["a", "b", "test_foo.py", "test_bar"]

	def test_class_nodeid(self, cdict):
		assert cdict.get_key_path("test_foo.py::MyClass::test_bar") == ["test_foo.py", "MyClass", "test_bar"]

	def test_file_only(self, cdict):
		assert cdict.get_key_path("test_foo.py") == ["test_foo.py"]

	def test_deep_class_nodeid(self, cdict):
		result = cdict.get_key_path("sub/test_foo.py::MyClass::test_bar")
		assert result == ["sub", "test_foo.py", "MyClass", "test_bar"]


# ---------------------------------------------------------------------------
# Plugin registration
# ---------------------------------------------------------------------------


def test_plugin_registered_by_default(pytester):
	pytester.makepyfile("""
		def test_pass():
			pass
	""")
	pytester.makeconftest("""
		from pytest_item_dict.plugin import ITEM_DICT_PLUGIN_NAME
		def pytest_collection_finish(session):
			plugin = session.config.pluginmanager.get_plugin(name=ITEM_DICT_PLUGIN_NAME)
			assert plugin is not None
	""")
	result = pytester.runpytest()
	assert result.ret == 0


def test_plugin_disabled_by_ini(pytester):
	pytester.makeini("""
		[pytest]
		create_item_dict = false
	""")
	pytester.makepyfile("""
		def test_pass():
			pass
	""")
	pytester.makeconftest("""
		from pytest_item_dict.plugin import ITEM_DICT_PLUGIN_NAME
		def pytest_collection_finish(session):
			plugin = session.config.pluginmanager.get_plugin(name=ITEM_DICT_PLUGIN_NAME)
			assert plugin is None
	""")
	result = pytester.runpytest()
	assert result.ret == 0


# ---------------------------------------------------------------------------
# INI options
# ---------------------------------------------------------------------------


def test_ini_options_in_help(pytester):
	result = pytester.runpytest("--help")
	result.stdout.fnmatch_lines([
	    f"*{INIOptions.CREATE_ITEM_DICT}*",
	    f"*{INIOptions.SET_COLLECT_MARKERS}*",
	    f"*{INIOptions.SET_TEST_MARKERS}*",
	    f"*{INIOptions.SET_TEST_OUTCOMES}*",
	    f"*{INIOptions.UPDATE_DICT_ON_TEST}*",
	    f"*{INIOptions.SET_TEST_DURATIONS}*",
	    f"*{INIOptions.SET_TEST_HIERARCHY_OUTCOMES}*",
	    f"*{INIOptions.SET_TEST_HIERARCHY_DURATIONS}*",
	    f"*{INIOptions.SET_SETUP_TEARDOWN}*",
	])


# ---------------------------------------------------------------------------
# Test-dict hierarchy – outcomes (default: enabled)
# ---------------------------------------------------------------------------


def test_outcome_passed(pytester):
	pytester.makeconftest(_WRITE_TEST)
	pytester.makepyfile(test_outcomes="""
		def test_will_pass():
			assert True
	""")
	result = pytester.runpytest()
	assert result.ret == 0
	h = json.loads((pytester.path / "test.json").read_text())
	assert h["test_outcomes.py"]["test_will_pass"]["@outcome"] == "passed"


def test_outcome_failed(pytester):
	pytester.makeconftest(_WRITE_TEST)
	pytester.makepyfile(test_outcomes="""
		def test_will_fail():
			assert False
	""")
	result = pytester.runpytest()
	assert result.ret != 0
	h = json.loads((pytester.path / "test.json").read_text())
	assert h["test_outcomes.py"]["test_will_fail"]["@outcome"] == "failed"


def test_outcome_skipped(pytester):
	pytester.makeconftest(_WRITE_TEST)
	pytester.makepyfile(test_outcomes="""
		import pytest

		def test_will_skip():
			pytest.skip("skipped inline")
	""")
	result = pytester.runpytest()
	assert result.ret == 0
	h = json.loads((pytester.path / "test.json").read_text())
	assert h["test_outcomes.py"]["test_will_skip"]["@outcome"] == "skipped"


def test_unexecuted_outcome_set_on_collection(pytester):
	"""test_dict hierarchy has 'unexecuted' for all tests immediately after collection."""
	pytester.makeconftest(_WRITE_COLLECT + """
import json
from pathlib import Path
from pytest_item_dict.plugin import ITEM_DICT_PLUGIN_NAME

def pytest_collection_finish(session):
	plugin = session.config.pluginmanager.get_plugin(name=ITEM_DICT_PLUGIN_NAME)
	if plugin:
		Path("test_pre.json").write_text(json.dumps(plugin.test_dict.hierarchy))
""")
	pytester.makepyfile(test_pre="""
		def test_something():
			pass
	""")
	pytester.runpytest()
	h = json.loads((pytester.path / "test_pre.json").read_text())
	assert h["test_pre.py"]["test_something"]["@outcome"] == "unexecuted"


def test_outcomes_disabled(pytester):
	pytester.makeini("""
		[pytest]
		set_test_dict_outcomes = false
	""")
	pytester.makeconftest(_WRITE_TEST)
	pytester.makepyfile(test_no_outcomes="""
		def test_pass():
			pass
	""")
	pytester.runpytest()
	h = json.loads((pytester.path / "test.json").read_text())
	# with outcomes disabled, @outcome key must not be present
	assert "@outcome" not in h.get("test_no_outcomes.py", {}).get("test_pass", {})


def test_multiple_outcomes_in_same_file(pytester):
	pytester.makeconftest(_WRITE_TEST)
	pytester.makepyfile(test_multi="""
		def test_a():
			assert True
		def test_b():
			assert False
	""")
	pytester.runpytest()
	h = json.loads((pytester.path / "test.json").read_text())
	assert h["test_multi.py"]["test_a"]["@outcome"] == "passed"
	assert h["test_multi.py"]["test_b"]["@outcome"] == "failed"


# ---------------------------------------------------------------------------
# Test-dict hierarchy – class-based tests
# ---------------------------------------------------------------------------


def test_outcome_class_based_tests(pytester):
	pytester.makeconftest(_WRITE_TEST)
	pytester.makepyfile(test_cls="""
		class TestGroup:
			def test_alpha(self):
				assert True
			def test_beta(self):
				assert False
	""")
	pytester.runpytest()
	h = json.loads((pytester.path / "test.json").read_text())
	assert h["test_cls.py"]["TestGroup"]["test_alpha"]["@outcome"] == "passed"
	assert h["test_cls.py"]["TestGroup"]["test_beta"]["@outcome"] == "failed"


def test_outcome_nested_directory(pytester):
	pytester.mkpydir("sub")
	(pytester.path / "sub" / "test_nested.py").write_text("def test_nested_one():\n\tassert True\n")
	pytester.makeconftest(_WRITE_TEST)
	pytester.runpytest()
	h = json.loads((pytester.path / "test.json").read_text())
	assert h["sub"]["test_nested.py"]["test_nested_one"]["@outcome"] == "passed"


# ---------------------------------------------------------------------------
# Collect-dict hierarchy – markers
# ---------------------------------------------------------------------------


def test_collect_markers_set(pytester):
	pytester.makeini("""
		[pytest]
		set_collect_dict_markers = true
		markers = smoke: smoke tests
	""")
	pytester.makeconftest(_WRITE_COLLECT)
	pytester.makepyfile(test_marked="""
		import pytest

		@pytest.mark.smoke
		def test_with_marker():
			pass
	""")
	pytester.runpytest()
	h = json.loads((pytester.path / "collect.json").read_text())
	assert "smoke" in h["test_marked.py"]["test_with_marker"]["@markers"]


def test_collect_markers_not_set_by_default(pytester):
	pytester.makeconftest(_WRITE_COLLECT + """
import json
from pathlib import Path
from pytest_item_dict.plugin import ITEM_DICT_PLUGIN_NAME

# override: capture AFTER collection but BEFORE run_ini_options completes
# we capture test_dict here which is a deepcopy taken before markers are applied
def pytest_sessionfinish(session, exitstatus):
	plugin = session.config.pluginmanager.get_plugin(name=ITEM_DICT_PLUGIN_NAME)
	if plugin:
		Path("collect_no_markers.json").write_text(json.dumps(plugin.collect_dict.hierarchy))
""")
	pytester.makeini("""
		[pytest]
		markers = smoke: smoke tests
	""")
	pytester.makepyfile(test_unmarked="""
		import pytest

		@pytest.mark.smoke
		def test_with_marker():
			pass
	""")
	pytester.runpytest()
	h = json.loads((pytester.path / "collect_no_markers.json").read_text())
	# @markers should NOT be present when set_collect_dict_markers = false (default)
	node = h.get("test_unmarked.py", {}).get("test_with_marker", {})
	assert "@markers" not in node


def test_test_dict_markers_set(pytester):
	pytester.makeini("""
		[pytest]
		set_test_dict_markers = true
		markers = fast: fast tests
	""")
	pytester.makeconftest(_WRITE_TEST)
	pytester.makepyfile(test_tmarked="""
		import pytest

		@pytest.mark.fast
		def test_fast():
			pass
	""")
	pytester.runpytest()
	h = json.loads((pytester.path / "test.json").read_text())
	assert "fast" in h["test_tmarked.py"]["test_fast"]["@markers"]


# ---------------------------------------------------------------------------
# Test-dict hierarchy – durations
# ---------------------------------------------------------------------------


def test_durations_set(pytester):
	pytester.makeini("""
		[pytest]
		set_test_dict_durations = true
	""")
	pytester.makeconftest(_WRITE_TEST)
	pytester.makepyfile(test_dur="""
		def test_something():
			pass
	""")
	pytester.runpytest()
	h = json.loads((pytester.path / "test.json").read_text())
	assert "@duration" in h["test_dur.py"]["test_something"]


def test_durations_not_set_by_default(pytester):
	pytester.makeconftest(_WRITE_TEST)
	pytester.makepyfile(test_nodur="""
		def test_something():
			pass
	""")
	pytester.runpytest()
	h = json.loads((pytester.path / "test.json").read_text())
	assert "@duration" not in h["test_nodur.py"]["test_something"]


# ---------------------------------------------------------------------------
# Aggregation – proving the math is correct at every hierarchy level
# ---------------------------------------------------------------------------


class TestAggregation:
	"""Verify that ``aggregate_counts`` bubbles metrics up through all levels.

	Each test in this class is a targeted mathematical assertion: given N tests
	with known outcomes at a particular hierarchy level, the ``@counts`` stored
	at the parent node must exactly match the expected breakdown.

	Attributes
	----------
	_WRITE_TEST : str
		Shared conftest snippet (module-level constant) that serialises the
		test-dict hierarchy to ``test.json`` in the pytester temp directory.
	"""

	def test_counts_at_module_level(self, pytester):
		"""``@counts`` at module level sums all functions in that file.

		Given two passing tests and one failing test in ``test_math.py``, the
		module node ``test_math.py`` must expose::

			"@counts": {"passed": 2, "failed": 1, "skipped": 0,
						"unexecuted": 0, "total": 3}
		"""
		pytester.makeini("""
			[pytest]
			set_test_hierarchy_dict_outcomes = true
		""")
		pytester.makeconftest(_WRITE_TEST)
		pytester.makepyfile(test_math="""
			def test_pass_a():
				pass
			def test_pass_b():
				pass
			def test_fail():
				assert False
		""")
		pytester.runpytest()
		h = json.loads((pytester.path / "test.json").read_text())
		counts = h["test_math.py"]["@counts"]
		assert counts["passed"] == 2
		assert counts["failed"] == 1
		assert counts["skipped"] == 0
		assert counts["unexecuted"] == 0
		assert counts["total"] == 3

	def test_counts_at_class_level(self, pytester):
		"""``@counts`` at class level sums only the tests inside that class.

		Given one pass, one fail, and one inline-skip inside ``TestGroup``,
		the class node must expose the correct breakdown without including
		any tests from sibling classes or module-level functions.
		"""
		pytester.makeini("""
			[pytest]
			set_test_hierarchy_dict_outcomes = true
		""")
		pytester.makeconftest(_WRITE_TEST)
		pytester.makepyfile(test_cls="""
			import pytest

			class TestGroup:
				def test_pass(self):
					pass
				def test_fail(self):
					assert False
				def test_skip(self):
					pytest.skip("skipped inline")
		""")
		pytester.runpytest()
		h = json.loads((pytester.path / "test.json").read_text())
		counts = h["test_cls.py"]["TestGroup"]["@counts"]
		assert counts["passed"] == 1
		assert counts["failed"] == 1
		assert counts["skipped"] == 1
		assert counts["total"] == 3

	def test_counts_at_folder_level(self, pytester):
		"""``@counts`` at folder level spans all files in that directory.

		Two sibling test files — one passing, one failing — must produce
		a folder-level ``@counts`` that sums across both files::

			folder/@counts == {"passed": 1, "failed": 1, "total": 2, ...}
		"""
		pytester.makeini("""
			[pytest]
			set_test_hierarchy_dict_outcomes = true
		""")
		pytester.mkpydir("suite")
		(pytester.path / "suite" / "test_a.py").write_text("def test_pass():\n\tpass\n")
		(pytester.path / "suite" / "test_b.py").write_text("def test_fail():\n\tassert False\n")
		pytester.makeconftest(_WRITE_TEST)
		pytester.runpytest()
		h = json.loads((pytester.path / "test.json").read_text())
		counts = h["suite"]["@counts"]
		assert counts["passed"] == 1
		assert counts["failed"] == 1
		assert counts["total"] == 2

	def test_counts_bubble_up_through_all_levels(self, pytester):
		"""Counts flow correctly from leaf → class → module → folder.

		Mathematical invariant: the count at every ancestor must equal the
		sum of all leaf outcomes under it.  This test checks that all three
		ancestor levels carry identical totals when there is only one
		module/class in scope.
		"""
		pytester.makeini("""
			[pytest]
			set_test_hierarchy_dict_outcomes = true
		""")
		pytester.mkpydir("deep")
		(pytester.path / "deep" / "test_nested.py").write_text("class TestClass:\n"
		                                                       "\tdef test_pass(self):\n\t\tpass\n"
		                                                       "\tdef test_fail(self):\n\t\tassert False\n")
		pytester.makeconftest(_WRITE_TEST)
		pytester.runpytest()
		h = json.loads((pytester.path / "test.json").read_text())

		expected = {"passed": 1, "failed": 1, "total": 2}
		for level_name, node in [
		    ("class", h["deep"]["test_nested.py"]["TestClass"]["@counts"]),
		    ("module", h["deep"]["test_nested.py"]["@counts"]),
		    ("folder", h["deep"]["@counts"]),
		]:
			for key, val in expected.items():
				assert node[key] == val, (f"Bubble-up failure at {level_name} level: "
				                          f"expected {key}={val}, got {node[key]}")

	def test_counts_parametrized_each_variant_is_leaf(self, pytester):
		"""Each parametrized variant counts as a separate leaf test.

		Three parameter values on a single function must produce a module-level
		``@counts["total"]`` of 3, with all three reported as "passed".
		"""
		pytester.makeini("""
			[pytest]
			set_test_hierarchy_dict_outcomes = true
		""")
		pytester.makeconftest(_WRITE_TEST)
		pytester.makepyfile(test_params="""
			import pytest

			@pytest.mark.parametrize("x", [1, 2, 3])
			def test_positive(x):
				assert x > 0
		""")
		pytester.runpytest()
		h = json.loads((pytester.path / "test.json").read_text())
		counts = h["test_params.py"]["@counts"]
		assert counts["passed"] == 3
		assert counts["total"] == 3

	def test_counts_mixed_classes_and_functions(self, pytester):
		"""Module ``@counts`` sums class-based and standalone functions.

		Given one standalone pass, one class with a pass and a fail, the
		module total must be 3 (2 passed, 1 failed).
		"""
		pytester.makeini("""
			[pytest]
			set_test_hierarchy_dict_outcomes = true
		""")
		pytester.makeconftest(_WRITE_TEST)
		pytester.makepyfile(test_mixed="""
			def test_standalone():
				pass

			class TestGroup:
				def test_in_class_pass(self):
					pass
				def test_in_class_fail(self):
					assert False
		""")
		pytester.runpytest()
		h = json.loads((pytester.path / "test.json").read_text())
		module_counts = h["test_mixed.py"]["@counts"]
		assert module_counts["passed"] == 2
		assert module_counts["failed"] == 1
		assert module_counts["total"] == 3
		# Standalone function is a direct leaf of the module; class is a subtree.
		class_counts = h["test_mixed.py"]["TestGroup"]["@counts"]
		assert class_counts["passed"] == 1
		assert class_counts["failed"] == 1
		assert class_counts["total"] == 2

	def test_counts_no_double_counting(self, pytester):
		"""Leaf outcomes are the sole source of truth; parent sums never inflate.

		Two sibling classes each containing two tests must produce a module
		total of exactly 4 (not 8 or any other inflated number).
		"""
		pytester.makeini("""
			[pytest]
			set_test_hierarchy_dict_outcomes = true
		""")
		pytester.makeconftest(_WRITE_TEST)
		pytester.makepyfile(test_siblings="""
			class TestA:
				def test_one(self):
					pass
				def test_two(self):
					pass

			class TestB:
				def test_three(self):
					assert False
				def test_four(self):
					assert False
		""")
		pytester.runpytest()
		h = json.loads((pytester.path / "test.json").read_text())
		module_counts = h["test_siblings.py"]["@counts"]
		assert module_counts["passed"] == 2
		assert module_counts["failed"] == 2
		assert module_counts["total"] == 4  # not 8 — no double-counting

	def test_duration_aggregated_at_module_level(self, pytester):
		"""``@total_duration`` at module level equals the sum of leaf durations.

		With ``set_test_dict_durations = true``, every leaf stores ``@duration``
		(float seconds) and every parent stores ``@total_duration``.  The
		module's ``@total_duration`` must exactly equal the arithmetic sum of
		its children's ``@duration`` values.
		"""
		pytester.makeini("""
			[pytest]
			set_test_dict_durations = true
			set_test_hierarchy_dict_durations = true
		""")
		pytester.makeconftest(_WRITE_TEST)
		pytester.makepyfile(test_dur="""
			def test_one():
				pass
			def test_two():
				pass
		""")
		pytester.runpytest()
		h = json.loads((pytester.path / "test.json").read_text())
		leaf_one: float = h["test_dur.py"]["test_one"]["@duration"]
		leaf_two: float = h["test_dur.py"]["test_two"]["@duration"]
		module_total: float = h["test_dur.py"]["@total_duration"]
		assert isinstance(leaf_one, float)
		assert isinstance(module_total, float)
		assert abs(module_total - (leaf_one + leaf_two)) < 1e-9

	def test_duration_not_aggregated_when_disabled(self, pytester):
		"""``@total_duration`` must be absent when durations are not enabled."""
		pytester.makeconftest(_WRITE_TEST)
		pytester.makepyfile(test_nodur="""
			def test_one():
				pass
		""")
		pytester.runpytest()
		h = json.loads((pytester.path / "test.json").read_text())
		assert "@total_duration" not in h.get("test_nodur.py", {})

	# ------------------------------------------------------------------
	# Hierarchy options – outcomes
	# ------------------------------------------------------------------

	def test_hierarchy_counts_absent_by_default(self, pytester):
		"""``@counts`` must not appear at parent nodes unless explicitly enabled.

		The ``set_test_hierarchy_dict_outcomes`` ini option defaults to
		``false``; without it ``aggregate_counts`` is never called and no
		``@counts`` key should appear anywhere in the hierarchy.
		"""
		pytester.makeconftest(_WRITE_TEST)
		pytester.makepyfile(test_no_counts="""
			def test_pass():
				pass
		""")
		pytester.runpytest()
		h = json.loads((pytester.path / "test.json").read_text())
		assert "@counts" not in h.get("test_no_counts.py", {})

	def test_hierarchy_counts_enabled(self, pytester):
		"""``@counts`` appears at parent nodes when the option is enabled."""
		pytester.makeini("""
			[pytest]
			set_test_hierarchy_dict_outcomes = true
		""")
		pytester.makeconftest(_WRITE_TEST)
		pytester.makepyfile(test_with_counts="""
			def test_pass():
				pass
			def test_fail():
				assert False
		""")
		pytester.runpytest()
		h = json.loads((pytester.path / "test.json").read_text())
		counts = h["test_with_counts.py"]["@counts"]
		assert counts["passed"] == 1
		assert counts["failed"] == 1
		assert counts["total"] == 2

	def test_executed_count_in_hierarchy_counts(self, pytester):
		"""``@counts["executed"]`` equals ``total - unexecuted``.

		With two run tests and one collected-but-unexecuted test (simulated by
		checking the hierarchy mid-session), the ``executed`` field must equal
		``total - unexecuted`` after the run.

		Here we simply verify that ``executed`` equals ``total`` when every
		collected test actually ran (zero unexecuted).
		"""
		pytester.makeini("""
			[pytest]
			set_test_hierarchy_dict_outcomes = true
		""")
		pytester.makeconftest(_WRITE_TEST)
		pytester.makepyfile(test_exec="""
			def test_one():
				pass
			def test_two():
				pass
		""")
		pytester.runpytest()
		h = json.loads((pytester.path / "test.json").read_text())
		counts = h["test_exec.py"]["@counts"]
		assert counts["executed"] == counts["total"] - counts["unexecuted"]
		assert counts["executed"] == 2

	# ------------------------------------------------------------------
	# Hierarchy options – durations
	# ------------------------------------------------------------------

	def test_hierarchy_durations_absent_by_default(self, pytester):
		"""``@total_duration`` must not appear unless the hierarchy option is set.

		``set_test_hierarchy_dict_durations`` defaults to ``false``, so even
		when ``set_test_dict_durations`` is ``true`` the parent-level
		``@total_duration`` key must be absent when the hierarchy option is
		off.
		"""
		pytester.makeini("""
			[pytest]
			set_test_dict_durations = true
		""")
		pytester.makeconftest(_WRITE_TEST)
		pytester.makepyfile(test_no_hier_dur="""
			def test_one():
				pass
		""")
		pytester.runpytest()
		h = json.loads((pytester.path / "test.json").read_text())
		assert "@total_duration" not in h.get("test_no_hier_dur.py", {})

	def test_hierarchy_durations_enabled(self, pytester):
		"""``@total_duration`` appears at parent nodes when the option is enabled."""
		pytester.makeini("""
			[pytest]
			set_test_dict_durations = true
			set_test_hierarchy_dict_durations = true
		""")
		pytester.makeconftest(_WRITE_TEST)
		pytester.makepyfile(test_hier_dur="""
			def test_one():
				pass
		""")
		pytester.runpytest()
		h = json.loads((pytester.path / "test.json").read_text())
		assert "@total_duration" in h["test_hier_dur.py"]
		assert isinstance(h["test_hier_dur.py"]["@total_duration"], float)


# ---------------------------------------------------------------------------
# Setup / teardown reporting
# ---------------------------------------------------------------------------

_SETUP_TEARDOWN_INI = """
[pytest]
set_test_dict_setup_teardown = true
"""


class TestSetupTeardown:
	"""Verify optional setup/teardown phase reporting.

	When ``set_test_dict_setup_teardown = true`` the test-dict hierarchy gains
	extra nodes (``setup_method``, ``teardown_method``, ``setup_function``,
	``teardown_function``, ``setup_class``, ``teardown_class``) that record
	the phase outcome but are *excluded* from ``@counts`` aggregation.
	"""

	def test_not_present_by_default(self, pytester):
		"""setup_method / teardown_method absent unless the option is enabled."""
		pytester.makeconftest(_WRITE_TEST)
		pytester.makepyfile(test_default="""
			class TestG:
				def test_one(self):
					pass
		""")
		pytester.runpytest()
		h = json.loads((pytester.path / "test.json").read_text())
		test_node = h["test_default.py"]["TestG"]["test_one"]
		assert "setup_method" not in test_node
		assert "teardown_method" not in test_node

	def test_setup_method_present_for_class_test(self, pytester):
		"""setup_method and teardown_method appear inside each class-based test."""
		pytester.makeini(_SETUP_TEARDOWN_INI)
		pytester.makeconftest(_WRITE_TEST)
		pytester.makepyfile(test_cls_setup="""
			class TestG:
				def test_one(self):
					pass
		""")
		pytester.runpytest()
		h = json.loads((pytester.path / "test.json").read_text())
		test_node = h["test_cls_setup.py"]["TestG"]["test_one"]
		assert "setup_method" in test_node
		assert "teardown_method" in test_node
		assert test_node["setup_method"]["@outcome"] == "passed"
		assert test_node["teardown_method"]["@outcome"] == "passed"

	def test_setup_function_present_for_module_level_test(self, pytester):
		"""setup_function / teardown_function appear inside module-level functions."""
		pytester.makeini(_SETUP_TEARDOWN_INI)
		pytester.makeconftest(_WRITE_TEST)
		pytester.makepyfile(test_fn_setup="""
			def test_standalone():
				pass
		""")
		pytester.runpytest()
		h = json.loads((pytester.path / "test.json").read_text())
		test_node = h["test_fn_setup.py"]["test_standalone"]
		assert "setup_function" in test_node
		assert "teardown_function" in test_node
		assert test_node["setup_function"]["@outcome"] == "passed"
		assert test_node["teardown_function"]["@outcome"] == "passed"

	def test_setup_class_at_class_node(self, pytester):
		"""setup_class appears at the class node when the class defines it."""
		pytester.makeini(_SETUP_TEARDOWN_INI)
		pytester.makeconftest(_WRITE_TEST)
		pytester.makepyfile(test_sc="""
			class TestWithSetupClass:
				@classmethod
				def setup_class(cls):
					pass

				@classmethod
				def teardown_class(cls):
					pass

				def test_one(self):
					pass

				def test_two(self):
					pass
		""")
		pytester.runpytest()
		h = json.loads((pytester.path / "test.json").read_text())
		class_node = h["test_sc.py"]["TestWithSetupClass"]
		assert "setup_class" in class_node
		assert "teardown_class" in class_node
		assert class_node["setup_class"]["@outcome"] == "passed"
		assert class_node["teardown_class"]["@outcome"] == "passed"
		# Test nodes are still siblings of setup_class / teardown_class
		assert "test_one" in class_node
		assert "test_two" in class_node

	def test_setup_class_absent_when_class_lacks_it(self, pytester):
		"""setup_class / teardown_class absent if the class does not define them."""
		pytester.makeini(_SETUP_TEARDOWN_INI)
		pytester.makeconftest(_WRITE_TEST)
		pytester.makepyfile(test_nosc="""
			class TestNoSetupClass:
				def test_one(self):
					pass
		""")
		pytester.runpytest()
		h = json.loads((pytester.path / "test.json").read_text())
		class_node = h["test_nosc.py"]["TestNoSetupClass"]
		assert "setup_class" not in class_node
		assert "teardown_class" not in class_node

	def test_setup_failure_recorded(self, pytester):
		"""A failing setup_method shows 'failed' for the setup_method outcome."""
		pytester.makeini(_SETUP_TEARDOWN_INI)
		pytester.makeconftest(_WRITE_TEST)
		pytester.makepyfile(test_setup_fail="""
			class TestG:
				def setup_method(self):
					raise RuntimeError("setup boom")

				def test_one(self):
					pass
		""")
		pytester.runpytest()
		h = json.loads((pytester.path / "test.json").read_text())
		test_node = h["test_setup_fail.py"]["TestG"]["test_one"]
		assert test_node["setup_method"]["@outcome"] == "failed"

	def test_teardown_failure_recorded(self, pytester):
		"""A failing teardown_method shows 'failed' for the teardown_method outcome."""
		pytester.makeini(_SETUP_TEARDOWN_INI)
		pytester.makeconftest(_WRITE_TEST)
		pytester.makepyfile(test_teardown_fail="""
			class TestG:
				def teardown_method(self):
					raise RuntimeError("teardown boom")

				def test_one(self):
					pass
		""")
		pytester.runpytest()
		h = json.loads((pytester.path / "test.json").read_text())
		test_node = h["test_teardown_fail.py"]["TestG"]["test_one"]
		assert test_node["teardown_method"]["@outcome"] == "failed"

	def test_setup_teardown_not_counted_in_hierarchy(self, pytester):
		"""setup_class, setup_method, teardown_method never count toward @counts.

		With two actual tests in a class that has setup_class, teardown_class,
		and setup_method / teardown_method defined, the class ``@counts``
		should reflect only the two test results (total=2) and not inflate
		due to the extra setup/teardown nodes.
		"""
		pytester.makeini("""
			[pytest]
			set_test_dict_setup_teardown = true
			set_test_hierarchy_dict_outcomes = true
		""")
		pytester.makeconftest(_WRITE_TEST)
		pytester.makepyfile(test_no_inflate="""
			class TestCounted:
				@classmethod
				def setup_class(cls):
					pass

				@classmethod
				def teardown_class(cls):
					pass

				def setup_method(self):
					pass

				def teardown_method(self):
					pass

				def test_a(self):
					pass

				def test_b(self):
					pass
		""")
		pytester.runpytest()
		h = json.loads((pytester.path / "test.json").read_text())
		counts = h["test_no_inflate.py"]["TestCounted"]["@counts"]
		assert counts["total"] == 2
		assert counts["passed"] == 2

	def test_setup_teardown_not_counted_for_functions(self, pytester):
		"""setup_function / teardown_function do not inflate module @counts."""
		pytester.makeini("""
			[pytest]
			set_test_dict_setup_teardown = true
			set_test_hierarchy_dict_outcomes = true
		""")
		pytester.makeconftest(_WRITE_TEST)
		pytester.makepyfile(test_fn_inflate="""
			def test_alpha():
				pass

			def test_beta():
				pass
		""")
		pytester.runpytest()
		h = json.loads((pytester.path / "test.json").read_text())
		counts = h["test_fn_inflate.py"]["@counts"]
		assert counts["total"] == 2
		assert counts["passed"] == 2
