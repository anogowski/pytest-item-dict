#############################################
#	Dual License: BSD-3-Clause AND MPL-2.0	#
#	Copyright (c) 2024, Adam Nogowski		#
#############################################

# Python Includes
from sre_constants import IN
from typing import Any, Callable, Self
from collections import defaultdict

from pytest import Config, Item

from pytest_item_dict.pytest_enums import INIOptions, CollectTypes


class CollectionDict:
	_hierarchy: dict[Any, Any]
	_total_duration: float = 0
	_add_markers: bool | Any = False

	def __init__(self, config: Config):
		self._config: Config = config
		self._add_markers = config.getini(name=INIOptions.SET_COLLECT_MARKERS)

	@property
	def hierarchy(self) -> dict[Any, Any]:
		return self._hierarchy

	@hierarchy.setter
	def hierarchy(self, hierarchy: dict[Any, Any]) -> None:
		self._hierarchy = hierarchy

	@property
	def items(self) -> list[Item]:
		return self._items

	@items.setter
	def items(self, items: list[Item]) -> None:
		self._items = items

	@property
	def total_duration(self) -> float:
		return self._total_duration

	@total_duration.setter
	def total_duration(self, duration: float) -> None:
		self._total_duration = duration

	def create_hierarchy_dict(self, items: list[Item]) -> dict:
		self._items: list[Item] = items
		"""Create the hierarchical dictionary for tests

		Returns:
			dict: hierarchical dictionary of tests
		"""
		hierarchy: dict[Any, Any] = {}
		for item in self._items:
			current: dict[Any, Any] = hierarchy
			full_path: list[str] = self.get_key_path(path=item.nodeid)

			self._set_default(current, full_path)

		self._hierarchy = hierarchy
		return hierarchy

	def get_key_path(self, path: str) -> list[str]:
		"""Split a path or nodeid into a list of keys to access the dictionary

		Args:
			path (str): a path or nodeid

		Returns:
			list[str]: keys in hierarchical order to access dictionary
		"""
		full_path: list[str] = path.split(sep="/")

		if '::' in full_path[-1]:
			temp_path: str = full_path[-1]
			full_path = full_path[:-1]
			full_path += temp_path.split(sep="::")

		return full_path

	def _set_default(self, hierarchy: dict, key_path: list[str]) -> None:
		"""Set the default value of each key to an empty dictionary

		Args:
			hierarchy (dict): hierarchical dictionary of tests
			key_path (list[str]): keys in hierarchical order to access dictionary
		"""
		for part in key_path:
			hierarchy = hierarchy.setdefault(part, defaultdict(dict))

	def _set_new_value(self, hierarchy: dict[Any, Any], key_path: list[str], value: Any) -> None:
		"""Sets a value in a hierarchical dictionary using a list as the key path.

		Args:
			hierarchy (dict[Any, Any]): hierarchical dictionary of tests
			key_path (list[str]): keys in hierarchical order to access dictionary
			value (Any): new value to add/overwrite
		"""

		current: dict[str, Any] = hierarchy
		for key in key_path[:-1]:
			if key not in current:
				current.setdefault(key, defaultdict(dict))
			current = current[key]
		key: str = key_path[-1]
		current[key] = value

	def get_value_from_key_path(self, hierarchy: dict[Any, Any], key_path: list[str]) -> None | Any:
		"""Gets a value from a hierarchical dictionary using a list as the key path.

		Args:
			hierarchy (dict[Any, Any]): hierarchical dictionary of tests
			key_path (list[str]): keys in hierarchical order to access dictionary

		Returns:
			None | Any: value of key_path if present
		"""
		current: Any = hierarchy
		for key in key_path:
			if key not in current:
				return None
			current = current[key]
		return current

	def set_attribute(self, hierarchy: dict, key_path: list[str], key: str, value: Any) -> None:
		"""Add an attribute to the key_path in the hierarchy dictionary \n hierarchy[key_path][key] = value
		
		Args:
			hierarchy (dict): hierarchical dictionary of tests
			key_path (list[str]): keys in hierarchical order to access dictionary
			key (str): new key to add/overwrite, if key does not start with '@' it will be pre-appended
			value (Any): new value to add/overwrite
		"""
		if key[0] != "@":
			key = f"@{key}"
		key_path.append(key)

		self._set_new_value(hierarchy=hierarchy, key_path=key_path, value=value)

		key_path.pop()

	def set_marker(self, item: Item) -> None:
		"""Add item.own_markers as an attribute to each test in hierarchy \n 

		Args:
			item (Item): Item to check for markers 
		"""
		if self._add_markers:
			current: dict[Any, Any] = self.hierarchy
			key_path: list[str] = self.get_key_path(path=item.nodeid)
			if len(item.own_markers) > 0:
				markers: list[str] = [marker.name for marker in item.own_markers]
				self.set_attribute(hierarchy=current, key_path=key_path, key="@markers", value=markers)

	def _dict_on_parent_types(self, search_type: list[str | CollectTypes], property_dict: dict[Any, Any], func: Callable[[dict, list[str], str, Any], None]):
		for item in self.items:
			parents = list(item.iter_parents())
			for parent in parents:
				if type(parent).__name__ in search_type and type(parent).__name__ != "Session" and parent.nodeid != ".":
					key_path: list[str] = self.get_key_path(path=parent.nodeid)
					for key, value in property_dict.items():
						func(hierarchy=self.hierarchy, key_path=key_path, key=key, value=value)

	def set_attribute_on_parent_types(self, search_type: list[str | CollectTypes], key: str, value: Any) -> None:
		"""Add an attribute to the hierarchy dict based on provided parent types
		Excludes Session type

		Args:
			search_type (list[str  |  CollectTypes]): list of type(parent).__name__
			key (str): new key to add/overwrite, if key does not start with '@' it will be pre-appended
			value (Any): new value to add/overwrite
		"""
		for item in self.items:
			parents = list(item.iter_parents())
			for parent in parents:
				if type(parent).__name__ in search_type and type(parent).__name__ != "Session" and parent.nodeid != ".":
					key_path: list[str] = self.get_key_path(path=parent.nodeid)
					self.set_attribute(hierarchy=self.hierarchy, key_path=key_path, key=key, value=value)

	def set_attribute_dict_to_types(self, search_type: list[str | CollectTypes], attr_dict: dict[Any, Any]) -> None:
		"""Add an attribute to the hierarchy dict based on provided parent types
		Excludes Session type

		Args:
			search_type (list[str  |  CollectTypes]): list of type(parent).__name__
			attr_dict (dict[Any, Any]): Key, Value pair to add/overwrite. If the key does not start with '@' it will be pre-appended
		"""
		self._dict_on_parent_types(search_type=search_type, property_dict=attr_dict, func=self.set_attribute)

	def set_sub_element(self, hierarchy: dict, key_path: list[str], key: str, value: Any) -> None:
		"""Add an sub element to the key_path in the hierarchy dictionary \n hierarchy[key_path][key] = value
		
		Args:
			hierarchy (dict): hierarchical dictionary of tests
			key_path (list[str]): keys in hierarchical order to access dictionary
			key (str): new key to add/overwrite, if key starts with '@' it will be removed
			value (Any): new value to add/overwrite
		"""
		if key[0] == "@":
			key = key[1:]
		key_path.append(key)

		self._set_new_value(hierarchy=hierarchy, key_path=key_path, value=value)

		key_path.pop()

	def set_sub_element_dict(self, hierarchy: dict, key_path: list[str], sub_dict: dict[Any, Any]) -> None:
		"""Add an sub element dict to the key_path in the hierarchy dictionary \n hierarchy[key_path][sub_dict_key] = sub_dict[sub_dict_key]

		Args:
			hierarchy (dict): hierarchical dictionary of tests
			key_path (list[str]): keys in hierarchical order to access dictionary
			sub_dict (dict[Any, Any]): Key, Value pair to add/overwrite. If the key does starts with '@' it will be removed
		"""
		for key, value in sub_dict.items():
			self.set_sub_element(hierarchy=hierarchy, key_path=key_path, key=key, value=value)

	def set_sub_element_dict_to_types(self, search_type: list[str | CollectTypes], sub_dict: dict[Any, Any]):
		"""Add a sub element dict to the hierarchy dict based on provided parent types

		Args:
			hierarchy (dict): hierarchical dictionary of tests
			key_path (list[str]): keys in hierarchical order to access dictionary
			sub_dict (dict[Any, Any]): Key, Value pair to add/overwrite. If the key does starts with '@' it will be removed
		"""
		self._dict_on_parent_types(search_type=search_type, property_dict=sub_dict, func=self.set_sub_element)

	def run_ini_options(self):
		"""Run functions based on stored ini values
		"""
		if self._add_markers:
			for item in self.items:
				self.set_marker(item=item)

	def run_hooks(self):
		"""Run hook functions
		"""
		self._config.hook
