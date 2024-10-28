#############################################
#	Dual License: BSD-3-Clause AND MPL-2.0	#
#	Copyright (c) 2024, Adam Nogowski		#
#############################################

# Python Includes
import json
from pathlib import Path

# Pip Includes
from data_to_xml.xml_converter import XMLConverter

# PyTest Includes
import pytest
from pytest import Session, Config

# Plugin Includes
from pytest_item_dict.items_dict import ItemsDict


def pytest_collection_finish(session: Session):
	items_dict: ItemsDict = ItemsDict(session=session)
	write_json_file(name="items", json_str=json.dumps(obj=items_dict.collect_dict))
	write_xml_file(name="items", items_dict=items_dict.collect_dict)
	session.config.pluginmanager.register(plugin=items_dict, name="items_dict")


def pytest_unconfigure(config: Config):
	items_dict: object | None = config.pluginmanager.getplugin(name="items_dict")
	if items_dict is not None:
		config.pluginmanager.unregister(plugin=items_dict)


def write_json_file(name: str, json_str: str):
	output_file: str = Path(f"{__file__}/../../../output/reports/collect_{name}.json").as_posix()
	Path(output_file).parent.mkdir(mode=764, parents=True, exist_ok=True)
	with open(file=output_file, mode="w+") as f:
		f.write(json_str + "\n")


def write_xml_file(name: str, items_dict: dict):
	output_file: str = Path(f"{__file__}/../../../output/reports/collect_{name}.xml").as_posix()
	xml: XMLConverter = XMLConverter(my_dict=items_dict, root_node="pytest")
	Path(output_file).parent.mkdir(mode=764, parents=True, exist_ok=True)
	with open(file=output_file, mode="w+") as f:
		f.writelines(xml.formatted_xml)
