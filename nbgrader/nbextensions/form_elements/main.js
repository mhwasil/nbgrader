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
    

    var form_metadata = 'form_cell';

    var is_form_cell = function (cell) {
        return cell.metadata.hasOwnProperty(form_metadata);
    };

    var is_multiplechoice_cell = function (cell) {
        return is_form_cell(cell) && cell.metadata[form_metadata].type == 'multiplechoice';
    };

    var is_singlechoice_cell = function (cell) {
        return is_form_cell(cell) && cell.metadata[form_metadata].type == 'singlechoice';
    };

    var is_choice_cell = function (cell) {
        return is_singlechoice_cell(cell) || is_multiplechoice_cell(cell);
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
    }

    var create_input = function(type, name, value, selected, onChange) {
        var input = $('<input>')
                        .attr('type', type)
                        .attr('name', name)
                        .attr('value', value)
                        .change(onChange);
        if (selected) {
            input.attr('checked', 'checked');
        }
        return input;
    }

    var create_checkbox = function(type, name, value, selected, points, cell) {
        var input = $('<input>')
                        .attr('type', type)
                        .attr('name', name)
                        .attr('value', value)
                        .change(function () {
                            if (this.checked) {
                                if (get_weights(cell)[value] < 0) {
                                    var new_weight = -get_weights(cell)[value];

                                    cell.metadata.form_cell.weights[value] = new_weight;
                                    points.attr('value', new_weight);
                                }
                                var cur_choices = get_choices(cell);
                                cur_choices.push(this.value);
                                cell.metadata[form_metadata].choice = cur_choices;
                            } else {
                                if (get_weights(cell)[value] > 0) {
                                    var new_weight = -get_weights(cell)[value];

                                    cell.metadata.form_cell.weights[value] = new_weight;
                                    points.attr('value', new_weight);
                                }
                                var index = get_choices(cell).indexOf(this.value);
                                if (index > -1) {
                                    cell.metadata[form_metadata].choice.splice(index, 1);
                                }
                            }
                            update_nbgrader_points(cell);
                        });
        if (selected) {
            input.attr('checked', 'checked');
        }
        return input;
    }

    var update_nbgrader_points = function (cell) {
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
    }

    var make_point_input = function (cell, i) {
        var points = $('<input>')
                .attr('type', 'number')
                .attr('value', get_weights(cell)[i])
                //.attr('disabled', 'disabled')
                .addClass('hbrs_points')
                .change(function () {
                    cell.metadata.form_cell.weights[i] = parseInt(this.value);
                    update_nbgrader_points(cell);
                });
        return points;
    }

    var make_radio = function (cell) {
        var in_area = $(cell.element).find('.rendered_html');
        var lists = in_area.find('ul');
        var choices = get_choices(cell);
        if (lists.length > 0) {
            var list = lists[0];
            var form = $('<form>').addClass('hbrs_radio');
            var items = $(list).find('li');
            for (var i=0; i<items.length; i++) {

                var input = create_input('radio', 'my_radio', i, choices.indexOf(i.toString()) >= 0, function () {
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
        var edit_button = $('<button>').attr('type', 'button')
                            .addClass('hbrs_unrender')
                            .click(function () {
                                cell.unrender_force();
                            }).append('Edit cell');
        in_area.append(edit_button);
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
                var input = create_checkbox('checkbox', 'my_checkbox', i, choices.indexOf(i.toString()) >= 0, points, cell);
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
        var edit_button = $('<button>').attr('type', 'button')
                    .addClass('hbrs_unrender')
                    .click(function () {
                        cell.unrender_force();
                    }).append('Edit cell');
        in_area.append(edit_button);
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
        var old_render = MarkdownCell.prototype.render;
        MarkdownCell.prototype.render = function () {
            old_render.apply(this, arguments);
            if (is_singlechoice_cell(this)) {
                make_radio(this);
            } else if (is_multiplechoice_cell(this)) {
                make_checkboxes(this);
            }
        }
    };

    var patch_MarkdownCell_unrender = function () {
        var old_unrender = MarkdownCell.prototype.unrender;

        MarkdownCell.prototype.unrender_force = old_unrender;
        
        MarkdownCell.prototype.unrender = function () {
            if (is_form_cell(this)) {
                return;
            } 
            old_unrender.apply(this, arguments);
        }
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

    var load_ipython_extension = function () {
        return Jupyter.notebook.config.loaded.then(initialize);
    };

    return {
        load_ipython_extension : load_ipython_extension
    };
});
