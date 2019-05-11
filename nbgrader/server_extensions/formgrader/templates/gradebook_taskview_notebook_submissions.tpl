{%- extends 'gradebook_taskview_base.tpl' -%}

{%- block head -%}
<script>
var assignment_id = "{{ assignment_id }}";
var notebook_id = "{{ notebook_id }}";
var task_id = "{{ task_id }}";
</script>

<script src="{{ base_url }}/formgrader/static/js/gradebook_taskview_notebook_submissions.js"></script>
{%- endblock head -%}

{%- block breadcrumbs -%}
<ol class="breadcrumb">
  <li><a href="{{ base_url }}/formgrader/gradebook_tasks">Manual Grading (Task View)</a></li>
  <li><a href="{{ base_url }}/formgrader/gradebook_tasks/{{ assignment_id }}">{{ assignment_id }}</a></li>
  <li><a href="{{ base_url }}/formgrader/gradebook_tasks/{{ assignment_id }}/{{ notebook_id }}">{{ notebook_id }}</a></li>
  <li class="active">{{ task_id }}</li>
</ol>
{%- endblock -%}

{%- block table_header -%}
<tr>
  <th></th>
  <th>Submission ID</th>
  <th class="text-center">Score</th>
  <th class="text-center">Needs Manual Grade?</th>
  <th class="text-center">Tests Failed?</th>
</tr>
{%- endblock -%}

{%- block table_body -%}
<tr><td colspan="7">Loading, please wait...</td></tr>
{%- endblock -%}
