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

import gridfs
import motor.web
import bson.objectid

import cStringIO
from PIL import Image

from handler import BaseHandler

class ImageUploadHandler(BaseHandler):

    max_size = (1600, 1200)
    accepted_format = {"JPEG", "PNG"}

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
            #logging.info(k)
            for file in v:
                print file.filename, file.content_type, len(file.body)
                try:
                    im = Image.open(cStringIO.StringIO(file.body))
                    print im.format, im.size, im.mode
                    #print im.info
                except IOError:
                    self.write_error(1, err="File invalid!")
                    return

                if im.format not in self.accepted_format:
                    self.write_error(1, err="File format invalid")
                    return

                if im.size[0] > self.max_size[0] or im.size[1] > self.max_size[1]:
                    im.thumbnail(self.max_size, Image.ANTIALIAS)

                out = cStringIO.StringIO()
                im.save(out, im.format)
                fs = yield motor.MotorGridFS(self.settings['db']).open()
                image_id = yield fs.put(out.getvalue(),
                                content_type=file.content_type,
                                filename=file.filename,
                                metadata={'user': self.current_user})

                #logging.info(image_id)

        self.redirect("/images/%s" % str(image_id))

class ImageHandler(BaseHandler):

    clients = [{'large': (1280, 720), 'medium': (640, 480), 'small': (320, 240), 'thumb': (128, 128)},
               {'large': (1024, 768), 'medium': (800, 600), 'small': (128, 128), 'thumb': (100, 100)}]

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, path):
        clientid = self.get_argument("client", None)
        size = self.get_argument("size", None)
        db = self.settings['db']
        fs = yield motor.MotorGridFS(db).open()

        try:
            image =yield fs.get(bson.objectid.ObjectId(path))
        except gridfs.NoFile:
            self.write_error(1, err="File not found")
            return

        self.set_header("Content-Type", image.content_type)

        if not clientid and not size:
            yield image.stream_to_handler(self)
            self.finish()
            return

        if not clientid or int(clientid) >= len(self.clients):
            clientid = 0
        if not size or size not in self.clients[int(clientid)]:
            size = 'medium'

        content = yield image.read()
        im = Image.open(cStringIO.StringIO(content))
        im.thumbnail(self.clients[int(clientid)][size], Image.ANTIALIAS)
        out = cStringIO.StringIO()
        im.save(out, im.format)
        #logging.info(im.format)

        self.write(out.getvalue())
        out.close()
        self.finish()
