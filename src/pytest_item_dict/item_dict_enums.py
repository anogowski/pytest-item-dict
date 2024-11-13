#############################################
#	Dual License: BSD-3-Clause AND MPL-2.0	#
#	Copyright (c) 2024, Adam Nogowski		#
#############################################

from enum import StrEnum


class INIOptions(StrEnum):
	CREATE_ITEM_DICT = "create_item_dict"
	UPDATE_DICT_ON_TEST = "update_dict_on_test"
	SET_COLLECT_MARKERS = "set_collect_dict_markers"
	SET_TEST_OUTCOMES = "set_test_dict_outcomes"
	SET_TEST_DURATIONS = "set_test_dict_durations"
	SET_TEST_MARKERS = "set_test_dict_markers"
	SET_TEST_HIERARCHY_OUTCOMES = "set_test_hierarchy_dict_outcomes"
	SET_TEST_HIERARCHY_DURATIONS = "set_test_hierarchy_dict_durations"


class CollectTypes(StrEnum):
	DIR = "Dir"
	PACKAGE = "Package"
	MODULE = "Module"
	CLASS = "Class"
	TEST = "Test"


class TestProperties(StrEnum):
	OUTCOME = "outcome"
	NODEID = "nodeid"
	NAME = "name"
	ORIGINAL_NAME = "original_name"
	MARKERS = "markers"
	DURATION = "duration"
