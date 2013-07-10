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
import time
import logging

import tornado.web
import tornado.gen
import tornado.httputil

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("usr")

class MainHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.web.authenticated
    def get(self):
        print "Get in Main Handler"
        name = tornado.escape.xhtml_escape(self.current_user)
        self.render("main.html")

class LoginHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self):
        if self.current_user:
            self.redirect("/")
        else:
            self.render("login.html")

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        db = self.settings['db']
        query = dict(username=self.get_argument("username"),
                     password=self.get_argument("password"))
        usr = yield db.usr.find_one(query)
        if not usr:
            self.redirect("/register")
        else:
            self.set_secure_cookie("usr", query["username"])
            self.redirect("/")

class RegisterHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("register.html")

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        db = self.settings['db']
        usr = yield db.usr.find_one({"username":self.get_argument("username")})

        if not usr:
            doc = dict(username=self.get_argument("username"),
                       password=self.get_argument("password"))
            result = yield db.usr.insert(doc)
            self.set_secure_cookie("usr", doc["username"])
            self.redirect("/")
        else:
            self.redirect("/login")

class LogoutHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self):
        self.clear_cookie("usr")
        self.redirect("/login")

class UploadHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("upload.html")

    @tornado.web.asynchronous
    def post(self):
        for k, v in self.request.files.iteritems():
            logging.info(k)
            for file in v:
                logging.info(file.content_type)
                logging.info(file.filename)
                suffix = '.' + file.filename.split('.').pop().lower()
                file_path = "./static/" + str(int(time.time())) + suffix
                with open(file_path, "w") as f:
                    f.write(file.body)
                    f.close()

        self.finish()
