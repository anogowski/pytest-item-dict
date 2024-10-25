"""
Simple xml serializer.
@author Reimund Trost 2013
@updater Thomas William 2018 - Added Attributes
@updater Adam Nogowski 2024 - Added Types and Formatting
"""

from typing import Any, Literal
import xml.etree.ElementTree as ET


class XML_Converter:

	def __init__(self, my_dict: dict, root_node: str | None = None) -> None:
		xml_heading: str = r'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' + "\n"
		self._raw_xml = xml_heading + self.dict2xml(my_dict=my_dict, root_node=root_node)

		element: ET.Element = ET.XML(text=self._raw_xml)
		ET.indent(tree=element, space="\t")

		self._formatted_xml: str = xml_heading + ET.tostring(element=element, encoding="UTF-8").decode(encoding="UTF-8")

	@property
	def formatted_xml(self) -> str:
		return self._formatted_xml

	@property
	def raw_xml(self) -> str:
		return self._raw_xml

	def dict2xml(self, my_dict, root_node=None):
		wrap: bool = False if None == root_node or isinstance(my_dict, list) else True
		root: None | Any | Literal['objects'] = "objects" if None == root_node else root_node
		root_singular: Any | str | None = root[:-1] if 's' == root[-1] and None == root_node else root
		xml: str = ''
		attr: str = ''
		children: list[Any] = []

		if isinstance(my_dict, dict):
			# print(d)
			for key, value in my_dict.items():
				if isinstance(value, dict):
					children.append(self.dict2xml(my_dict=value, root_node=key))
				elif isinstance(value, list):
					children.append(self.dict2xml(my_dict=value, root_node=key))
				elif key[0] == '@':
					attr = attr + ' ' + key[1::] + '="' + str(object=value) + '"'
				else:
					xml = '<' + key + ">" + str(object=value) + '</' + key + '>'
					children.append(xml)

		if isinstance(my_dict, list):
			for value in my_dict:
				children.append(self.dict2xml(value, root_singular))

		end_tag = '>' if 0 < len(children) else '/>'

		if wrap or isinstance(my_dict, dict):
			xml = '<' + root + attr + end_tag

		if 0 < len(children):
			for child in children:
				xml = xml + child

			if wrap or isinstance(my_dict, dict):
				xml = xml + '</' + root + '>'

		return xml
