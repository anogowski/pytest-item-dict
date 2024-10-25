#############################################
#	Dual License: BSD-3-Clause AND MPL-2.0	#
#	Copyright (c) 2024, Adam Nogowski		#
#############################################

# Python Includes
from pathlib import Path
import os
from typing import Callable

# Pip Includes
from dict2xml import dict2xml, DataSorter

# PyTest Includes
import pytest

# Plugin Includes
from pytest_item_dict.items_dict import ItemsDict
from pytest_item_dict.attributes_dict import AttributesDict
from pytest_item_dict.dict_2_xml import XML_Converter


def _to_xml(data: dict) -> str:
	return dict2xml(data=data, indent="	", data_sorter=DataSorter.never(), iterables_repeat_wrap=False)


def pytest_collection_finish(session: pytest.Session):

	items_dict: ItemsDict = ItemsDict(session=session)
	attr_dict: AttributesDict = AttributesDict(session=session)

	write_file(append_name="hierarchy_dict", values=items_dict.hierarchy_dict)
	write_file(append_name="hierarchy_list", values=items_dict.hierarchy_list)
	write_file(append_name="temp_dict", values=items_dict._temp_dict)
	write_file(append_name="path_dict", values=items_dict.path_dict)

	write_file(append_name='attr_h_dict', values=attr_dict.hierarchy_dict)
	write_file(append_name='attr_h_list', values=attr_dict.hierarchy_list)
	# write_file(append_name='attr_a_dict', values=attr_dict._attr_dict)
	# write_file(append_name='attr_t_dict', values=attr_dict._temp_attr)

	test_xml()


def write_file(append_name: str, values: dict | list):
	output_file: str = Path(f"{__file__}/../../../output/reports/collect_{append_name}.xml").as_posix()
	xml: XML_Converter = XML_Converter(my_dict=values, root_node="test")
	Path(output_file).parent.mkdir(mode=764, parents=True, exist_ok=True)
	with open(file=output_file, mode="w+") as f:
		f.writelines(xml.formatted_xml)


def test_xml():
	output_file: str = Path(f"{__file__}/../../../output/reports/test_{XML_Converter.dict2xml.__qualname__}.xml").as_posix()
	mydict = {
	    'name': 'The Andersson\'s',
	    'size': 4,
	    'members': {
	        'total-age': 62,
	        'child': [
	            {
	                '@name': 'Tom',
	                '@sex': 'male',
	            },
	            {
	                '@name': 'Betty',
	                '@sex': 'female',
	                'grandchild': [
	                    {
	                        '@name': 'herbert',
	                        '@sex': 'male',
	                    },
	                    {
	                        '@name': 'lisa',
	                        '@sex': 'female',
	                    },
	                ]
	            },
	        ]
	    },
	}
	xml: XML_Converter = XML_Converter(mydict, root_node='family')
	Path(output_file).parent.mkdir(mode=764, parents=True, exist_ok=True)
	with open(file=output_file, mode="w+") as f:
		f.writelines(xml.formatted_xml)
