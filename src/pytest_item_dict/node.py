class Node(object):

	def __init__(self, name, parent=None):
		self._name = name
		self._children = []
		self._parent = parent

		if parent is not None:
			parent.addChild(self)

	def addChild(self, child):
		self._children.append(child)

	def name(self):
		return self._name

	def setName(self, name):
		self._name = name

	def child(self, row):
		return self._children[row]

	def childCount(self):
		return len(self._children)

	def parent(self):
		return self._parent


class Dir_Node(Node):

	def __init__(self, name, parent=None):
		super(Dir_Node, self).__init__(name, parent)


class Module_Node(Node):

	def __init__(self, name, parent=None):
		super(Module_Node, self).__init__(name, parent)


class Class_Node(Node):

	def __init__(self, name, parent=None):
		super(Class_Node, self).__init__(name, parent)


class Test_Node(Node):

	def __init__(self, name, parent=None):
		super(Test_Node, self).__init__(name, parent)
