#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  conf.py
#
#  Copyright 2013 Gerry <gerry@gerry-ubuntu-laptop>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#

from tornado.options import define


define("server_port", default=8000, type=int, help="The server port")
define("db_host", default="localhost", help="Database host")
define("db_port", default="27017", help="Database port")
define("thumbnail_width", default=128, help="Width of the thumbnail")
define("thumbnail_height", default=128, help="Height of the thumbnail")
