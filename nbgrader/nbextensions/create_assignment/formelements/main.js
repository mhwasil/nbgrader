define([
    'base/js/namespace',
    'base/js/events',
    'notebook/js/textcell',
    'require'
], function(
    Jupyter,
    events,
    textcell,
    require
) {

    "use strict";

    var MarkdownCell = textcell.MarkdownCell;
    var old_render = MarkdownCell.prototype.render;
    var old_unrender = MarkdownCell.prototype.unrender;  

    var form_metadata = 'form_cell';

    var is_form_cell = function (cell) {
        return cell.metadata.hasOwnProperty(form_metadata);
    };

    var is_multiplechoice = function (cell) {
        return is_form_cell(cell) && cell.metadata[form_metadata].type == 'multiplechoice';
    };

    var to_multiplechoice = function (cell) {
        if (cell.metadata.hasOwnProperty(form_metadata)) {
            delete cell.metadata.form_cell;
        }
        cell.metadata.form_cell = {
            "type": "multiplechoice"
        }        
    };

    var is_singlechoice = function (cell) {
        return is_form_cell(cell) && cell.metadata[form_metadata].type == 'singlechoice';
    };

    var to_singlechoice = function (cell) {
        if (cell.metadata.hasOwnProperty(form_metadata)) {
            delete cell.metadata.form_cell;
        }
        cell.metadata.form_cell = {
            "type": "singlechoice"
        }        
    };

    var is_choice_cell = function (cell) {
        return is_singlechoice(cell) || is_multiplechoice(cell);
    };

    var remove_form_metadata = function (cell) {
        if (cell.metadata.hasOwnProperty(form_metadata)) {
            delete cell.metadata.form_cell;
            if (cell.rendered) {
                cell.unrender();
                cell.render();
            }
        }
    };

    var get_choices = function (cell) {
        if (is_choice_cell) {
            if (cell.metadata[form_metadata].hasOwnProperty('choice')) {
                return cell.metadata[form_metadata].choice;
            }
        }
        return [];
    };

    var get_weights = function (cell) {
        if (is_choice_cell) {
            if (cell.metadata[form_metadata].hasOwnProperty('weights')) {
                return cell.metadata[form_metadata].weights;
            }
        }
        return [];
    };

    function create_edit_button(cell) {
        return $('<button>')
                .attr('type', 'button')
                .addClass('hbrs_unrender')
                .click(function () {
                    cell.unrender_force();
                }).append('Edit cell');
    };

    var create_checkbox = function(name, value, selected, points, cell) {
        var input = $('<input>')
                        .attr('type', 'checkbox')
                        .attr('name', name)
                        .attr('value', value);
        input.change(function () {
            var weight = get_weights(cell)[value];
            if (this.checked) {
                if (weight < 0) {
                    cell.metadata[form_metadata].weights[value] = -weight;
                    points.attr('value', -weight);
                }
                var cur_choices = get_choices(cell);
                cur_choices.push(this.value);
                cell.metadata[form_metadata].choice = cur_choices;
            } else {
                if (weight > 0) {
                    cell.metadata[form_metadata].weights[value] = -weight;
                    points.attr('value', -weight);
                }
                var idx = get_choices(cell).indexOf(this.value);
                if (idx > -1) {
                    cell.metadata[form_metadata].choice.splice(idx, 1);
                }
            }
        update_nbgrader_points(cell);
        });

        if (selected) {
            input.attr('checked', 'checked');
        }
        return input;
    };

    function create_radio(name, value, selected, onChange) {
        var input = $('<input>')
                        .attr('type', 'radio')
                        .attr('name', name)
                        .attr('value', value)
                        .change(onChange);
        if (selected) {
            input.attr('checked', 'checked');
        }
        return input;
    };

    function update_nbgrader_points(cell) {
        if (cell.metadata.hasOwnProperty('nbgrader') && cell.metadata.nbgrader.hasOwnProperty('points')) {
            var point_total = 0
            for (var i=0;i<get_weights(cell).length;i++) {
                if (get_weights(cell)[i] > 0) {
                    point_total += get_weights(cell)[i];
                }
            }
            var points_input = $(cell.element).find('.nbgrader-points-input');
            if (points_input.length > 0) {
                points_input.attr('value', point_total);
            }
            cell.metadata.nbgrader.points = point_total;
        }
    };

    function make_point_input(cell, i) {
        var points = $('<input>')
                .attr('type', 'number')
                .attr('value', get_weights(cell)[i])
                .addClass('hbrs_points')
                .change(function () {
                    cell.metadata.form_cell.weights[i] = parseInt(this.value);
                    update_nbgrader_points(cell);
                });
        return points;
    };

    var make_radio = function (cell) {
        var in_area = $(cell.element).find('.rendered_html');
        var lists = in_area.find('ul');
        var choices = get_choices(cell);
        if (lists.length > 0) {
            var list = lists[0];
            var form = $('<form>').addClass('hbrs_radio');
            var items = $(list).find('li');
            for (var i=0; i<items.length; i++) {

                var input = create_radio('my_radio', i, choices.indexOf(i.toString()) >= 0, function () {
                    cell.metadata[form_metadata].choice = [this.value];
                });

                Jupyter.keyboard_manager.register_events(input);

                form.append($('<div>')
                            .append(input)
                            .append('&nbsp;&nbsp;')
                            .append(items[i].childNodes));
            };
            $(list).replaceWith(form);
        }
        in_area.append(create_edit_button(cell));
    };

    var make_checkboxes = function (cell) {
        var in_area = $(cell.element).find('.rendered_html');
        var lists = $(cell.element).find('ul');
        var choices = get_choices(cell);
        if (lists.length > 0) {
            var list = lists[0];
            var form = $('<form>').addClass('hbrs_checkbox');
            var items = $(list).find('li');
            var weights = get_weights(cell);
            if (weights.length<items.length) {
                weights = [];
                for (var i=0; i<items.length; i++) {
                    weights.push(-1);
                }
                cell.metadata.form_cell.weights = weights;
            }
            for (var i=0; i<items.length; i++) {
                var points = make_point_input(cell, i);
                var input = create_checkbox('my_checkbox', i, choices.indexOf(i.toString()) >= 0, points, cell);
                Jupyter.keyboard_manager.register_events(points);
                Jupyter.keyboard_manager.register_events(input);

                form.append($('<div>')
                            .append(input)
                            .append('&nbsp;&nbsp;')
                            .append(items[i].childNodes)
                            .append('&nbsp;&nbsp;')
                            .append(points)
                            .append('Points'));
            };
            $(list).replaceWith(form);
        }
        in_area.append(create_edit_button(cell));
    };

    function render_form_cells() {
        var cells = Jupyter.notebook.get_cells();
        for (var i in cells) {
            var cell = cells[i];
            // Rerender rendered form cells
            if (is_form_cell(cell) && cell.rendered) {
                cell.unrender_force();
                cell.render();
            }
        }
    };

    function render_form_cells_asap() {
        if (Jupyter.notebook && Jupyter.notebook.kernel && Jupyter.notebook.kernel.info_reply.status == 'ok') {
            render_form_cells();
        }
        events.on('kernel_ready.Kernel', render_form_cells);
    };

    var patch_MarkdownCell_render = function () {
        //var old_render = MarkdownCell.prototype.render;
        MarkdownCell.prototype.render = function () {
            old_render.apply(this, arguments);
            if (is_singlechoice(this)) {
                make_radio(this);
            } else if (is_multiplechoice(this)) {
                make_checkboxes(this);
            }
        }
    };

    var unpatch_MarkdownCell_render = function () {
        MarkdownCell.prototype.render = old_render;
    };

    var patch_MarkdownCell_unrender = function () {
        //var old_unrender = MarkdownCell.prototype.unrender;

        MarkdownCell.prototype.unrender_force = old_unrender;
        
        MarkdownCell.prototype.unrender = function () {
            if (is_form_cell(this)) {
                return;
            } 
            old_unrender.apply(this, arguments);
        }
    };

    var unpatch_MarkdownCell_unrender = function () {
        MarkdownCell.prototype.unrender = old_unrender;
    };

    function load_css() {
        var link = document.createElement("link");
        link.type = "text/css";
        link.rel = "stylesheet";
        link.href = require.toUrl("./forms.css");
        document.getElementsByTagName("head")[0].appendChild(link);
    };

    function initialize() {
        load_css();
        patch_MarkdownCell_unrender();
        patch_MarkdownCell_render();        
        render_form_cells();
    };

    return {
        patch_MarkdownCell_render: patch_MarkdownCell_render,
        unpatch_MarkdownCell_render: unpatch_MarkdownCell_render,
        patch_MarkdownCell_unrender: patch_MarkdownCell_unrender,
        unpatch_MarkdownCell_unrender: unpatch_MarkdownCell_unrender,
        remove_form_metadata: remove_form_metadata,
        is_multiplechoice: is_multiplechoice,
        to_multiplechoice: to_multiplechoice,
        is_singlechoice: is_singlechoice,
        to_singlechoice: to_singlechoice,
        load_css: load_css,
        render_form_cells: render_form_cells
    };
});
