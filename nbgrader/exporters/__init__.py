import os
import os.path

from traitlets.config import Config
from traitlets import Unicode
from nbconvert.exporters.html import HTMLExporter
from jinja2 import contextfilter
from bs4 import BeautifulSoup
from .. import utils

class FormExporter(HTMLExporter):
    """
    My custom exporter
    """

    extra_cell_field = Unicode(
        'extended_cell', 
        help='The name of the extra cell metadata field.'
    )

    @contextfilter
    def to_choicecell(self, context, source):
        cell = context.get('cell', {})
        metadata = context.get('cell', {}).metadata
        soup = BeautifulSoup(source, 'html.parser')
        if not soup.ul:
            return soup.prettify().replace('\n', '')
        if utils.is_singlechoice(cell):
            my_type = 'radio'
        elif utils.is_multiplechoice(cell):
            my_type = 'checkbox'
        form = soup.new_tag('form')
        form['class'] = 'hbrs_checkbox'
        
        list_elems = soup.ul.find_all('li')
        inputs = []
        for i in range(len(list_elems)):
            div = soup.new_tag('div')
            box = soup.new_tag('input')
            box['type'] = my_type
            box['value'] = i
            box['disabled'] = 'disabled'
            if str(i) in utils.get_choices(cell):
                box['checked'] = 'checked'                
            div.append(box)
            children = [c for c in list_elems[i].children]
            for child in children:
                div.append(child)

            if utils.has_solution(cell):
                check = soup.new_tag('span')
                if str(i) in utils.get_instructor_choices(cell):
                    check.string = 'correct'
                    check['style'] = 'color:green'
                else:
                    check.string = 'false'
                    check['style'] = 'color:red'
                
                if utils.is_multiplechoice(cell):
                    weight = utils.get_instructor_weights(cell)[i]
                    if weight > 0:
                        check.append('[+{} point(s)]'.format(weight))
                    else:
                        check.append('[{} point(s)]'.format(weight))
                div.append(check)
            form.append(div)
        soup.ul.replaceWith(form)
        return soup.prettify().replace('\n', '')

    def default_filters(self):
        for pair in super(FormExporter, self).default_filters():
            yield pair
        yield ('to_choicecell', self.to_choicecell)

    @property
    def template_path(self):
        """
        We want to inherit from HTML template, and have template under
        `./templates/` so append it to the search path. (see next section)
        """
        return super().template_path + [os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'server_extensions', 'formgrader', 'templates'))]