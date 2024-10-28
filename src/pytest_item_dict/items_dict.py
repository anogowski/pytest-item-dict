#############################################
#	Dual License: BSD-3-Clause AND MPL-2.0	#
#	Copyright (c) 2024, Adam Nogowski		#
#############################################

from typing import Any
from collections import defaultdict

from pytest import Session


class ItemsDict:

	def __init__(self, session: Session):
		self.session: Session = session
		self.collect_dict: dict[Any, Any] = self.create_hierarchy_dict()
		self.report_dict: dict[Any, Any] = self.collect_dict.copy()
		self.add_markers(hierarchy=self.collect_dict)

	def create_hierarchy_dict(self) -> dict:
		"""Create the hierarchical dictionary for tests

		Returns:
			dict: hierarchical dictionary of tests
		"""
		hierarchy: dict[Any, Any] = {}
		for item in self.session.items:
			current: dict[Any, Any] = hierarchy
			full_path: list[str] = self.convert_path_to_key_list(path=item.nodeid)

			self.set_default(current, full_path)
		return hierarchy

	def convert_path_to_key_list(self, path: str) -> list[str]:
		"""Split a path or nodeid into a list of keys to access the dictionary

		Args:
			path (str): a path or nodeid

		Returns:
			list[str]: keys in hierarchical order to access dictionary
		"""
		full_path: list[str] = []

		paths: list[str] = path.split(sep="/")
		full_path += paths[:-1]

		if '::' in paths[-1]:
			full_path += path.split(sep="/")[-1].split(sep="::")
		else:
			full_path += paths[-1]

		return full_path

	def set_default(self, hierarchy: dict, key_path: list[str]) -> None:
		"""Set the default value of each key to an empty dictionary

		Args:
			hierarchy (dict): hierarchical dictionary of tests
			key_path (list[str]): keys in hierarchical order to access dictionary
		"""
		for part in key_path:
			hierarchy = hierarchy.setdefault(part, defaultdict(dict))

	def add_attribute(self, hierarchy: dict, key_path: list[str], key: str, value: Any) -> None:
		"""Add an attribute to the key_path in the hierarchy dictionary \n hierarchy[key_path][key] = value
		
		Args:
			hierarchy (dict): hierarchical dictionary of tests
			key_path (list[str]): keys in hierarchical order to access dictionary
			key (str): new key to add, if key does not start with '@' it will be pre-appended
			value (Any): new value to add
		"""
		if key[0] != "@":
			key = f"@{key}"
		key_path += [key]

		self.set_new_value(hierarchy, key_path, value)

	def add_markers(self, hierarchy: dict) -> None:
		"""Add markers attribute to tests in hierarchy

		Args:
			hierarchy (dict): add item.own_markers as an attribute to each test
		"""
		for item in self.session.items:
			current: dict[Any, Any] = hierarchy
			key_path: list[str] = self.convert_path_to_key_list(path=item.nodeid)
			if len(item.own_markers) > 0:

				markers: list[str] = [marker.name for marker in item.own_markers]
				self.add_attribute(hierarchy=current, key_path=key_path, key="@markers", value=markers)

	def set_new_value(self, data: dict, path: list[str], value: Any) -> None:
		"""Sets a value in a hierarchical dictionary using a list as the key path."""
		current: dict[str, Any] = data
		for key in path[:-1]:
			if key not in current:
				current.setdefault(key, defaultdict(dict))
			current = current[key]
		current[path[-1]] = value

	def get_value(self, data, path) -> None | Any:
		"""Gets a value from a hierarchical dictionary using a list as the key path."""
		current = data
		for key in path:
			if key not in current:
				return None
			current = current[key]
		return current
