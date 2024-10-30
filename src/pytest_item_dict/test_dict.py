#############################################
#	Dual License: BSD-3-Clause AND MPL-2.0	#
#	Copyright (c) 2024, Adam Nogowski		#
#############################################

# Python Imports
from typing import Any
import datetime

# Pytest Imports
from pytest import Config, Item

# Plugin Imports
from pytest_item_dict.pytest_enums import TestProperties, INIOptions
from pytest_item_dict.collect_dict import CollectionDict


class TestDict(CollectionDict):
	_set_outcomes: bool | Any = False
	_set_durations: bool | Any = False

	def __init__(self, config: Config) -> None:
		super().__init__(config=config)
		self._add_markers = config.getini(name=INIOptions.SET_TEST_MARKERS)
		self._set_durations = config.getini(name=INIOptions.SET_TEST_DURATIONS)
		self._set_outcomes = self._config.getini(name=INIOptions.SET_TEST_OUTCOMES)

	def set_outcomes(self, outcome="unexecuted"):
		if self._set_outcomes:
			for item in self.items:
				self.set_outcome(item=item, outcome=outcome)

	def run_ini_options(self,) -> None:
		if self._add_markers or self._set_durations:
			for item in self.items:
				self.set_marker(item=item)
				self.set_duration(item=item)

	def set_outcome(self, item: Item, outcome: str) -> None:
		if self._set_outcomes:
			key_path: list[str] = self.get_key_path(path=item.nodeid)
			self.set_attribute(hierarchy=self.hierarchy, key_path=key_path, key=TestProperties.OUTCOME, value=outcome)

	def set_duration(self, item: Item):
		if self._set_durations:
			key_path: list[str] = self.get_key_path(path=item.nodeid)
			if hasattr(item, TestProperties.DURATION):
				td: datetime.timedelta = datetime.timedelta(seconds=getattr(item, TestProperties.DURATION))
				self.set_attribute(hierarchy=self.hierarchy, key_path=key_path, key=TestProperties.DURATION, value=str(td))
