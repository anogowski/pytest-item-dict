#############################################
#	Dual License: BSD-3-Clause AND MPL-2.0	#
#	Copyright (c) 2024, Adam Nogowski		#
#############################################
"""Pytest plugin entry point for pytest-item-dict.

This module registers :class:`ItemDictPlugin` with pytest's plugin manager,
wires up the relevant hooks, and exposes two public objects:

* ``plugin.collect_dict`` — a :class:`~pytest_item_dict.collect_dict.CollectionDict`
  populated after the collection phase.
* ``plugin.test_dict`` — a :class:`~pytest_item_dict.test_dict.TestDict`
  populated incrementally during the run and finalised (with aggregated
  counts) at session end.

Module-level helpers :func:`write_json_file` and :func:`write_xml_file`
can serialise either hierarchy to disk on demand.

Attributes
----------
ITEM_DICT_PLUGIN_NAME : str
	Canonical name used to register and look up the plugin instance.
"""

from __future__ import annotations

from typing import Any, Final, Generator
import json
from pathlib import Path
from copy import deepcopy
import time

# Pip Includes
from data_to_xml.xml_converter import XMLConverter

# PyTest Includes
from pluggy import PluginManager
import pytest
from pytest import Item, Session, Config, Parser, CallInfo, TestReport

# Plugin Includes
from pytest_item_dict.item_dict_enums import INIOptions, CollectTypes, TestProperties
from pytest_item_dict.collect_dict import CollectionDict
from pytest_item_dict.test_dict import TestDict

ITEM_DICT_PLUGIN_NAME: Final[str] = "item_dict"
"""str : Canonical name used to register and look up the plugin instance."""

# def pytest_addhooks(pluginmanager: PluginManager) -> None:
# 	"""Register Pytest hooks

# 	Args:
# 		pluginmanager (PluginManager): pluggy.PluginManager
# 	"""
# 	from pytest_item_dict import hooks

# 	pluginmanager.add_hookspecs(hooks)


def pytest_addoption(parser: Parser) -> None:
	"""Register pytest ini options for the plugin.

	Parameters
	----------
	parser : pytest.Parser
		The pytest option parser.
	"""
	group: pytest.OptionGroup = parser.getgroup(name=ITEM_DICT_PLUGIN_NAME)
	parser.addini(name=INIOptions.CREATE_ITEM_DICT, type='bool', default=True, help='create collection and test hierarchical dicts')
	parser.addini(name=INIOptions.SET_COLLECT_MARKERS, type='bool', default=False, help='set test markers in collection hierarchical dict')
	parser.addini(name=INIOptions.SET_TEST_MARKERS, type='bool', default=False, help='set test markers in test hierarchical dict')
	parser.addini(name=INIOptions.SET_TEST_OUTCOMES, type='bool', default=True, help='set test outcomes in test hierarchical dict')
	parser.addini(name=INIOptions.UPDATE_DICT_ON_TEST, type='bool', default=True, help='update the test outcomes after each test in test hierarchical dict')
	parser.addini(name=INIOptions.SET_TEST_DURATIONS, type='bool', default=False, help='set test durations in test hierarchical dict')


def pytest_configure(config: Config) -> None:
	"""Register :class:`ItemDictPlugin` with pytest's plugin manager.

	Parameters
	----------
	config : pytest.Config
		The active pytest configuration object.
	"""
	create_item_dict: bool = bool(config.getini(name=INIOptions.CREATE_ITEM_DICT))
	if create_item_dict:
		item_dict_plugin: ItemDictPlugin = ItemDictPlugin(config=config)
		config.pluginmanager.register(plugin=item_dict_plugin, name=ITEM_DICT_PLUGIN_NAME)


def pytest_unconfigure(config: Config) -> None:
	"""Unregister :class:`ItemDictPlugin` from pytest's plugin manager.

	Parameters
	----------
	config : pytest.Config
		The active pytest configuration object.
	"""
	item_dict_plugin: object | None = config.pluginmanager.getplugin(name=ITEM_DICT_PLUGIN_NAME)
	if item_dict_plugin is not None:
		config.pluginmanager.unregister(plugin=item_dict_plugin)


def write_json_file(
    hierarchy: dict[str, Any],
    prefix: str = "collect",
    name: str = "hierarchy",
) -> None:
	"""Serialise a hierarchy dict to a JSON file under ``output/reports/``.

	Parameters
	----------
	hierarchy : dict[str, Any]
		The hierarchical dict to serialise.
	prefix : str, optional
		File-name prefix (default ``"collect"``).
	name : str, optional
		File-name stem (default ``"hierarchy"``).
	"""
	output_file: str = Path(f"{__file__}/../../../output/reports/{prefix}_{name}.json").as_posix()
	Path(output_file).parent.mkdir(mode=0o764, parents=True, exist_ok=True)
	with open(file=output_file, mode="w+") as f:
		f.write(json.dumps(obj=hierarchy) + "\n")


def write_xml_file(
    hierarchy: dict[str, Any],
    prefix: str = "collect",
    name: str = "hierarchy",
) -> None:
	"""Serialise a hierarchy dict to an XML file under ``output/reports/``.

	Parameters
	----------
	hierarchy : dict[str, Any]
		The hierarchical dict to serialise.
	prefix : str, optional
		File-name prefix (default ``"collect"``).
	name : str, optional
		File-name stem (default ``"hierarchy"``).
	"""
	output_file: str = Path(f"{__file__}/../../../output/reports/{prefix}_{name}.xml").as_posix()
	xml: XMLConverter = XMLConverter(my_dict=hierarchy, root_node="pytest")
	Path(output_file).parent.mkdir(mode=0o764, parents=True, exist_ok=True)
	with open(file=output_file, mode="w+") as f:
		f.writelines(xml.formatted_xml)


class ItemDictPlugin:
	"""Core pytest plugin that builds and maintains the item-dict hierarchies.

	Two hierarchy dicts are managed throughout the session:

	* :attr:`collect_dict` — populated once during collection and optionally
	  annotated with markers.
	* :attr:`test_dict` — a deep copy of the collection dict, updated
	  incrementally with outcomes/durations as each test runs, then finalised
	  (with aggregated counts) in ``pytest_sessionfinish``.

	Parameters
	----------
	config : pytest.Config
		The active pytest configuration object.

	Attributes
	----------
	config : pytest.Config
		Stored reference to the pytest ``Config`` object.
	collect_dict : CollectionDict
		Hierarchy built from collected items.
	test_dict : TestDict
		Hierarchy extended with outcomes, durations, markers, and aggregated
		counts.
	_suite_start_time : float
		Wall-clock timestamp captured at plugin instantiation, used to compute
		total suite duration.
	"""

	def __init__(self, config: Config) -> None:
		self.config: Config = config
		self.collect_dict: CollectionDict = CollectionDict(config=config)
		self.test_dict: TestDict = TestDict(config=config)
		self._suite_start_time: float = time.time()

	def pytest_collection_modifyitems(
	    self,
	    session: Session,
	    config: Config,
	    items: list[Item],
	) -> None:
		"""Build both hierarchy dicts immediately after collection.

		Parameters
		----------
		session : pytest.Session
			The pytest session object.
		config : pytest.Config
			The pytest config object.
		items : list[pytest.Item]
			Ordered list of collected test items (may be filtered in place).
		"""
		for item in items:
			setattr(item, TestProperties.DURATION, 0.0)
			setattr(item, TestProperties.OUTCOME, "unexecuted")
		self.collect_dict.create_hierarchy_dict(items=items)

		self.test_dict.hierarchy = deepcopy(self.collect_dict.hierarchy)
		self.test_dict.items = items

		self.collect_dict.run_ini_options()
		self.test_dict.set_unexecuted_test_outcomes()

	def pytest_collection_finish(self, session: Session) -> dict[Any, Any]:
		"""Return the collection hierarchy after all modifications are applied.

		Parameters
		----------
		session : pytest.Session
			The pytest session object.

		Returns
		-------
		dict[Any, Any]
			The root of the collection hierarchy dict.
		"""
		self.collect_dict._total_duration = time.time() - self._suite_start_time
		# write_json_file(hierarchy=self.collect_dict.hierarchy)
		# write_xml_file(hierarchy=self.collect_dict.hierarchy)
		return self.collect_dict.hierarchy

	def pytest_sessionfinish(self, session: Session) -> None:
		"""Finalise the test-run hierarchy and compute aggregated metrics.

		Called after all tests have completed.  Writes per-item durations and
		markers (if enabled), then runs :meth:`~TestDict.aggregate_counts` to
		bubble outcome counts and total durations up through every parent node.

		Parameters
		----------
		session : pytest.Session
			The pytest session object.
		"""
		self.test_dict._total_duration = time.time() - self._suite_start_time
		self.test_dict.run_ini_options()
		if self.test_dict.set_outcomes:
			self.test_dict.aggregate_counts()

	@pytest.hookimpl(tryfirst=True, hookwrapper=True)
	def pytest_runtest_makereport(
	    self,
	    item: Item,
	    call: CallInfo,
	) -> Generator[None, Any, None]:
		"""Capture per-test outcomes and cumulative durations in real time.

		This hook wraps the default report-creation mechanism so it can inspect
		the :class:`~pytest.TestReport` for each test phase.  Only the
		``"call"`` phase updates the test outcome; all phases contribute to the
		cumulative item duration.

		Parameters
		----------
		item : pytest.Item
			The test item being reported.
		call : pytest.CallInfo
			Timing and exception information for the current test phase.

		Yields
		------
		None
			Delegation point; the wrapped hook produces the
			:class:`~pytest.TestReport`.
		"""
		outcome = yield
		report: TestReport = outcome.get_result()

		if hasattr(item, TestProperties.DURATION):
			prev_duration: float = getattr(item, TestProperties.DURATION)
			setattr(item, TestProperties.DURATION, prev_duration + report.duration)

		match report.when:

			case "call":
				if self.test_dict.set_outcomes:
					setattr(item, TestProperties.OUTCOME, report.outcome)
					if self.test_dict.update_on_test:
						self.test_dict.set_outcome_attribute(item=item)

			case _:
				pass
