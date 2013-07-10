#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  main.py
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
import os
import base64
import uuid

import tornado.ioloop
import tornado.web
from tornado.options import define, options
import handler

import motor

define("server_port", default=8000, type=int, help="The server port")
define("db_host", default="localhost", help="Database host")
define("db_port", default="27017", help="Database port")

settings = dict(

# General settings:
    debug=True,
    #gzip=True,
    #log_function=func
    #ui_modules=
    #ui_methods=

# Authentication and security settings:
    cookie_secret=base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes),
    login_url="/login",
    #xsrf_cookies=

# Template settings:
    #autoescape=xhtml_escape
    template_path=os.path.join(os.path.dirname(__file__), "template"),

# Static file settings:
    static_path=os.path.join(os.path.dirname(__file__), "static"),
    #static_url_prefix="/static/"

    db=motor.MotorClient().open_sync().usr_test
)

application = tornado.web.Application([
    (r"/", handler.MainHandler),
    (r"/login", handler.LoginHandler),
    (r"/register", handler.RegisterHandler),
    (r"/logout", handler.LogoutHandler),
    (r"/upload", handler.UploadHandler),
], **settings)

def main():
    tornado.options.parse_command_line()
    application.listen(options.server_port)
    tornado.ioloop.IOLoop.instance().start()
    return 0

if __name__ == '__main__':
    main()
