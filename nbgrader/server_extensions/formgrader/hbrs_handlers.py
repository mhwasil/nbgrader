import re
import json
import os

from tornado import web
from .base import BaseHandler, check_xsrf



class MyHandler(BaseHandler):

    @web.authenticated
    @check_xsrf
    def get(self):
        info = 'DB URL: {}'.format(self.db_url)
        info = '{}\nBase URL: {}'.format(info, self.base_url) 
        self.write(info)

class InfoHandler(BaseHandler):

    @web.authenticated
    @check_xsrf
    def get(self, assignment_id):
        assignment = self.api.get_notebooks(assignment_id)
        self.write(str(assignment))

class SolutionCellHandler(BaseHandler):

    @web.authenticated
    @check_xsrf
    def get(self, notebook_id):
        cells = self.api.get_solution_cell_ids(notebook_id)
        self.write(str(cells))

class SubmissionHandler(BaseHandler):

    @web.authenticated
    @check_xsrf
    def get(self, assignment_id):
        submissions = self.api.get_submissions(assignment_id)
        self.write(json.dumps(submissions))

class SubmissionArgumentHandler(BaseHandler):

    @web.authenticated
    @check_xsrf
    def get(self, submission_id, question_id):
        output = '{}, {}\n {}!'.format(submission_id, question_id, self.base_url)
        self.write(output)


class ExporterHandler(BaseHandler):

    @web.authenticated
    @check_xsrf
    def get(self):
        self.write(str(self.taskview_exporter.config))


class SingleSubmissionHandler(BaseHandler):

    @web.authenticated
    @check_xsrf
    def get(self, assignment_id, student_id):
        student = self.api.get_student(student_id)
        submission = self.api.get_submission(assignment_id, student_id)
        k = 'Submission for assignment {} by student:<\\br> {} {}.'.format(assignment_id, student['first_name'], student['last_name'])
        k += '\nYour unique id is:\n' + str(submission['id'])
        self.write(k)

class GradebookTaskViewAssignmentsHandler(BaseHandler):
    @web.authenticated
    @check_xsrf
    def get(self):
        html = self.render(
            "gradebook_taskview_assignments.tpl",
            base_url=self.base_url)
        self.write(html)

class GradebookTaskViewNotebooksHandler(BaseHandler):
    @web.authenticated
    @check_xsrf
    def get(self, assignment_id):
        html = self.render(
            "gradebook_taskview_notebooks.tpl",
            assignment_id=assignment_id,
            base_url=self.base_url)
        self.write(html)

class GradebookTaskViewTasksHandler(BaseHandler):
    @web.authenticated
    @check_xsrf
    def get(self, assignment_id, notebook_id):
        html = self.render(
            "gradebook_taskview_tasks.tpl",
            assignment_id=assignment_id,
            notebook_id=notebook_id,
            base_url=self.base_url)
        self.write(html)

class GradebookTaskViewNotebookSubmissionsHandler(BaseHandler):
    @web.authenticated
    @check_xsrf
    def get(self, assignment_id, notebook_id, task_id):
        html = self.render(
            "gradebook_taskview_notebook_submissions.tpl",
            assignment_id=assignment_id,
            notebook_id=notebook_id,
            task_id=task_id,
            base_url=self.base_url)
        self.write(html)

class SubmissionTaskViewNavigationHandler(BaseHandler):

    def _assignment_notebook_list_url(self, assignment_id, notebook_id, task_id):
        return '{}/formgrader/gradebook_tasks/{}/{}/{}'.format(self.base_url, assignment_id, notebook_id, task_id)

    def _submission_url(self, submission_id, task_id):
        url = '{}/formgrader/hbrs_submissions/{}/{}'.format(self.base_url, submission_id, task_id)
        if self.get_argument('index', default=None) is not None:
            return "{}?index={}".format(url, self.get_argument('index'))
        else:
            return url

    def _get_submission_ids(self, assignment_id, notebook_id):
        notebooks = self.gradebook.notebook_submissions(notebook_id, assignment_id)
        submissions = self.api._filter_existing_notebooks(assignment_id, notebooks)
        return sorted([x.id for x in submissions])

    def _get_incorrect_submission_ids(self, assignment_id, notebook_id, task_id, submission):
        notebooks = self.gradebook.notebook_submissions(notebook_id, assignment_id)
        submissions = self.api._filter_existing_notebooks(assignment_id, notebooks)
        incorrect_ids = set([x.id for x in submissions if x.failed_tests])
        incorrect_ids.add(submission.id)
        incorrect_ids = sorted(incorrect_ids)
        return incorrect_ids

    def _next(self, assignment_id, notebook_id, task_id, submission):
        # find next submission
        submission_ids = self._get_submission_ids(assignment_id, notebook_id)
        ix = submission_ids.index(submission.id)
        if ix == (len(submission_ids) - 1):
            return self._assignment_notebook_list_url(assignment_id, notebook_id, task_id)
        else:
            return self._submission_url(submission_ids[ix + 1], task_id)

    def _prev(self, assignment_id, notebook_id, task_id, submission):
        # find previous submission
        submission_ids = self._get_submission_ids(assignment_id, notebook_id)
        ix = submission_ids.index(submission.id)
        if ix == 0:
            return self._assignment_notebook_list_url(assignment_id, notebook_id, task_id)
        else:
            return self._submission_url(submission_ids[ix - 1], task_id)

    def _next_incorrect(self, assignment_id, notebook_id, task_id, submission):
        # find next incorrect submission
        submission_ids = self._get_incorrect_submission_ids(assignment_id, notebook_id, submission)
        ix_incorrect = submission_ids.index(submission.id)
        if ix_incorrect == (len(submission_ids) - 1):
            return self._assignment_notebook_list_url(assignment_id, notebook_id, task_id)
        else:
            return self._submission_url(submission_ids[ix_incorrect + 1], task_id)

    def _prev_incorrect(self, assignment_id, notebook_id, task_id, submission):
        # find previous incorrect submission
        submission_ids = self._get_incorrect_submission_ids(assignment_id, notebook_id, submission)
        ix_incorrect = submission_ids.index(submission.id)
        if ix_incorrect == 0:
            return self._assignment_notebook_list_url(assignment_id, notebook_id, task_id)
        else:
            return self._submission_url(submission_ids[ix_incorrect - 1], task_id)

    @web.authenticated
    @check_xsrf
    def get(self, submission_id, task_id, action):
        try:
            submission = self.gradebook.find_submission_notebook_by_id(submission_id)
            assignment_id = submission.assignment.assignment.name
            notebook_id = submission.notebook.name
        except MissingEntry:
            raise web.HTTPError(404, "Invalid submission: {}".format(submission_id))

        handler = getattr(self, '_{}'.format(action))
        self.redirect(handler(assignment_id, notebook_id, task_id, submission), permanent=False)

class SubmissionTaskViewHandler(BaseHandler):
    
    @web.authenticated
    @check_xsrf
    def get(self, submission_id, task_id):
        try:
            submission = self.gradebook.find_submission_notebook_by_id(submission_id)
            assignment_id = submission.assignment.assignment.name
            notebook_id = submission.notebook.name
            student_id = submission.student.id
        except MissingEntry:
            raise web.HTTPError(404, "Invalid submission: {}".format(submission_id))

        # redirect if there isn't a trailing slash in the uri
        if os.path.split(self.request.path)[1] == task_id:
            url = self.request.path + '/'
            if self.request.query:
                url += '?' + self.request.query
            return self.redirect(url, permanent=True)


        filename = os.path.join(os.path.abspath(self.coursedir.format_path(
            self.coursedir.autograded_directory, student_id, assignment_id)), '{}.ipynb'.format(notebook_id))
        relative_path = os.path.relpath(filename, self.coursedir.root)
        indices = self.api.get_notebook_submission_indices(assignment_id, notebook_id)
        ix = indices.get(submission.id, -2)

        resources = {
            'assignment_id': assignment_id,
            'notebook_id': notebook_id,
            'submission_id': submission.id,
            'index': ix,
            'total': len(indices),
            'base_url': self.base_url,
            'mathjax_url': self.mathjax_url,
            'student': student_id,
            'last_name': submission.student.last_name,
            'first_name': submission.student.first_name,
            'notebook_path': self.url_prefix + '/' + relative_path,
            'keyword': task_id,
            'task_id': task_id
        }

        if not os.path.exists(filename):
            resources['filename'] = filename
            html = self.render('formgrade_404.tpl', resources=resources)
            self.clear()
            self.set_status(404)
            self.write(html)

        else:
            html, _ = self.taskview_exporter.from_filename(filename, resources=resources)
            self.write(html)

_navigation_regex = r"(?P<action>next_incorrect|prev_incorrect|next|prev)"

default_handlers = [
    (r"/formgrader/hbrs/?", MyHandler),
    (r"/formgrader/hbrs/exporter/?", ExporterHandler),
    (r"/formgrader/hbrs_info/([^/]+)/?", InfoHandler),
    (r"/formgrader/hbrs_cells/([^/]+)/?", SolutionCellHandler),
    (r"/formgrader/hbrs_submission/([^/]+)/?", SubmissionHandler),
    (r"/formgrader/hbrs_submission/([^/]+)/([^/]+)/?", SubmissionArgumentHandler),
    (r"/formgrader/hbrs_single_submission/([^/]+)/([^/]+)/?", SingleSubmissionHandler),
    (r"/formgrader/hbrs_submissions/([^/]+)/([^/]+)/?", SubmissionTaskViewHandler),

    (r"/formgrader/gradebook_tasks/?", GradebookTaskViewAssignmentsHandler),
    (r"/formgrader/gradebook_tasks/([^/]+)/?", GradebookTaskViewNotebooksHandler),
    (r"/formgrader/gradebook_tasks/([^/]+)/([^/]+)/?", GradebookTaskViewTasksHandler),
    (r"/formgrader/gradebook_tasks/([^/]+)/([^/]+)/([^/]+)/?", GradebookTaskViewNotebookSubmissionsHandler),
    (r"/formgrader/hbrs_submissions/(?P<submission_id>[^/]+)/(?P<task_id>[^/]+)/%s/?" % _navigation_regex, SubmissionTaskViewNavigationHandler),
]