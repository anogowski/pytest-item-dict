#############################################
#	Dual License: BSD-3-Clause AND MPL-2.0	#
#	Copyright (c) 2024, Adam Nogowski		#
#############################################

# Python Imports
from typing import Any
from pathlib import Path
import json

# Pip Includes
from data_to_xml.xml_converter import XMLConverter

# Pytest Imports
import pytest
from pytest import Session, Config, Item

# Plugin Imports
from pytest_item_dict.plugin import ItemDictPlugin, ITEM_DICT_PLUGIN_NAME
from pytest_item_dict.item_dict_enums import CollectTypes


def write_json_file(json_str: str, prefix: str = "collect", name: str = "hierarchy"):
	output_file: str = Path(f"{__file__}/../output/reports/{prefix}_{name}.json").as_posix()
	Path(output_file).parent.mkdir(mode=764, parents=True, exist_ok=True)
	with open(file=output_file, mode="w+") as f:
		f.write(json_str + "\n")


def write_xml_file(items_dict: dict, prefix: str = "collect", name: str = "hierarchy"):
	output_file: str = Path(f"{__file__}/../output/reports/{prefix}_{name}.xml").as_posix()
	xml: XMLConverter = XMLConverter(my_dict=items_dict, root_node="pytest")
	Path(output_file).parent.mkdir(mode=764, parents=True, exist_ok=True)
	with open(file=output_file, mode="w+") as f:
		f.writelines(xml.formatted_xml)


def pytest_collection_modifyitems(session: Session, config: Config, items: list[Item]) -> None:
	item_dict: ItemDictPlugin | Any | None = session.config.pluginmanager.get_plugin(name=ITEM_DICT_PLUGIN_NAME)
	if item_dict:
		write_xml_file(items_dict=item_dict.test_dict.hierarchy, prefix="test")
		write_json_file(json_str=json.dumps(obj=item_dict.test_dict.hierarchy), prefix="test")


def pytest_collection_finish(session: Session):
	item_dict: ItemDictPlugin | Any | None = session.config.pluginmanager.get_plugin(name=ITEM_DICT_PLUGIN_NAME)
	if item_dict:
		write_xml_file(items_dict=item_dict.collect_dict.hierarchy, prefix="collect")
		write_json_file(json_str=json.dumps(obj=item_dict.collect_dict.hierarchy), prefix="collect")


def pytest_sessionfinish(session: Session):
	item_dict: ItemDictPlugin | Any | None = session.config.pluginmanager.get_plugin(name=ITEM_DICT_PLUGIN_NAME)
	if item_dict:
		write_xml_file(items_dict=item_dict.test_dict.hierarchy, prefix="test")
		write_json_file(json_str=json.dumps(obj=item_dict.test_dict.hierarchy), prefix="test")
