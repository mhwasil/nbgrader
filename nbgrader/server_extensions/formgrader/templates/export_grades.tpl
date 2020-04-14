{%- extends 'base.tpl' -%}

{%- block title -%}
Export Grades
{%- endblock -%}

{%- block sidebar -%}
<li role="presentation"><a href="{{ base_url }}/formgrader/manage_assignments">Manage Assignments</a></li>
<li role="presentation"><a href="{{ base_url }}/formgrader/gradebook">Manual Grading</a></li>
<li role="presentation"><a href="{{ base_url }}/formgrader/gradebook/?view=task">Manual Grading (Task View)</a></li>
<li role="presentation"><a href="{{ base_url }}/formgrader/manage_students">Manage Students</a></li>
<li role="presentation" class="active"><a href="{{ base_url }}/formgrader/export_grades">Export Grades</a></li>
{%- endblock -%}

{%- block table_body -%}

<h4>Here you can export grades</h4>
<p>There are two variants. Either on a notebook level (total score per notebook per student) or on a task level (score for each task of each notebook).</p>

<a target="_blank" href="{{ base_url }}/formgrader/export_grades/notebooks" download="grades.csv">Download CSV - Notebooks only</a></br>
<a target="_blank" href="{{ base_url }}/formgrader/export_grades/tasks" download="grades.csv">Download CSV - With Tasks</a>

{%- endblock -%}