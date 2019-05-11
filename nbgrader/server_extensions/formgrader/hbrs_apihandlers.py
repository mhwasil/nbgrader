import re
import json
import os

from tornado import web
from .base import BaseApiHandler, check_xsrf


class SolutionCellCollectionHandler(BaseApiHandler):

    @web.authenticated
    @check_xsrf
    def get(self, assignment_id, notebook_id):
        cells = self.api.get_solution_cell_ids(assignment_id, notebook_id)
        self.write(json.dumps(cells))

class SubmittedTaskViewNotebookCollectionHandler(BaseApiHandler):
    @web.authenticated
    @check_xsrf
    def get(self, assignment_id, notebook_id, task_id):
        submissions = self.api.get_task_submissions(assignment_id, notebook_id, task_id)
        self.write(json.dumps(submissions))


default_handlers = [
    (r"/formgrader/api/taskview/solution_cells/([^/]+)/([^/]+)", SolutionCellCollectionHandler),
    (r"/formgrader/api/taskview/submitted_notebooks/([^/]+)/([^/]+)/([^/]+)", SubmittedTaskViewNotebookCollectionHandler),
]