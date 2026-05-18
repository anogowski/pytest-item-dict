#############################################
#	Dual License: BSD-3-Clause AND MPL-2.0	#
#	Copyright (c) 2024, Adam Nogowski		#
#############################################

# Python Imports
from copy import deepcopy
from typing import Any
from pathlib import Path
import json

# Pip Includes
from data_to_xml.xml_converter import XMLConverter

# Pytest Imports
from pytest import Session

# Plugin Imports
from pytest_item_dict.plugin import ItemDictPlugin, ITEM_DICT_PLUGIN_NAME


def write_json_file(hierarchy: dict[str, Any], prefix: str = "collect", name: str = "hierarchy") -> None:
	output_file: str = Path(f"{__file__}/../output/reports/{prefix}_{name}.json").as_posix()
	Path(output_file).parent.mkdir(mode=0o764, parents=True, exist_ok=True)
	with open(file=output_file, mode="w+") as f:
		f.write(json.dumps(obj=hierarchy, indent=2) + "\n")


def write_xml_file(hierarchy: dict[str, Any], prefix: str = "collect", name: str = "hierarchy") -> None:
	output_file: str = Path(f"{__file__}/../output/reports/{prefix}_{name}.xml").as_posix()
	xml: XMLConverter = XMLConverter(my_dict=hierarchy, root_node="pytest")
	Path(output_file).parent.mkdir(mode=0o764, parents=True, exist_ok=True)
	with open(file=output_file, mode="w+") as f:
		f.writelines(xml.formatted_xml)


def pytest_collection_finish(session: Session) -> None:
	item_dict: ItemDictPlugin | Any | None = session.config.pluginmanager.get_plugin(name=ITEM_DICT_PLUGIN_NAME)
	if item_dict:
		# collect_hierarchy.* — pure structure snapshot (no outcomes/durations)
		write_json_file(hierarchy=item_dict.collect_dict.hierarchy, prefix="collect")
		write_xml_file(hierarchy=item_dict.collect_dict.hierarchy, prefix="collect")
		# test_unexecuted_hierarchy.* — all items "unexecuted" with aggregated @counts
		unexecuted_snapshot: dict[str, Any] = deepcopy(item_dict.test_dict.hierarchy)
		item_dict.test_dict._aggregate_node(unexecuted_snapshot)
		write_json_file(hierarchy=unexecuted_snapshot, prefix="test_unexecuted")
		write_xml_file(hierarchy=unexecuted_snapshot, prefix="test_unexecuted")


def pytest_sessionfinish(session: Session) -> None:
	item_dict: ItemDictPlugin | Any | None = session.config.pluginmanager.get_plugin(name=ITEM_DICT_PLUGIN_NAME)
	if item_dict:
		# test_hierarchy.* — final outcomes + aggregated @counts (computed by the plugin)
		write_json_file(hierarchy=item_dict.test_dict.hierarchy, prefix="test")
		write_xml_file(hierarchy=item_dict.test_dict.hierarchy, prefix="test")
