#############################################
#	Dual License: BSD-3-Clause AND MPL-2.0	#
#	Copyright (c) 2024, Adam Nogowski		#
#############################################

import os

os.system(command="mkdocs build")
os.system(command="mkdocs gh-deploy")
