#############################################
#	Dual License: BSD-3-Clause AND MPL-2.0	#
#	Copyright (c) 2024, Adam Nogowski		#
#############################################

# Python Includes
from typing import Any, Callable
from collections import defaultdict

# Pytest Imports
from pytest import Config, Item
from _pytest.nodes import Node

# Plugin Imports
from pytest_item_dict.item_dict_enums import INIOptions, CollectTypes


class CollectionDict:
	_total_duration: float = 0
	_add_markers: bool | Any = False
	_hierarchy: dict[Any, Any] = {}
	_items: list[Item] = []

	def __init__(self, config: Config):
		self._config: Config = config
		self._add_markers = config.getini(name=INIOptions.SET_COLLECT_MARKERS)

	@property
	def add_markers(self) -> bool:
		"""Add test markers to hierarchy dict

		Returns:
			bool: INI Option for setting test markers
		"""
		return self._add_markers

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

	def create_hierarchy_dict(self, items: list[Item]) -> None:
		self._items: list[Item] = items
		"""Create the hierarchical dictionary for tests
		"""
		for item in self._items:
			key_path: list[str] = self.get_key_path(path=item.nodeid)

			self._set_default(key_path=key_path)

	def get_key_path(self, path: str) -> list[str]:
		"""Split a path or nodeid into a list of keys to access the dictionary

		Args:
			path (str): a path or nodeid

		Returns:
			list[str]: keys in hierarchical order to access dictionary
		"""
		key_path: list[str] = path.split(sep="/")

		if '::' in key_path[-1]:
			temp_path: str = key_path[-1]
			key_path = key_path[:-1]
			key_path += temp_path.split(sep="::")

		return key_path

	def _set_default(self, key_path: list[str]) -> None:
		"""Set the default value of each key to an empty dictionary

		Args:
			key_path (list[str]): keys in hierarchical order to access dictionary
		"""
		for part in key_path:
			self._hierarchy = self._hierarchy.setdefault(part, defaultdict(dict))

	def _set_new_value(self, key_path: list[str], value: Any) -> None:
		"""Sets a value in a hierarchical dictionary using a list as the key path.

		Args:
			key_path (list[str]): keys in hierarchical order to access dictionary
			value (Any): new value to add/overwrite
		"""

		current: dict[str, Any] = self._hierarchy
		for key in key_path[:-1]:
			if key not in current:
				current.setdefault(key, defaultdict(dict))
			current = current[key]
		key: str = key_path[-1]
		current[key] = value

	def get_value_from_key_path(self, key_path: list[str]) -> None | Any:
		"""Gets a value from a hierarchical dictionary using a list as the key path.

		Args:
			key_path (list[str]): keys in hierarchical order to access dictionary

		Returns:
			None | Any: value of key_path if present
		"""
		current: Any = self._hierarchy

		try:
			for key in key_path:
				if key not in current:
					return None
				current = current[key]
			return current
		except KeyError:
			return None

	def set_attribute(self, key_path: list[str], key: str, value: Any) -> None:
		"""Add/Overwrite an attribute to the key_path in the hierarchy dictionary \n hierarchy[key_path][key] = value
		
		Args:
			key_path (list[str]): keys in hierarchical order to access dictionary
			key (str): new key to add/overwrite, if key does not start with '@' it will be pre-appended
			value (Any): new value to add/overwrite
		"""
		if key[0] != "@":
			key = f"@{key}"
		key_path.append(key)

		self._set_new_value(key_path=key_path, value=value)

		key_path.pop()

	def set_marker_attribute(self, item: Item) -> None:
		"""Add/Overwrite item.own_markers as an attribute to each test in hierarchy \n 

		Args:
			item (Item): Item to check for markers 
		"""
		if self._add_markers:
			key_path: list[str] = self.get_key_path(path=item.nodeid)
			if len(item.own_markers) > 0:
				markers: list[str] = [marker.name for marker in item.own_markers]
				self.set_attribute(key_path=key_path, key="@markers", value=markers)

	def _check_parent(self, parent: Node) -> bool:
		return type(parent).__name__ != "Session" and parent.nodeid != "."

	def _dict_on_parent_types(self, search_type: list[str | CollectTypes], property_dict: dict[Any, Any], func: Callable[[list[str], str, Any], None]) -> None:
		"""Add/Overwrite an attribute or sub element in the hierarchy dict based on provided parent types

		Args:
			search_type (list[str  |  CollectTypes]): list of type(parent).__name__
			property_dict (dict[Any, Any]): dict to use
			func (Callable[[list[str], str, Any], None]): set_attribute OR set_sub_element
		"""
		for item in self.items:
			parents = list(item.iter_parents())
			for parent in parents:
				if type(parent).__name__ in search_type and self._check_parent(parent=parent):
					key_path: list[str] = self.get_key_path(path=parent.nodeid)
					for key, value in property_dict.items():
						func(key_path=key_path, key=key, value=value)

	def set_attribute_on_parent_types(self, search_type: list[str | CollectTypes], key: str, value: Any) -> None:
		"""Add/Overwrite an attribute in the hierarchy dict based on provided parent types
		Excludes Session type

		Args:
			search_type (list[str  |  CollectTypes]): list of type(parent).__name__
			key (str): new key to add/overwrite, if key does not start with '@' it will be pre-appended
			value (Any): new value to add/overwrite
		"""
		for item in self.items:
			parents = list(item.iter_parents())
			for parent in parents:
				if type(parent).__name__ in search_type and self._check_parent(parent=parent):
					key_path: list[str] = self.get_key_path(path=parent.nodeid)
					self.set_attribute(key_path=key_path, key=key, value=value)

	def set_attribute_dict_to_types(self, search_type: list[str | CollectTypes], attr_dict: dict[Any, Any]) -> None:
		"""Add/Overwrite an attribute in the hierarchy dict based on provided parent types
		Excludes Session type

		Args:
			search_type (list[str  |  CollectTypes]): list of type(parent).__name__
			attr_dict (dict[Any, Any]): Key, Value pair to add/overwrite. If the key does not start with '@' it will be pre-appended
		"""
		self._dict_on_parent_types(search_type=search_type, property_dict=attr_dict, func=self.set_attribute)

	def set_sub_element(self, key_path: list[str], key: str, value: Any) -> None:
		"""Add/Overwrite an sub element in the key_path in the hierarchy dictionary \n hierarchy[key_path][key] = value
		
		Args:
			key_path (list[str]): keys in hierarchical order to access dictionary
			key (str): new key to add/overwrite, if key starts with '@' it will be removed
			value (Any): new value to add/overwrite
		"""
		if key[0] == "@":
			key = key[1:]
		key_path.append(key)

		self._set_new_value(key_path=key_path, value=value)

		key_path.pop()

	def set_sub_element_dict(self, key_path: list[str], sub_dict: dict[Any, Any]) -> None:
		"""Add/Overwrite an sub element dict in the key_path in the hierarchy dictionary \n hierarchy[key_path][sub_dict_key] = sub_dict[sub_dict_key]

		Args:
			key_path (list[str]): keys in hierarchical order to access dictionary
			sub_dict (dict[Any, Any]): Key, Value pair to add/overwrite. If the key does starts with '@' it will be removed
		"""
		for key, value in sub_dict.items():
			self.set_sub_element(key_path=key_path, key=key, value=value)

	def set_sub_element_dict_to_types(self, search_type: list[str | CollectTypes], sub_dict: dict[Any, Any]):
		"""Add/Overwrite a sub element dict in the hierarchy dict based on provided parent types

		Args:
			key_path (list[str]): keys in hierarchical order to access dictionary
			sub_dict (dict[Any, Any]): Key, Value pair to add/overwrite. If the key does starts with '@' it will be removed
		"""
		self._dict_on_parent_types(search_type=search_type, property_dict=sub_dict, func=self.set_sub_element)

	def _set_item_attribute_per_item(self, attributes: list[str], func: Callable[[list[str], str, Any], None]):
		"""Set a pre-existing attribute of pytest.Item per item to the hierarchy dict

		Args:
			attributes (list[str]): attributes (list[str]): name of attributes
			func (Callable[[list[str], str, Any], None]): set_attribute OR set_sub_element
		"""
		for item in self.items:
			key_path: list[str] = self.get_key_path(path=item.nodeid)
			for attribute in attributes:
				if hasattr(item, attribute):
					func(key_path, attribute, getattr(item, attribute))

	def set_item_attributes_as_attribute(self, attributes: list[str]):
		"""Set a pre-existing attribute of pytest.Item per item to the hierarchy dict as an attribute

		Args:
			attributes (list[str]): name of attributes
		"""
		self._set_item_attribute_per_item(attributes=attributes, func=self.set_attribute)

	def set_item_attributes_as_sub_element(self, attributes: list[str]):
		"""Set a pre-existing attribute of pytest.Item per item to the hierarchy dict as a sub element

		Args:
			attributes (list[str]): name of attributes
		"""
		self._set_item_attribute_per_item(attributes=attributes, func=self.set_sub_element)

	def run_ini_options(self):
		"""Run functions based on stored ini values
		"""
		if self._add_markers:
			for item in self.items:
				self.set_marker_attribute(item=item)

	def run_hooks(self):
		"""Run hook functions
		"""
		self._config.hook
