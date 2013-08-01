#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  imagehandler2.py
#
#  Copyright 2013 Gerry <gerry@gerry-work-tcl>
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
import datetime
import hashlib
import os
import os.path

import tornado.web
import tornado.gen
from tornado.options import options

import motor.web
import bson.objectid

import cStringIO
from PIL import Image

from handler import BaseRequestHandler

accepted_format = {"JPEG":"image/jpeg", "PNG":"image/png"}
datetime_format = "%Y%m%d%H%M%S%f"
subfix = {"JPEG": ".jpg", "PNG": ".png"}

class ImageUploadHandler(BaseRequestHandler):
    max_size = (1600, 1200)

    @tornado.web.asynchronous
    def get(self):
        self.render("upload.html")

    @tornado.web.asynchronous
    def post(self):
        files = self.request.files
        if files is None or "pic_uploaded" not in files:
            self.write_error(1, "File not found")
            return

        self.process()

    def process(self):
        file = self.request.files['pic_uploaded'][0]
        print file.filename, file.content_type, len(file.body)
        try:
            im = Image.open(cStringIO.StringIO(file.body))
            print im.format, im.size, im.mode
            #print im.info
        except IOError:
            self.write_error(1, err="File invalid!")
            return

        if im.format not in accepted_format:
            self.write_error(1, err="File format invalid!")
            return

        if im.size[0] > self.max_size[0] or im.size[1] > self.max_size[1]:
            im.thumbnail(self.max_size, Image.ANTIALIAS)

        out = cStringIO.StringIO()
        im.save(out, im.format)

        content_type = file.content_type
        if content_type is None or len(content_type) == 0:
            content_type = accepted_format[im.format]

        now = datetime.datetime.utcnow()
        nows = now.strftime(datetime_format)
        md5 = hashlib.md5(file.body).hexdigest()
        filename = nows + subfix[im.format]
        print filename

        path =os.path.join(options.upload_path, str(now.year), str(now.month), str(now.day))
        print path
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except os.error:
                self.write_error(1, err="Can't make path %s" % path)
                return

        with open(os.path.join(path, filename), "wb") as f:
            f.write(out.getvalue())

        self.write_error(0, err="Upload success!")

class StaticImageFileHandler(tornado.web.StaticFileHandler):
    clients = {"iphone": {'car_pic_large': {'size': (640, 431), 'path': "large"},
                          'car_pic_large_thumbnail': {'size': (133, 90), 'path': "small"},
                          'car_pic_thumbnail': {'size': (76, 53), 'path': "thm"},
                          'user_profile_pic_large': {'size': (640, 640), 'path': "large"},
                          'user_profile_pic_large_thumbnail': {'size': (120, 120), 'path': "small"},
                          'user_profile_pic_thumbnail': {'size': (60, 60), 'path': "thm"}}
              }

    def initialize(self, path):
        tornado.web.StaticFileHandler.initialize(self, path)

    def parse_url_path(self, url_path):
        id = self.get_argument("id")
        return self.resized_image_path(id)

    def get_cache_time(self, path, modified, mime_type):
        return 60 * 60 * 24


    def resized_image_path(self, url_path):
        client_type = self.get_argument("client", None)
        size = self.get_argument("size", None)
        file_path = self.url_file_path(url_path)

        if not client_type and not size:
            return file_path

        if client_type not in self.clients:
            client_type = "iphone"

        sizes = self.clients[client_type]
        if size not in sizes:
            return file_path

        if not os.access(os.path.join(options.upload_path, file_path), os.F_OK | os.R_OK):
            raise tornado.web.HTTPError(404)
            return

        sub_file_path = os.path.join(os.path.dirname(file_path), client_type, sizes[size]['path'], url_path)
        sub_file = os.path.join(options.upload_path, sub_file_path)

        if os.access(sub_file, os.F_OK | os.R_OK):
            return sub_file_path

        if not os.path.exists(os.path.dirname(sub_file)):
            try:
                os.makedirs(os.path.dirname(sub_file))
            except os.error:
                raise tornado.web.HTTPError(500)
                return

        try:
            im = Image.open(os.path.join(options.upload_path, file_path))
            im.thumbnail(sizes[size]['size'], Image.ANTIALIAS)
            im.save(sub_file, im.format)
        except IOError:
            raise tornado.web.HTTPError(500)
            return

        return sub_file_path

    def url_file_path(self, url):
        parts = url.split(".")
        if len(parts) != 2:
            return None
        try:
            dt = datetime.datetime.strptime(parts[0], datetime_format)
        except ValueError:
            return None
        return os.path.join(str(dt.year), str(dt.month), str(dt.day), url)
