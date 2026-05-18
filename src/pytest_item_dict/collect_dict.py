#############################################
#	Dual License: BSD-3-Clause AND MPL-2.0	#
#	Copyright (c) 2024, Adam Nogowski		#
#############################################
"""Core hierarchical dictionary builder for pytest items.

This module provides :class:`CollectionDict`, which converts a flat list of
:class:`pytest.Item` objects into a nested Python dictionary keyed by the
components of each item's ``nodeid`` (directory segments, module name, class
name, and function name).

The class is intentionally general-purpose: it stores no per-plugin state and
can be sub-classed (see :class:`~pytest_item_dict.test_dict.TestDict`) to add
richer metrics such as outcomes, durations, and aggregated counts.
"""

# Python Includes
from __future__ import annotations

from typing import Any, Callable

from pytest import Config, Item

from pytest_item_dict.item_dict_enums import INIOptions, CollectTypes


class CollectionDict:
	"""Builds and queries a hierarchical dictionary from a pytest item list.

	The hierarchy mirrors the nodeid structure::

	    {
	        "folder": {
	            "test_module.py": {
	                "TestClass": {
	                    "test_method": {}
	                }
	            }
	        }
	    }

	Attribute keys (e.g. ``@outcome``, ``@markers``) are stored alongside
	child keys using :meth:`set_attribute`.  Sub-element keys (without the
	``@`` prefix) are stored with :meth:`set_sub_element`.

	Parameters
	----------
	config : pytest.Config
	    Active pytest configuration object, used to read ini options.

	Attributes
	----------
	_config : pytest.Config
	    Stored reference to the pytest ``Config`` object.
	_hierarchy : dict[Any, Any]
	    Root of the hierarchical dict.  Populated by
	    :meth:`create_hierarchy_dict` and mutated in place by all ``set_*``
	    methods.  Always anchored at the root; never re-pointed to an inner
	    node.
	_items : list[pytest.Item]
	    Ordered list of collected test items.
	_total_duration : float
	    Cumulative wall-clock duration of the suite (seconds).
	_add_markers : bool
	    Whether to persist pytest markers into the hierarchy.
	"""

	def __init__(self, config: Config) -> None:
		self._config: Config = config
		# Instance-level initialization avoids the mutable-class-variable trap
		# where a shared default dict would bleed state across instances.
		self._hierarchy: dict[Any, Any] = {}
		self._items: list[Item] = []
		self._total_duration: float = 0.0
		self._add_markers: bool = bool(config.getini(name=INIOptions.SET_COLLECT_MARKERS))

	# ------------------------------------------------------------------
	# Properties
	# ------------------------------------------------------------------

	@property
	def hierarchy(self) -> dict[Any, Any]:
		"""Root of the hierarchical dictionary.

		Returns
		-------
		dict[Any, Any]
		    The root mapping whose keys are top-level directory / module
		    names derived from collected item nodeids.
		"""
		return self._hierarchy

	@hierarchy.setter
	def hierarchy(self, hierarchy: dict[Any, Any]) -> None:
		"""Replace the entire hierarchy with *hierarchy*.

		Parameters
		----------
		hierarchy : dict[Any, Any]
		    New root mapping to use.
		"""
		self._hierarchy = hierarchy

	@property
	def items(self) -> list[Item]:
		"""Collected test items.

		Returns
		-------
		list[pytest.Item]
		    The ordered list set by :meth:`create_hierarchy_dict` or via the
		    setter.
		"""
		return self._items

	@items.setter
	def items(self, items: list[Item]) -> None:
		"""Replace the stored item list.

		Parameters
		----------
		items : list[pytest.Item]
		    New ordered list of collected test items.
		"""
		self._items = items

	@property
	def total_duration(self) -> float:
		"""Total suite wall-clock duration in seconds.

		Returns
		-------
		float
		    Sum of all test durations recorded for this collection.
		"""
		return self._total_duration

	@total_duration.setter
	def total_duration(self, duration: float) -> None:
		"""Set the total suite duration.

		Parameters
		----------
		duration : float
		    Wall-clock duration in seconds.
		"""
		self._total_duration = duration

	# ------------------------------------------------------------------
	# Hierarchy construction
	# ------------------------------------------------------------------

	def create_hierarchy_dict(self, items: list[Item]) -> None:
		"""Populate ``_hierarchy`` from a flat list of collected items.

		Each item's ``nodeid`` is decomposed via :meth:`get_key_path` and
		inserted into ``_hierarchy`` so that the resulting structure mirrors
		the file-system and class layout.

		Parameters
		----------
		items : list[pytest.Item]
		    Ordered list of collected test items from
		    ``pytest_collection_modifyitems``.
		"""
		self._items = items
		for item in self._items:
			key_path: list[str] = self.get_key_path(path=item.nodeid)
			self._set_default(key_path=key_path)

	def get_key_path(self, path: str) -> list[str]:
		"""Decompose a nodeid or file-system path into a hierarchy key list.

		Splits on ``/`` for directory segments, then on ``::`` for the class /
		function components of the final segment.  Parametrized test variants
		(e.g. ``test_fn[a-b]``) are kept intact as leaf keys so that each
		variant is represented as a separate, independently counted leaf node.

		Parameters
		----------
		path : str
		    A pytest nodeid (e.g. ``"a/b/test_mod.py::MyClass::test_fn[p]"``)
		    or a plain file-system path.

		Returns
		-------
		list[str]
		    Ordered list of keys suitable for traversing ``_hierarchy``.

		Examples
		--------
		>>> cdict.get_key_path("a/b/test_mod.py::MyClass::test_fn")
		['a', 'b', 'test_mod.py', 'MyClass', 'test_fn']
		>>> cdict.get_key_path("test_fn[p1-p2]")
		['test_fn[p1-p2]']
		"""
		key_path: list[str] = path.split(sep="/")
		if "::" in key_path[-1]:
			last_segment: str = key_path.pop()
			key_path.extend(last_segment.split(sep="::"))
		return key_path

	def _set_default(self, key_path: list[str]) -> None:
		"""Ensure every node on *key_path* exists in ``_hierarchy``.

		Traverses ``_hierarchy`` using a **local** cursor so that
		``self._hierarchy`` always remains anchored at the root dict.
		Missing intermediate nodes are created as plain empty dicts.

		Parameters
		----------
		key_path : list[str]
		    Ordered sequence of keys from root to leaf.

		Notes
		-----
		The previous implementation re-assigned ``self._hierarchy`` on each
		iteration, causing it to drift to the innermost leaf of the last
		processed item.  This method fixes that by using a separate local
		variable for traversal.
		"""
		current: dict[Any, Any] = self._hierarchy
		for part in key_path:
			current = current.setdefault(part, {})

	def _set_new_value(self, key_path: list[str], value: Any) -> None:
		"""Write *value* at the location identified by *key_path*.

		Traverses ``_hierarchy`` from the root, creating missing intermediate
		nodes as needed, and sets the terminal key to *value*.

		Parameters
		----------
		key_path : list[str]
		    Ordered sequence of keys; the last key is set to *value*.
		value : Any
		    The value to store at
		    ``_hierarchy[key_path[0]][...][key_path[-1]]``.
		"""
		current: dict[str, Any] = self._hierarchy
		for key in key_path[:-1]:
			current = current.setdefault(key, {})
		current[key_path[-1]] = value

	def get_value_from_key_path(self, key_path: list[str]) -> Any | None:
		"""Retrieve the value stored at *key_path* in ``_hierarchy``.

		Parameters
		----------
		key_path : list[str]
		    Ordered sequence of keys from root to the target node.

		Returns
		-------
		Any or None
		    The stored value, or ``None`` if any key along the path is absent.
		"""
		current: Any = self._hierarchy
		for key in key_path:
			if not isinstance(current, dict) or key not in current:
				return None
			current = current[key]
		return current

	# ------------------------------------------------------------------
	# Attribute / sub-element setters
	# ------------------------------------------------------------------

	def set_attribute(self, key_path: list[str], key: str, value: Any) -> None:
		"""Store *value* as an attribute at the node identified by *key_path*.

		Attribute keys are prefixed with ``"@"`` to distinguish them from
		child-node keys.  If *key* already starts with ``"@"`` it is left
		unchanged.

		Parameters
		----------
		key_path : list[str]
		    Path to the target parent node.
		key : str
		    Attribute name; ``"@"`` is prepended if absent.
		value : Any
		    Value to store.
		"""
		if not key.startswith("@"):
			key = f"@{key}"
		key_path.append(key)
		self._set_new_value(key_path=key_path, value=value)
		key_path.pop()

	def set_marker_attribute(self, item: Item) -> None:
		"""Write the item's own markers as an ``@markers`` attribute.

		Does nothing when ``_add_markers`` is ``False`` or the item carries
		no own markers.

		Parameters
		----------
		item : pytest.Item
		    The test item whose :attr:`~pytest.Item.own_markers` to persist.
		"""
		if self._add_markers and item.own_markers:
			key_path: list[str] = self.get_key_path(path=item.nodeid)
			markers: list[str] = [marker.name for marker in item.own_markers]
			self.set_attribute(key_path=key_path, key="@markers", value=markers)

	def _dict_on_parent_types(
	    self,
	    search_type: list[str | CollectTypes],
	    property_dict: dict[Any, Any],
	    func: Callable[[list[str], str, Any], None],
	) -> None:
		"""Apply *func* to every parent node whose type is in *search_type*.

		``Session`` nodes and the virtual root node (``nodeid == "."``) are
		always skipped.

		Parameters
		----------
		search_type : list[str or CollectTypes]
		    Node type names to match (``type(parent).__name__``).
		property_dict : dict[Any, Any]
		    Key-value pairs passed individually to *func*.
		func : callable
		    Either :meth:`set_attribute` or :meth:`set_sub_element`.
		"""
		for item in self.items:
			for parent in item.iter_parents():
				type_name: str = type(parent).__name__
				if type_name in search_type and type_name != "Session" and parent.nodeid != ".":
					key_path: list[str] = self.get_key_path(path=parent.nodeid)
					for key, value in property_dict.items():
						func(key_path, key, value)

	def set_attribute_on_parent_types(
	    self,
	    search_type: list[str | CollectTypes],
	    key: str,
	    value: Any,
	) -> None:
		"""Write a single attribute on every matching parent node.

		Parameters
		----------
		search_type : list[str or CollectTypes]
		    Node type names to match.
		key : str
		    Attribute key (``"@"`` prepended if absent).
		value : Any
		    Attribute value.
		"""
		for item in self.items:
			for parent in item.iter_parents():
				type_name: str = type(parent).__name__
				if type_name in search_type and type_name != "Session" and parent.nodeid != ".":
					key_path: list[str] = self.get_key_path(path=parent.nodeid)
					self.set_attribute(key_path=key_path, key=key, value=value)

	def set_attribute_dict_to_types(
	    self,
	    search_type: list[str | CollectTypes],
	    attr_dict: dict[Any, Any],
	) -> None:
		"""Write multiple attributes on every matching parent node.

		Parameters
		----------
		search_type : list[str or CollectTypes]
		    Node type names to match.
		attr_dict : dict[Any, Any]
		    Key-value pairs to store; ``"@"`` is prepended to each key if absent.
		"""
		self._dict_on_parent_types(
		    search_type=search_type,
		    property_dict=attr_dict,
		    func=self.set_attribute,
		)

	def set_sub_element(self, key_path: list[str], key: str, value: Any) -> None:
		"""Store *value* as a sub-element (non-attribute) at *key_path*.

		Sub-element keys must not start with ``"@"``; a leading ``"@"`` is
		stripped automatically.

		Parameters
		----------
		key_path : list[str]
		    Path to the target parent node.
		key : str
		    Sub-element key; leading ``"@"`` is removed if present.
		value : Any
		    Value to store.
		"""
		if key.startswith("@"):
			key = key[1:]
		key_path.append(key)
		self._set_new_value(key_path=key_path, value=value)

		key_path.pop()

	def set_sub_element_dict(self, key_path: list[str], sub_dict: dict[Any, Any]) -> None:
		"""Write every key-value pair in *sub_dict* as sub-elements at *key_path*.

		Parameters
		----------
		key_path : list[str]
		    Path to the target parent node.
		sub_dict : dict[Any, Any]
		    Mapping of sub-element keys to values; leading ``"@"`` is removed
		    from each key if present.
		"""
		for key, value in sub_dict.items():
			self.set_sub_element(key_path=key_path, key=key, value=value)

	def set_sub_element_dict_to_types(
	    self,
	    search_type: list[str | CollectTypes],
	    sub_dict: dict[Any, Any],
	) -> None:
		"""Write a sub-element dict on every matching parent node.

		Parameters
		----------
		search_type : list[str or CollectTypes]
		    Node type names to match.
		sub_dict : dict[Any, Any]
		    Key-value pairs to store as sub-elements.
		"""
		self._dict_on_parent_types(
		    search_type=search_type,
		    property_dict=sub_dict,
		    func=self.set_sub_element,
		)

	def _set_item_attribute_per_item(
	    self,
	    attributes: list[str],
	    func: Callable[[list[str], str, Any], None],
	) -> None:
		"""Apply *func* for each named attribute found on each item.

		Parameters
		----------
		attributes : list[str]
		    Attribute names to look up via :func:`hasattr` / :func:`getattr`.
		func : callable
		    Either :meth:`set_attribute` or :meth:`set_sub_element`.
		"""
		for item in self.items:
			key_path: list[str] = self.get_key_path(path=item.nodeid)
			for attribute in attributes:
				if hasattr(item, attribute):
					func(key_path, attribute, getattr(item, attribute))

	def set_item_attributes_as_attribute(self, attributes: list[str]) -> None:
		"""Store named item attributes as ``@``-prefixed hierarchy attributes.

		Parameters
		----------
		attributes : list[str]
		    Names of :class:`pytest.Item` attributes to persist.
		"""
		self._set_item_attribute_per_item(attributes=attributes, func=self.set_attribute)

	def set_item_attributes_as_sub_element(self, attributes: list[str]) -> None:
		"""Store named item attributes as sub-element hierarchy keys.

		Parameters
		----------
		attributes : list[str]
		    Names of :class:`pytest.Item` attributes to persist.
		"""
		self._set_item_attribute_per_item(attributes=attributes, func=self.set_sub_element)

	def run_ini_options(self) -> None:
		"""Execute all marker-related ini-option logic for collected items.

		Called by
		:meth:`~pytest_item_dict.plugin.ItemDictPlugin.pytest_collection_modifyitems`
		after the hierarchy has been populated.
		"""
		if self._add_markers:
			for item in self.items:
				self.set_marker_attribute(item=item)

	def run_hooks(self) -> None:
		"""Invoke registered plugin hooks.

		Reserved for future use; currently a no-op placeholder.
		"""
		self._config.hook
