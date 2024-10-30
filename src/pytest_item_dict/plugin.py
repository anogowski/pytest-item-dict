#############################################
#	Dual License: BSD-3-Clause AND MPL-2.0	#
#	Copyright (c) 2024, Adam Nogowski		#
#############################################

# Python Includes
from typing import Any, Final, Generator
import json
from pathlib import Path
from copy import deepcopy
import time

# Pip Includes
from data_to_xml.xml_converter import XMLConverter

# PyTest Includes
import pytest
from pytest import Item, Session, Config, Parser, CallInfo, TestReport

# Plugin Includes
from pytest_item_dict.pytest_enums import INIOptions, CollectTypes, TestProperties
from pytest_item_dict.collect_dict import CollectionDict
from pytest_item_dict.test_dict import TestDict

PLUGIN_NAME: Final[str] = 'item_dict'


def pytest_addhooks(pluginmanager) -> None:
	from pytest_item_dict import hooks

	pluginmanager.add_hookspecs(hooks)


def pytest_addoption(parser: Parser):
	group: pytest.OptionGroup = parser.getgroup(name=PLUGIN_NAME)
	parser.addini(name=INIOptions.CREATE_ITEM_DICT, type='bool', default=True, help='create collection and test hierarchical dicts')
	parser.addini(name=INIOptions.SET_COLLECT_MARKERS, type='bool', default=False, help='set test markers in collection hierarchical dict')
	parser.addini(name=INIOptions.SET_TEST_MARKERS, type='bool', default=False, help='set test markers in test hierarchical dict')
	parser.addini(name=INIOptions.SET_TEST_OUTCOMES, type='bool', default=True, help='set test outcomes in test hierarchical dict')
	parser.addini(name=INIOptions.SET_TEST_DURATIONS, type='bool', default=False, help='set test durations in test hierarchical dict')


def pytest_configure(config: Config) -> None:
	"""Register Plugin

	Args:
		config (Config): Pytest Config
	"""
	create_item_dict: bool | Any = config.getini(name="create_item_dict")
	if create_item_dict:
		item_dict_plugin: ItemDictPlugin = ItemDictPlugin(config=config)
		config.pluginmanager.register(plugin=item_dict_plugin, name=PLUGIN_NAME)


def pytest_unconfigure(config: Config) -> None:
	"""Unregister Plugin

	Args:
		config (Config): Pytest Config
	"""
	item_dict_plugin: object | None = config.pluginmanager.getplugin(name=PLUGIN_NAME)
	if item_dict_plugin is not None:
		config.pluginmanager.unregister(plugin=item_dict_plugin)


def write_json_file(json_str: str, prefix: str = "collect", name: str = "hierarchy"):
	output_file: str = Path(f"{__file__}/../../../output/reports/{prefix}_{name}.json").as_posix()
	Path(output_file).parent.mkdir(mode=764, parents=True, exist_ok=True)
	with open(file=output_file, mode="w+") as f:
		f.write(json_str + "\n")


def write_xml_file(items_dict: dict, prefix: str = "collect", name: str = "hierarchy"):
	output_file: str = Path(f"{__file__}/../../../output/reports/{prefix}_{name}.xml").as_posix()
	xml: XMLConverter = XMLConverter(my_dict=items_dict, root_node="pytest")
	Path(output_file).parent.mkdir(mode=764, parents=True, exist_ok=True)
	with open(file=output_file, mode="w+") as f:
		f.writelines(xml.formatted_xml)


class ItemDictPlugin:

	def __init__(self, config: Config):
		self.config: Config = config
		self.collect_dict: CollectionDict = CollectionDict(config=config)
		self.test_dict: TestDict = TestDict(config=config)
		self._suite_start_time: float = time.time()

	def pytest_collection_modifyitems(self, session: Session, config: Config, items: list[Item]):
		for item in items:
			setattr(item, TestProperties.DURATION, 0)
			setattr(item, TestProperties.OUTCOME, "unexecuted")
		self.collect_dict.create_hierarchy_dict(items=items)

		self.test_dict.hierarchy = deepcopy(self.collect_dict.hierarchy)
		self.test_dict.items = items

		self.collect_dict.run_ini_options()
		self.test_dict.set_outcomes()

	def pytest_collection_finish(self, session: Session) -> dict[Any, Any]:
		self.collect_dict._total_duration = self._suite_start_time - time.time()
		write_json_file(json_str=json.dumps(obj=self.collect_dict.hierarchy))
		write_xml_file(items_dict=self.collect_dict.hierarchy)
		return self.collect_dict.hierarchy

	def pytest_sessionfinish(self, session: Session):
		self.test_dict._total_duration = self._suite_start_time - time.time()
		self.test_dict.run_ini_options()

		write_xml_file(items_dict=self.test_dict.hierarchy, prefix="test")
		write_json_file(json_str=json.dumps(obj=self.test_dict.hierarchy), prefix="test")

	@pytest.hookimpl(tryfirst=True, hookwrapper=True)
	def pytest_runtest_makereport(self, item: Item, call: CallInfo) -> Generator[None, Any, None]:
		"""Called to create a :class:`~pytest.TestReport` for each of
		the setup, call and teardown runtest phases of a test item.

		See :hook:`pytest_runtest_protocol` for a description of the runtest protocol.

		:param item: The item.
		:param call: The :class:`~pytest.CallInfo` for the phase.

		Stops at first non-None result, see :ref:`firstresult`.

		Use in conftest plugins
		=======================

		Any conftest file can implement this hook. For a given item, only conftest
		files in the item's directory and its parent directories are consulted.
		"""
		outcome = yield
		report: TestReport = outcome.get_result()

		if hasattr(item, TestProperties.DURATION):
			prev_duration: float = getattr(item, TestProperties.DURATION)
			setattr(item, TestProperties.DURATION, prev_duration + report.duration)

		match report.when:

			case "call":
				setattr(item, TestProperties.OUTCOME, report.outcome)
				self.test_dict.set_outcome(item=item, outcome=report.outcome)

			case _:
				pass
