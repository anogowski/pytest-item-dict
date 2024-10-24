#############################################
#	Dual License: BSD-3-Clause AND MPL-2.0	#
#	Copyright (c) 2024, Adam Nogowski		#
#############################################

# Python Includes
from pathlib import Path

# Pip Includes
from dict2xml import dict2xml
# PyTest Includes
import pytest


def check_parent(item, item_data):
	if type(item).__name__ not in ["Session", "Instance"]:
		item_data = {hash(type(item).__name__ + item.name): {"type": type(item).__name__, "title": item.name, "children": item_data}}
	if item.parent is not None:
		item_data = check_parent(item.parent, item_data)
	return item_data


def check_children(hierarchy, l):
	for data in l:
		if data in hierarchy:
			hierarchy[data]['children'] = check_children(hierarchy[data].get('children', {}), l[data].get('children', {}))
		else:
			return {**hierarchy, **l}
	return hierarchy


def remove_keys_and_make_lists(hierarchy):
	array = []
	for k, v in hierarchy.items():
		v['children'] = remove_keys_and_make_lists(v['children'])
		if v['type'] == "Function":  # since Function is the minimal unit in pytest
			array.append({'type': v['type'], 'title': v['title']})
		else:
			array.append({'type': v['type'], 'title': v['title'], 'children': v['children']})
	return array


def classic_collection(session):
	hierarchy = {}
	for item in session.items:
		l = check_parent(item, {})
		if hierarchy:
			hierarchy = check_children(hierarchy, l)
		else:
			hierarchy = l
	return hierarchy


def path_collection(session):
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
			l = {"pytest_unit" + p: {"type": "pytest_unit", "title": p, "children": cur_h}}
			cur_h = l
		for p in path:
			l = {"path" + p: {"type": "path", "title": p, "children": cur_h}}
			cur_h = l

		if hierarchy:
			hierarchy = check_children(hierarchy, l)
		else:
			hierarchy = l

	return hierarchy


def pytest_collection_finish(session):
	collect_type = "classic"
	hierarchy = {}
	if collect_type == 'classic':
		hierarchy = classic_collection(session)
	elif collect_type == 'path':
		hierarchy = path_collection(session)

	hierarchy = remove_keys_and_make_lists(hierarchy)

	output_file: str = Path(f"{__file__}/../../../output/reports/collection.xml").as_posix()
	with open(output_file, "w+") as f:
		xml_lines: list[str] = [
		    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' + '\n',
		    '<collection-report>',
		    dict2xml(data=hierarchy, indent="\t", data_sorter=None),
		    '\n' + '</collection-report>',
		]
		f.writelines(xml_lines)
