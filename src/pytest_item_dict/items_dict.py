from collections import Counter
import json
from dataclasses import dataclass
from pytest import CollectReport, Item, Session
from _pytest.nodes import Node
from typing import Any
from collections import defaultdict


class ItemsDict:
	_items: list[Item]
	_hierarchy_dict = defaultdict()
	_path_dict = defaultdict()
	_hierarchy_list: list[Any] = list()
	_temp_dict = defaultdict()

	def __init__(self, session: Session):
		self._items = session.items
		self._hierarchy_dict = self.get_hierarchy_dict(session.items)
		self._path_dict = self.path_collection(session)
		self._hierarchy_list = self.remove_keys_and_make_lists(self._hierarchy_dict)

	@property
	def hierarchy_list(self) -> list[Any]:
		return self._hierarchy_list

	@property
	def hierarchy_dict(self) -> dict[Any, Any]:
		return self._hierarchy_dict

	@property
	def path_dict(self) -> dict[Any, Any]:
		return self._path_dict

	def get_hierarchy_dict(self, items: list[Item]) -> dict[Any, Any] | Any | dict[int, dict[str, Any]]:
		hierarchy = {}
		for item in items:
			l = self.check_parent(item, {})
			if hierarchy:
				hierarchy = self.check_children(hierarchy, l)
			else:
				hierarchy = l
		return hierarchy

	def check_parent(self, item, item_data) -> Any | dict[int, dict[str, Any]]:
		if type(item).__name__ not in ["Session", "Instance"]:
			if isinstance(item.parent, Session):
				item_data = {item.name: {"@type": type(item).__name__, "@name": item.name, "children": item_data}}
			else:
				item_data = {item.name: {"@parent": item.parent.name, "@type": type(item).__name__, "@name": item.name, "children": item_data}}
		if item.parent is not None:
			item_data = self.check_parent(item.parent, item_data)
		return item_data

	def check_children(self, hierarchy, l) -> dict[Any, Any] | Any:
		for data in l:
			if data in hierarchy:
				hierarchy[data]['children'] = self.check_children(hierarchy[data].get('children', {}), l[data].get('children', {}))
			else:
				return {**hierarchy, **l}
		return hierarchy

	def remove_keys_and_make_lists(self, hierarchy: dict) -> list[Any]:
		array = []
		for k, v in hierarchy.items():
			v['children'] = self.remove_keys_and_make_lists(v['children'])
			if v['@type'] == "Function":  # since Function is the minimal unit in pytest
				v.pop("children", None)
			array.append(v)
			self._temp_dict.update(v)
		return array

	def path_collection(self, session: Session):
		hierarchy = {}
		for item in session.items:
			l = {}
			cur_h = {}
			parameterized = item.nodeid.find('[')
			if parameterized < 0:
				path = item.nodeid.split('/')
			else:
				path = item.nodeid[0:parameterized].split('/')
				path[-1] = path[-1] + item.nodeid[parameterized:]
			pytest_items = path[-1].split('::')
			path[-1] = pytest_items[0]
			pytest_items = pytest_items[1:]
			pytest_items.reverse()
			path.reverse()
			for p in pytest_items:
				l = {
				    p: {
				        "@type": "test",
				        "children": cur_h,
				    },
				}
				cur_h = l
			for p in path:
				l = {
				    p: {
				        "@type": "path",
				        "children": cur_h,
				    },
				}
				cur_h = l

			if hierarchy:
				hierarchy = self.check_children(hierarchy, l)
			else:
				hierarchy = l

		return hierarchy
