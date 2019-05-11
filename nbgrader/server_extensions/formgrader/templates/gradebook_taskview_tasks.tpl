{%- extends 'gradebook_taskview_base.tpl' -%}

{%- block head -%}
<script>
var assignment_id = "{{ assignment_id }}";
var notebook_id = "{{ notebook_id }}";
</script>

<script src="{{ base_url }}/formgrader/static/js/gradebook_taskview_tasks.js"></script>
{%- endblock head -%}

{%- block breadcrumbs -%}
<ol class="breadcrumb">
  <li><a href="{{ base_url }}/formgrader/gradebook_tasks">Manual Grading (TaskView)</a></li>
  <li><a href="{{ base_url }}/formgrader/gradebook_tasks/{{ assignment_id }}/">{{ assignment_id }}</a></li>
  <li class="active">{{ notebook_id }}</li>
</ol>
{%- endblock -%}

{%- block table_header -%}
<tr>
  <th>Task ID</th>
  <th class="text-center">Avg. Score</th>
  <th class="text-center">Is Autograded?</th>
  <th class="text-center">Needs Manual Grade?</th>
</tr>
{%- endblock -%}

{%- block table_body -%}
<tr><td colspan="5">Loading, please wait...</td></tr>
{%- endblock -%}
