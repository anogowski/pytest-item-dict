#############################################
#	Dual License: BSD-3-Clause AND MPL-2.0	#
#	Copyright (c) 2024, Adam Nogowski		#
#############################################
"""Test-run hierarchy dictionary with outcome tracking and metric aggregation.

This module provides :class:`TestDict`, a sub-class of
:class:`~pytest_item_dict.collect_dict.CollectionDict` that extends the
collection-time hierarchy with per-test outcomes, durations, and markers, then
*aggregates* those metrics upward through the hierarchy so that every parent
node (class, module, folder) exposes summarised counts and total duration.
"""

# Python Imports
from __future__ import annotations

from collections import defaultdict
from typing import Any, Final

# Pytest Imports
from pytest import Config, Item

# Plugin Imports
from pytest_item_dict.item_dict_enums import TestProperties, INIOptions
from pytest_item_dict.collect_dict import CollectionDict


class TestDict(CollectionDict):
	"""Extends :class:`CollectionDict` with per-test metrics and aggregation.

	After a test session completes, calling :meth:`aggregate_counts` populates
	every non-leaf node with ``@counts`` (outcome breakdown) and, when
	durations are enabled, ``@total_duration`` (summed child durations in
	seconds).

	Parameters
	----------
	config : pytest.Config
	    Active pytest configuration object.

	Attributes
	----------
	UNEXECUTED : str
	    Sentinel outcome value (``"unexecuted"``) assigned to tests that were
	    collected but not yet executed.
	_set_outcomes : bool
	    Whether to record individual test outcomes in the hierarchy.
	_set_durations : bool
	    Whether to record individual and aggregated durations in the hierarchy.
	_update_on_test : bool
	    Whether to update the hierarchy dict after each individual test
	    (real-time) rather than only at session end.
	"""

	__test__: bool = False  # Prevent pytest from collecting this class as a test case

	UNEXECUTED: Final[str] = "unexecuted"

	def __init__(self, config: Config) -> None:
		super().__init__(config=config)
		self._add_markers: bool = bool(config.getini(name=INIOptions.SET_TEST_MARKERS))
		self._set_durations: bool = bool(config.getini(name=INIOptions.SET_TEST_DURATIONS))
		self._set_outcomes: bool = bool(config.getini(name=INIOptions.SET_TEST_OUTCOMES))
		self._update_on_test: bool = bool(config.getini(name=INIOptions.UPDATE_DICT_ON_TEST))

	# ------------------------------------------------------------------
	# Properties
	# ------------------------------------------------------------------

	@property
	def set_outcomes(self) -> bool:
		"""Whether to record individual test outcomes.

		Returns
		-------
		bool
		    Value of the ``set_test_dict_outcomes`` ini option.
		"""
		return self._set_outcomes

	@property
	def set_durations(self) -> bool:
		"""Whether to record individual and aggregated durations.

		Returns
		-------
		bool
		    Value of the ``set_test_dict_durations`` ini option.
		"""
		return self._set_durations

	@property
	def update_on_test(self) -> bool:
		"""Whether to update the hierarchy after every individual test.

		Returns
		-------
		bool
		    Value of the ``update_dict_on_test`` ini option.
		"""
		return self._update_on_test

	# ------------------------------------------------------------------
	# Outcome tracking
	# ------------------------------------------------------------------

	def set_unexecuted_test_outcomes(self) -> None:
		"""Initialise every item's ``@outcome`` attribute to ``"unexecuted"``.

		Called immediately after collection so that tests that are never
		reached (e.g. due to a session-abort) retain a meaningful outcome
		rather than being absent from the hierarchy.
		"""
		if self._set_outcomes:
			for item in self.items:
				setattr(item, TestProperties.OUTCOME, self.UNEXECUTED)
				self.set_outcome_attribute(item=item)

	def set_test_outcomes(self) -> None:
		"""Write each item's current ``outcome`` attribute into the hierarchy.

		Iterates over all items and calls :meth:`set_outcome_attribute` for
		each.  Useful for a final one-shot sync at session end.
		"""
		if self._set_outcomes:
			for item in self.items:
				self.set_outcome_attribute(item=item)

	def set_outcome_attribute(self, item: Item) -> None:
		"""Write *item*'s ``outcome`` attribute into the test-dict hierarchy.

		Parameters
		----------
		item : pytest.Item
		    The test item whose outcome to persist.
		"""
		if self._set_outcomes and hasattr(item, TestProperties.OUTCOME):
			key_path: list[str] = self.get_key_path(path=item.nodeid)
			self.set_attribute(
			    key_path=key_path,
			    key=TestProperties.OUTCOME,
			    value=getattr(item, TestProperties.OUTCOME),
			)

	# ------------------------------------------------------------------
	# Duration tracking
	# ------------------------------------------------------------------

	def set_duration_attribute(self, item: Item) -> None:
		"""Write *item*'s accumulated duration (seconds) into the hierarchy.

		The duration is stored as a plain :class:`float` (seconds) to
		facilitate numeric aggregation in :meth:`aggregate_counts`.

		Parameters
		----------
		item : pytest.Item
		    The test item whose ``duration`` attribute to persist.
		"""
		if self._set_durations and hasattr(item, TestProperties.DURATION):
			key_path: list[str] = self.get_key_path(path=item.nodeid)
			duration_seconds: float = float(getattr(item, TestProperties.DURATION))
			self.set_attribute(
			    key_path=key_path,
			    key=TestProperties.DURATION,
			    value=duration_seconds,
			)

	# ------------------------------------------------------------------
	# Aggregation
	# ------------------------------------------------------------------

	def aggregate_counts(self) -> None:
		"""Recursively aggregate outcome counts and durations through the hierarchy.

		For every non-leaf node (folder, module, class) computes and stores
		``@counts``, a mapping of outcome label to test count.  When
		``set_test_dict_durations`` is enabled, also stores ``@total_duration``
		(float, seconds) at every non-leaf node.

		Leaf nodes are detected structurally: a node is a leaf when it contains
		no child keys whose values are plain dicts (``@``-prefixed attribute
		keys are ignored).

		Notes
		-----
		The method mutates ``_hierarchy`` in place and is idempotent.  It
		should be called once, after all individual outcomes and durations have
		been recorded (i.e. from ``pytest_sessionfinish``).

		Examples
		--------
		Given a two-test module hierarchy after the run::

		    {
		        "test_mod.py": {
		            "test_pass": {"@outcome": "passed"},
		            "test_fail": {"@outcome": "failed"},
		        }
		    }

		After ``aggregate_counts()``::

		    {
		        "@counts": {"passed": 1, "failed": 1, "skipped": 0,
		                    "unexecuted": 0, "total": 2},
		        "test_mod.py": {
		            "@counts": {"passed": 1, "failed": 1, "skipped": 0,
		                        "unexecuted": 0, "total": 2},
		            "test_pass": {"@outcome": "passed"},
		            "test_fail": {"@outcome": "failed"},
		        }
		    }
		"""
		self._aggregate_node(self._hierarchy)

	def _aggregate_node(
	    self,
	    node: dict[str, Any],
	) -> tuple[dict[str, int], float]:
		"""Recursively aggregate a single hierarchy node.

		Parameters
		----------
		node : dict[str, Any]
		    A node from the test-dict hierarchy.  Attribute keys are prefixed
		    with ``"@"``; child nodes are plain keys whose values are ``dict``
		    instances.

		Returns
		-------
		tuple[dict[str, int], float]
		    A 2-tuple of:

		    counts : dict[str, int]
		        Outcome label → count for all leaf tests in this subtree, plus
		        ``"total"`` for the grand total.
		    total_duration : float
		        Sum of all ``@duration`` values (seconds) in this subtree.
		"""
		outcome_key: str = f"@{TestProperties.OUTCOME}"
		duration_key: str = f"@{TestProperties.DURATION}"

		# Structural leaf detection: no non-attribute dict children.
		child_keys: list[str] = [k for k, v in node.items() if not k.startswith("@") and isinstance(v, dict)]

		if not child_keys:
			# ── Leaf node ──────────────────────────────────────────────
			outcome: str = node.get(outcome_key, self.UNEXECUTED)
			duration: float = float(node.get(duration_key, 0.0))
			return {outcome: 1, "total": 1}, duration

		# ── Parent node: aggregate children ────────────────────────────
		counts: defaultdict[str, int] = defaultdict(int)
		total_duration: float = 0.0

		for key in child_keys:
			child_counts, child_duration = self._aggregate_node(node[key])
			for label, count in child_counts.items():
				counts[label] += count
			total_duration += child_duration

		# Guarantee all standard outcome keys are present even when zero.
		for outcome in ("passed", "failed", "skipped", self.UNEXECUTED):
			counts.setdefault(outcome, 0)

		node[f"@{TestProperties.COUNTS}"] = dict(counts)
		if self._set_durations:
			node[f"@{TestProperties.TOTAL_DURATION}"] = total_duration

		return dict(counts), total_duration

	# ------------------------------------------------------------------
	# Session-end runners
	# ------------------------------------------------------------------

	def run_ini_options(self) -> None:
		"""Execute all ini-option-driven metric recording for the test run.

		Iterates over :attr:`items` and calls :meth:`set_marker_attribute`
		and :meth:`set_duration_attribute` for each item when the respective
		ini options are enabled.
		"""
		if self._add_markers or self._set_durations:
			for item in self.items:
				self.set_marker_attribute(item=item)
				self.set_duration_attribute(item=item)
