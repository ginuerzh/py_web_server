#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  handler.py
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
import tornado.web

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")


class MainHandler(BaseHandler):
    @tornado.web.authenticated
    @tornado.web.asynchronous
    def get(self):
        name = tornado.escape.xhtml_escape(self.current_user)
        self.write("Hello, " + name)
        self.finish()

class LoginHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("login.html")

    @tornado.web.asynchronous
    def post(self):
        self.set_header("Content-Type", "text/plain")
        content = self.get_argument("message")
        if content != "ginuerzh":
            raise tornado.web.HTTPError(403)
        else:
            self.set_secure_cookie("user", content)
            self.redirect("/")
