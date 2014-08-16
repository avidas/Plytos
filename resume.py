from flask import Blueprint, render_template, request, redirect, url_for, g, abort
from flask.views import MethodView
from models import Resume, Comment, CommentPerSection, User, ToDosPerSection
from flask.ext.mongoengine.wtf import model_form
from flask.ext.login import login_required, current_user
from flask.ext.principal import (identity_loaded, Permission, RoleNeed,
                                UserNeed, AnonymousIdentity, Identity)

import json
from app import app, principals

from collections import namedtuple
from functools import partial

ResumeNeed = namedtuple('resume', ['method', 'value'])
EditResumeNeed = partial(ResumeNeed, 'edit')

class EditResumePermission(Permission):
    def __init__(self, resume_id):
        need = EditResumeNeed(unicode(resume_id))
        super(EditResumePermission, self).__init__(need)

@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    # Set the identity user object
    identity.user = g.user

    # Add the UserNeed to the identity
    if hasattr(g.user, 'id'):
        identity.provides.add(UserNeed(g.user.id))

    # Assuming the User model has a list of roles, update the
    # identity with the roles that the user provides
    # Currently roles does not get populated
    if hasattr(g.user, 'roles'):
        for role in g.user.roles:
            identity.provides.add(RoleNeed(role.name))

    # Assuming the User model has a list of resumes the user
    # has authored, add the needs to the identity
    
    #if not isinstance(current_user._get_current_object(), AnonymousUser):
    if type(identity) != AnonymousIdentity:
        creator = User.objects.get(email=g.user.email)
        resumes = Resume.objects.filter(user=creator)
        for resume in resumes:
            identity.provides.add(EditResumeNeed(unicode(resume.id)))

resume_app = Blueprint('resume_app', __name__, template_folder='templates')

class ListView(MethodView):
    decorators = [login_required]

    def get(self):
        # Listview only show particular user's resume
        creator = User.objects.get_or_404(email=g.user.email)
        resumes = Resume.objects.filter(user=creator)
        return render_template('resumes/list.html', resumes=resumes)


class DetailView(MethodView):
    decorators = [login_required]
    CHOICES = ((1, "skills"), (2, "experience"), (3, "education"), (4, "activities"), (5, "honors"), (6, "publication"))
    form = model_form(Comment, exclude=['created_at'])

    #These two should be one top method
    @classmethod
    def init_comments(self, resume):
        if len(resume.comments_per_section) == 0:
            for choice in self.CHOICES:
                comment_per_tag = CommentPerSection()
                comment_per_tag.num_comments = 0
                comment_per_tag.index_num = choice[0]
                comment_per_tag.section_name = choice[1]
                resume.comments_per_section.append(comment_per_tag) 

    @classmethod
    def init_todos(self, resume):
        if len(resume.todos_per_section) == 0:
            for choice in self.CHOICES:
                todos_per_tag = ToDosPerSection()
                todos_per_tag.num_todos = 0
                todos_per_tag.index_num = choice[0]
                todos_per_tag.section_name = choice[1]
                resume.todos_per_section.append(todos_per_tag) 

    def get_context(self, slug=None):       
        resume = Resume.objects.get_or_404(slug=slug)
        form = self.form(request.form)
        context = {
            "resume": resume,
            "form": form,
            "choices": self.CHOICES
        }
        return context

    def get(self, slug):
        context = self.get_context(slug)

        # When this is passed in render template is smart enough
        # to have post, form available in the template context
        return render_template('resumes/detail.html', **context)

    def post(self, slug):
        context = self.get_context(slug)
        form = context.get('form')

        if form.validate():
            comment = Comment()
            form.populate_obj(comment)

            resume = context.get('resume')
            resume.comments.append(comment)

            # Intitialize the tags counter for sections
            # Looping from fields possible 
            # http://stackoverflow.com/questions/8586738/get-required-fields-from-document-in-mongoengine
            self.init_comments(resume)
            self.init_todos(resume)

            for tag in comment.tags:
                resume.comments_per_section[tag-1].num_comments += 1

            resume.save()

            return redirect(url_for('resume_app.detail', slug=slug))
        return render_template('resumes/detail.html', **context)

class CreateView(MethodView):
    decorators = [login_required]
    CHOICES = ((1, "skills"), (2, "experience"), (3, "education"), (4, "activities"), (5, "honors"), (6, "publication"))
    ResumeForm = model_form(Resume, exclude=['created_at', 'last_updated', 'comments', 'slug', 'user', 'comments', 'comments_per_section', 'todos_per_section'])
    #ActivityForm = model_form(ActivityItem, exclude=['comments'])

    def get_context(self, slug=None):
        if slug:
            resume = Resume.objects.get_or_404(slug=slug)
            permission = EditResumePermission(unicode(resume.id))
            #permission = Permission(UserNeed(g.user.id))
            g.identity.provides.add(EditResumeNeed(unicode(resume.id)))

            #FIXME: At this point, permission.can does not allow access
            if permission.can():
                if request.method == 'POST':
                    form = self.ResumeForm(request.form, initial=resume._data)
                else:
                    form = self.ResumeForm(obj=resume)
            abort(403)
        else:
            resume = Resume()
            form = self.ResumeForm(request.form)

        context = {
            "resume": resume,
            "form": form,
            "create": slug is None
        }
        return context

    def get(self, slug):
        context = self.get_context(slug)        
        return render_template('resumes/create.html', **context)

    def post(self, slug):
        context = self.get_context(slug)
        form = context.get('form')

        if form.validate():
            resume = context.get('resume')
            form.populate_obj(resume)
            resume.slug = resume.slug or resume['title'].lower()

            creator = User.objects.get_or_404(email=g.user.email)
            resume.user = creator
            
            DetailView.init_comments(resume)
            DetailView.init_todos(resume)
            resume.save()

            #FIXME: should redirect to details page for given slug 
            #(or other unique resume indicator)
            return redirect(url_for('resume_app.list'))
        return render_template('resumes/create.html', **context)

class TodoView(MethodView):
    #Also need a decorator to verify this is the owner of resume
    #TODO should not be displayed 
    decorators = [login_required]

    def post(self, slug=None):
        x = json.loads(request.data)
        # This is a limitation of logic to generate slugs
        # should really generate a unique slug
        resume = Resume.objects.get_or_404(slug=x['slug'].replace("%20", " "))

        for section in x['sections']:
            for todo in resume.todos_per_section:
                if todo.section_name.lower() == section["section_name"].lower():
                    todo.num_todos = section["value"]
        
        resume.save()
        return "200"

resume_app.add_url_rule('/', view_func=ListView.as_view('list'), methods=['GET', 'POST'])
resume_app.add_url_rule('/<slug>', view_func=DetailView.as_view('detail'), methods=['GET', 'POST'])
#defaults added otherwise create crashes as get takes two params
resume_app.add_url_rule('/create', defaults={'slug': None}, view_func=CreateView.as_view('create'), methods=['GET', 'POST'])
resume_app.add_url_rule('/<slug>/edit', view_func=CreateView.as_view('edit'), methods=['GET', 'POST'])
resume_app.add_url_rule('/todos', view_func=TodoView.as_view('todos'), methods=['POST'])