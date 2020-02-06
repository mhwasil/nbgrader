import os
import os.path

from traitlets.config import Config
from nbconvert.exporters.html import HTMLExporter
from jinja2 import contextfilter
from bs4 import BeautifulSoup

#-----------------------------------------------------------------------------
# Classes
#-----------------------------------------------------------------------------

class FormExporter(HTMLExporter):
    """
    My custom exporter
    """

    @contextfilter
    def to_choicecell(self, context, source):
        metadata = context.get('cell', {}).metadata
        soup = BeautifulSoup(source, 'html.parser')
        if not soup.ul:
            return cell_html
        if metadata['form_cell']['type'] == 'singlechoice':
            my_type = 'radio'
        else:
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
            if str(i) in metadata['form_cell']['choice']:
                box['checked'] = 'checked'
            div.append(box)
            children = [c for c in list_elems[i].children]
            for child in children:
                div.append(child)
            form.append(div)
        soup.ul.replaceWith(form)
        return soup.prettify().replace('\n', '')

    def default_filters(self):
        for pair in super(FormExporter, self).default_filters():
            yield pair
        yield ('to_choicecell', self.to_choicecell)