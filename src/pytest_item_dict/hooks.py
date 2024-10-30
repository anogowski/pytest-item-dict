#############################################
#	Dual License: BSD-3-Clause AND MPL-2.0	#
#	Copyright (c) 2024, Adam Nogowski		#
#############################################

# Python Imports
from typing import Any

# Plugin Imports
from pytest_item_dict.pytest_enums import CollectTypes


def pytest_collect_dict_key_property(key_path: list[str], value: Any) -> None:
	"""Add or overwrite property in the collection dict for the given key_path

	Args:
		key_path (list[str]): key to add or overwrite
		value (Any): value of the key
	"""


def pytest_collect_dict_type_property(type: CollectTypes | str, key: str, value: Any) -> None:
	"""Add or overwrite property in the collection dict for the all of the given type

	Args:
		type (CollectTypes | str): Node type to add the property
		key (str): key to add or overwrite
		value (Any): value of the key
	"""


def pytest_test_dict_key_property(key_path: list[str], value: Any) -> None:
	"""Add or overwrite property in the test dict for the given key_path

	Args:
		key_path (list[str]): key to add or overwrite
		value (Any): value of the key
	"""


def pytest_test_dict_type_property(type: CollectTypes | str, key: str, value: Any) -> None:
	"""Add or overwrite property in the test dict for the all of the given type

	Args:
		type (CollectTypes | str): Node type to add the property
		key (str): key to add or overwrite
		value (Any): value of the key
	"""
