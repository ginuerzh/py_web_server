#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  imagehandler.py
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
import bson.objectid

import cStringIO
from PIL import Image

from handler import BaseHandler

class ImageUploadHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.web.authenticated
    def get(self):
        self.render("upload.html")

    @tornado.web.asynchronous
    @tornado.web.authenticated
    @tornado.gen.coroutine
    def post(self):
        if not self.request.files or len(self.request.files) == 0:
            self.finish()
            return

        for k, v in self.request.files.iteritems():
            logging.info(k)
            for file in v:
                logging.info(file.content_type)
                logging.info(file.filename)

                fs = yield motor.MotorGridFS(self.settings['db']).open()
                original = yield fs.put(file.body,
                                content_type=file.content_type,
                                filename=file.filename,
                                metadata={'user': self.current_user})

                logging.info(original)

        self.redirect("/images/%s" % str(original))


class ImageHandler(motor.web.GridFSHandler):
    def get_cache_time(self, path, modified, mime_type):
        return 86400    # 24 hours

    def get_gridfs_file(self, fs, path):
        return fs.get(file_id=bson.objectid.ObjectId(path))

def check_and_resize(db, path, size):
    origin_id = bson.objectid.ObjectId(path)
    fs = yield motor.MotorGridFS(db).open()

    file = yield db.fs.files.find_one({'metadata.origin_id': origin_id,
                        'metadata.size': size})
    if file:
        logging.info("find one small image %s" % file['_id'])
        yield file['_id']
    else:
        logging.info('small image not exist')
        original = yield fs.get(origin_id)
        content = yield original.read()
        im = Image.open(cStringIO.StringIO(content))
        im.thumbnail((options.thumbnail_width, options.thumbnail_height),
            Image.ANTIALIAS)
        #print im.format, "%dx%d" % im.size, im.mode
        out = cStringIO.StringIO()
        im.save(out, im.format)
        yield fs.put(out.getvalue(),
                        content_type=original.content_type,
                        metadata={'origin_id': origin_id, 'size': size})


class SmallImageHandler(ImageHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, path):
        small = yield check_and_resize(self.settings['db'], path, 'small')
        yield motor.web.GridFSHandler.get(self, small)

