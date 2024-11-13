#############################################
#	Dual License: BSD-3-Clause AND MPL-2.0	#
#	Copyright (c) 2024, Adam Nogowski		#
#############################################

# Python Imports
from typing import Any, Final
from datetime import datetime, timedelta

# Pytest Imports
from pytest import Config, Item, Session, Function
from _pytest.nodes import Node

# Plugin Imports
from pytest_item_dict.item_dict_enums import TestProperties, INIOptions
from pytest_item_dict.collect_dict import CollectionDict


class TestDict(CollectionDict):
	_set_outcomes: bool | Any = False
	_set_durations: bool | Any = False
	_update_on_test: bool | Any = False
	_count_test_outcomes: bool | Any = False
	_calculate_test_durations: bool | Any = False

	UNEXECUTED: Final[str] = "unexecuted"
	MILLISECONDS_TIME_FORMAT: Final[str] = r"%H:%M:%S.%f"
	SECONDS_TIME_FORMAT: Final[str] = r"%H:%M:%S"

	def __init__(self, config: Config) -> None:
		super().__init__(config=config)
		self._add_markers = config.getini(name=INIOptions.SET_TEST_MARKERS)
		self._set_durations = config.getini(name=INIOptions.SET_TEST_DURATIONS)
		self._set_outcomes = self._config.getini(name=INIOptions.SET_TEST_OUTCOMES)
		self._update_on_test = self._config.getini(name=INIOptions.UPDATE_DICT_ON_TEST)
		self._count_test_outcomes = self._config.getini(name=INIOptions.SET_TEST_HIERARCHY_OUTCOMES)
		self._calculate_test_durations = self._config.getini(name=INIOptions.SET_TEST_HIERARCHY_DURATIONS)

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

	@property
	def count_test_outcomes(self) -> bool:
		"""Add test outcome to parents in hierarchy dict

		Returns:
			bool: INI Option for setting test outcomes to parents
		"""

		return self._count_test_outcomes

	@property
	def calculate_test_durations(self) -> bool:
		"""Add test durations to parents in hierarchy dict

		Returns:
			bool: INI Option for setting test durations to parents
		"""

		return self._calculate_test_durations

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
		if self._set_outcomes or self._set_durations or self._add_markers:
			for item in self.items:
				self.set_outcome_attribute(item=item)
				self.set_duration_attribute(item=item)
				self.set_marker_attribute(item=item)

				if self._count_test_outcomes or self._calculate_test_durations:
					for parent in item.iter_parents():
						if self._check_parent(parent=parent):
							break
						if isinstance(parent, Function):
							continue

						self.update_parent_outcome_attribute(item=item, parent=parent)
						self.update_parent_duration_attribute(item=item, parent=parent)

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

	def get_parent_attribute(self, item: Item, parent: Node, test_prop: TestProperties, key: str) -> tuple[Any, list[str], Any | None]:
		"""Get the prop_value from the item based on test_prop. Get the dict_value based on key.

		Args:
			item (Item): pytest.Item
			parent (Node): pytest.Item.parent
			test_prop (TestProperties): property to get from item
			key (str): key in dict to check for dict_value

		Returns:
			tuple[Any, list[str], Any | None]: prop_value, key_path, dict_value
		"""
		prop_value: Any = getattr(item, test_prop)
		key_path: list[str] = self.get_key_path(path=parent.nodeid)
		key_path.append(key)
		dict_value: Any | None = self.get_value_from_key_path(key_path=key_path)
		key_path.pop()

		return prop_value, key_path, dict_value

	def update_parent_outcome_attribute(self, item: Item, parent: Node) -> None:
		"""Set or update the outcome of child tests for each class, module, and directory

		Args:
			item (Item): pytest.Item
			parent (Node): pytest.Item.parent
		"""
		if self._set_outcomes and self._count_test_outcomes and hasattr(item, TestProperties.OUTCOME):
			prop_value: str = getattr(item, TestProperties.OUTCOME)
			dict_key: str = f"@{prop_value}"

			prop_value, key_path, dict_value = self.get_parent_attribute(item=item, parent=parent, test_prop=TestProperties.OUTCOME, key=dict_key)

			if dict_value is not None:
				num_outcome: int = int(dict_value)
				num_outcome += 1
				self.set_attribute(key_path=key_path, key=dict_key, value=num_outcome)
				if prop_value != self.UNEXECUTED:
					key_path.append(f"@{self.UNEXECUTED}")
					unexecuted: Any | None = self.get_value_from_key_path(key_path=key_path)
					key_path.pop()
					if unexecuted is not None:
						num_unexecuted: int = int(unexecuted)
						num_unexecuted -= 1
						self.set_attribute(key_path=key_path, key=f"@{self.UNEXECUTED}", value=num_unexecuted)

			else:
				self.set_attribute(key_path=key_path, key=dict_key, value=1)

	def update_parent_duration_attribute(self, item: Item, parent: Node) -> None:
		"""Set or update the duration of child tests for each class, module, and directory

		Args:
			item (Item): pytest.Item
			parent (Node): pytest.Item.parent
		"""
		if self._set_durations and self._calculate_test_durations and hasattr(item, TestProperties.DURATION):
			prop_value: float = 0
			dict_key: str = f"@{TestProperties.DURATION}"

			prop_value, key_path, dict_value = self.get_parent_attribute(item=item, parent=parent, test_prop=TestProperties.DURATION, key=dict_key)

			if dict_value is not None:
				td: timedelta = timedelta(seconds=prop_value)
				dt_value: datetime
				try:
					dt_value: datetime = datetime.strptime(dict_value, self.MILLISECONDS_TIME_FORMAT)
				except ValueError:
					dt_value: datetime = datetime.strptime(dict_value, self.SECONDS_TIME_FORMAT)

				new_dt: datetime = dt_value + td

				self.set_attribute(key_path=key_path, key=dict_key, value=new_dt.strftime(self.MILLISECONDS_TIME_FORMAT))
			else:
				td: timedelta = timedelta(seconds=prop_value)
				self.set_attribute(key_path=key_path, key=dict_key, value=str(object=td))

	def set_duration_attribute(self, item: Item):
		"""Update test duration in hierarchy dict from item.duration

		Args:
			item (Item): pytest.Item - test to update
		"""
		if self._set_durations and hasattr(item, TestProperties.DURATION):
			key_path: list[str] = self.get_key_path(path=item.nodeid)
			td: timedelta = timedelta(seconds=getattr(item, TestProperties.DURATION))
			self.set_attribute(key_path=key_path, key=TestProperties.DURATION, value=str(object=td))
