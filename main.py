#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):

	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

class Blog(db.Model):
	title = db.StringProperty(required = True)
	post_body = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)
		


class MainPage(Handler):
	
	def render_form(self, title="", post_body="", error=""):
		self.render("frontpage.html", title = title, post_body = post_body, error = error)


	def get(self):
		self.render_form()

	def post(self):

		title = self.request.get("title")
		post_body = self.request.get("post_body")

		if (not title) or (not post_body):
			error = "We need both a title and some content!"
			self.render_form(title, post_body, error)

		else:
			a = Blog(title = title, post_body = post_body)
			a.put()

			self.redirect("/blog")




class BlogPosts(Handler):
	def render_blog(self, title="", post_body="", error=""):
		posts = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT 5")

		self.render("blog.html", title = title, post_body = post_body, error = error, posts = posts)


	def get(self):
		self.render_blog()

	def post(self):
		title = self.request.get("title")
		post_body = self.request.get("post_body")

class ViewPostHandler(webapp2.RequestHandler):
    def get(self, id):
    	post_id = self.request.get('id')
        id = Blog.get_by_id( int(post_id) )



app = webapp2.WSGIApplication([
	('/blog/newpost', MainPage),
	('/blog', BlogPosts),
	webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
	], debug=True)
