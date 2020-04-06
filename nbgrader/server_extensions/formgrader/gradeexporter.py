from traitlets.config import LoggingConfigurable
from traitlets import Unicode
from ...api import *
import nbformat
import os
import pandas as pd

class GradeExporter(LoggingConfigurable):

    def __init__(self, gradebook, course_dir):
        self.gb = gradebook
        self.course_dir = course_dir


    def get_assignments(self):
        all_assignments = self.gb.db.query(
            Assignment.name
        ).all()
        # Filter out assignments with no submissions
        assignments = []
        for assignment in all_assignments:
            name = assignment[0]
            submissions = self.gb.db.query(
                SubmittedAssignment
            ) \
            .filter(Assignment.name == name) \
            .filter(SubmittedAssignment.assignment_id == Assignment.id) \
            .all()
            if len(submissions) > 0:
                assignments.append(name)
        return assignments


    def get_notebooks(self, assignment):
        notebooks = self.gb.db.query(
            Notebook.name
        ) \
        .filter(Assignment.name == assignment) \
        .filter(Notebook.assignment_id == Assignment.id) \
        .all()
        return [notebook[0] for notebook in notebooks]


    def get_tasks(self, assignment, notebook):
        tasks = self.gb.db.query(
            BaseCell.name
        ) \
        .filter(Assignment.name == assignment) \
        .filter(Notebook.assignment_id == Assignment.id) \
        .filter(Notebook.name == notebook) \
        .filter(BaseCell.notebook_id == Notebook.id) \
        .filter(BaseCell.type == 'GradeCell') \
        .all()
        tasks = [task[0] for task in tasks]
        
        nb_file = os.path.join(self.course_dir, 'release', assignment, '{}.ipynb'.format(notebook))
        nb = nbformat.read(nb_file, as_version=4)
        
        tasks_sorted = []
        for cell in nb.cells:
            if 'nbgrader' in cell.metadata:
                grade_id = cell.metadata.nbgrader.grade_id
                if grade_id in tasks:
                    tasks_sorted.append(grade_id)
        return tasks_sorted


class GradeTaskExporter(GradeExporter):
      
    def __init__(self, gradebook, course_dir):
        super(GradeTaskExporter, self).__init__(gradebook, course_dir)

    
    def get_columns(self):
        columns = []
        assignments = self.get_assignments()
        for assignment in assignments:
            for notebook in self.get_notebooks(assignment):
                for task in self.get_tasks(assignment, notebook):
                    columns.append((assignment, notebook, task))            
        return columns

    
    def get_grades(self):
        grades = self.gb.db.query(
            SubmittedAssignment.student_id,
            Assignment.name,
            Notebook.name,
            BaseCell.name,
            Grade.auto_score,
            Grade.manual_score,
            GradeCell.max_score
        )\
        .filter(Notebook.assignment_id == Assignment.id) \
        .filter(SubmittedAssignment.assignment_id == Assignment.id) \
        .filter(SubmittedNotebook.assignment_id == SubmittedAssignment.id) \
        .filter(BaseCell.notebook_id == Notebook.id) \
        .filter(BaseCell.type == 'GradeCell') \
        .filter(Grade.cell_id == BaseCell.id) \
        .filter(Grade.notebook_id == SubmittedNotebook.id) \
        .all()
        
        return grades

    
    def make_table(self):
        columns = ['Student ID'] + ['.'.join(col) for col in self.get_columns()]
        data = []
        for student in self.gb.db.query(Student.id).all():
            data.append([student[0]] + [0.0 for _ in range(len(columns) - 1)])
        table = pd.DataFrame(data, columns=columns)
        
        grades = self.get_grades()
        for grade in grades:
            task = '.'.join(grade[1:4])
            auto = grade[4]
            manual = grade[5]
            score = 0.0
            if auto:
                score += auto
            if manual:
                score += manual
            table.loc[table['Student ID'] == grade[0], task] = score
        table['Total'] = table.sum(axis=1, numeric_only=True)
        return table    


class GradeNotebookExporter(GradeExporter):
    
    def __init__(self, gradebook, course_dir):
        super(GradeNotebookExporter, self).__init__(gradebook, course_dir)


    def get_columns(self):
        columns = []
        assignments = self.get_assignments()
        for assignment in assignments:
            for notebook in self.get_notebooks(assignment):
                    columns.append((assignment, notebook))            
        return columns

    
    def get_notebook_grades(self):
        grades = self.gb.db.query(
            SubmittedAssignment.student_id, 
            Assignment.name,
            Notebook.name, 
            func.coalesce(func.sum(Grade.manual_score),0),
            func.coalesce(func.sum(Grade.auto_score),0)
        ) \
        .filter(Notebook.assignment_id == Assignment.id) \
        .filter(SubmittedAssignment.assignment_id == Assignment.id) \
        .filter(SubmittedNotebook.assignment_id == SubmittedAssignment.id) \
        .filter(SubmittedNotebook.notebook_id == Notebook.id) \
        .filter(Grade.notebook_id == SubmittedNotebook.id) \
        .group_by(SubmittedAssignment.student_id) \
        .all()
        return grades
    

    def make_table(self):
        columns = ['Student ID'] + ['.'.join(col) for col in self.get_columns()]
        data = []
        for student in self.gb.db.query(Student.id).all():
            data.append([student[0]] + [0.0 for _ in range(len(columns) - 1)])
        table = pd.DataFrame(data, columns=columns)
        
        grades = self.get_notebook_grades()
        for grade in grades:
            nb = '.'.join(grade[1:3])
            auto = grade[3]
            manual = grade[4]
            score = grade[3] + grade[4]
            table.loc[table['Student ID'] == grade[0], nb] = score
        table['Total'] = table.sum(axis=1, numeric_only=True)
        return table  