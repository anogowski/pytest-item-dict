#############################################
#	Dual License: BSD-3-Clause AND MPL-2.0	#
#	Copyright (c) 2024, Adam Nogowski		#
#############################################

# Python Imports
from typing import Any, Final
import datetime

# Pytest Imports
from pytest import Config, Item

# Plugin Imports
from pytest_item_dict.item_dict_enums import TestProperties, INIOptions
from pytest_item_dict.collect_dict import CollectionDict


class TestDict(CollectionDict):
	_set_outcomes: bool | Any = False
	_set_durations: bool | Any = False
	_update_on_test: bool | Any = False

	UNEXECUTED: Final[str] = "unexecuted"

	def __init__(self, config: Config) -> None:
		super().__init__(config=config)
		self._add_markers = config.getini(name=INIOptions.SET_TEST_MARKERS)
		self._set_durations = config.getini(name=INIOptions.SET_TEST_DURATIONS)
		self._set_outcomes = self._config.getini(name=INIOptions.SET_TEST_OUTCOMES)
		self._update_on_test = self._config.getini(name=INIOptions.UPDATE_DICT_ON_TEST)

	@property
	def set_outcomes(self) -> bool:
		"""Add test outcome to session.items and hierarchy dict

		Returns:
			bool: INI Option for setting test outcomes
		"""
		return self._set_outcomes

	@property
	def set_durations(self) -> bool:
		"""Add test duration to session.items and hierarchy dict

		Returns:
			bool: INI Option for setting test duration
		"""
		return self._set_durations

	@property
	def update_on_test(self) -> bool:
		"""Update test outcome in hierarchy dict after every test

		Returns:
			bool: INI Option for updating test outcome after every test
		"""
		return self._update_on_test

	def set_unexecuted_test_outcomes(self) -> None:
		"""Create/Overwrite each item.outcome in session.items to 'self.UNEXECUTED'
		"""
		if self._set_outcomes:
			for item in self.items:
				setattr(item, TestProperties.OUTCOME, self.UNEXECUTED)
				self.set_outcome_attribute(item=item)

	def run_ini_options(self) -> None:
		"""Run functions to set attributes for options store in ini/toml/yaml file
		"""
		if self._add_markers or self._set_durations:
			for item in self.items:
				self.set_marker_attribute(item=item)
				self.set_duration_attribute(item=item)

	def set_test_outcomes(self) -> None:
		"""Set test outcome in hierarchy dict for every test based on item.outcome
		"""
		if self._set_outcomes:
			for item in self.items:
				self.set_outcome_attribute(item=item)

	def set_outcome_attribute(self, item: Item) -> None:
		"""Update test outcome in hierarchy dict from item.outcome

		Args:
			item (Item): pytest.Item - test to update
		"""
		if self._set_outcomes and hasattr(item, TestProperties.OUTCOME):
			key_path: list[str] = self.get_key_path(path=item.nodeid)
			self.set_attribute(key_path=key_path, key=TestProperties.OUTCOME, value=getattr(item, TestProperties.OUTCOME))

	def set_duration_attribute(self, item: Item):
		"""Update test duration in hierarchy dict from item.duration

		Args:
			item (Item): pytest.Item - test to update
		"""
		if self._set_durations and hasattr(item, TestProperties.DURATION):
			key_path: list[str] = self.get_key_path(path=item.nodeid)
			td: datetime.timedelta = datetime.timedelta(seconds=getattr(item, TestProperties.DURATION))
			self.set_attribute(key_path=key_path, key=TestProperties.DURATION, value=str(object=td))
