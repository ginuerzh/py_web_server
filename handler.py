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

import logging

import tornado.web
import tornado.gen
from tornado.options import options

import motor.web

class BaseRequestHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("usr")

    def write_error(self, status_code, **kwargs):
        result = dict(r=status_code, err=kwargs.get("err", ""))

        self.write(result)
        self.finish()

class MainHandler(BaseRequestHandler):
    @tornado.web.asynchronous
    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self):
        db = self.settings['db']
        usr = yield db.usr.find_one({'username': self.current_user}, {'images': 1})

        if not usr:
            self.write_error(1, err="User not found!")
            return
        cursor = db.fs.files.find({'metadata.user': self.current_user}).sort("uploadDate", -1).limit(10)
        images = []
        while (yield cursor.fetch_next):
            doc = cursor.next_object()
            images.append(doc['_id'])

        self.render("main.html", images=[])

class LoginHandler(BaseRequestHandler):
    @tornado.web.asynchronous
    def get(self):
        if self.current_user:
            self.redirect("/")
        else:
            #self.write_error(1, err="Login please!")
            self.render("login.html")
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        db = self.settings['db']
        query = dict(username=self.get_argument("username", ""),
                     password=self.get_argument("password", ""))
        usr = yield db.usr.find_one(query)
        if not usr:
            self.redirect("/register")
        else:
            self.set_secure_cookie("usr", query["username"])
            next = self.get_argument("next", '')
            logging.info("next uri: %s" % next)
            if next:
                self.redirect(next)
            else:
                self.redirect("/")

class RegisterHandler(BaseRequestHandler):
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

class LogoutHandler(BaseRequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.clear_cookie("usr")
        self.redirect("/login")
