import re
from . import NbGraderPreprocessor

class Unscramble(NbGraderPreprocessor):
    
    def __init__(self, **kw):
        self.pattern = re.compile('{{([^{]+)}}')
        self.log.info('Init Unscramble')     
    
    def preprocess(self, nb, resources):        
        if 'scramble_config' not in nb.metadata:
            return nb, resources
            
        config = nb.metadata.scramble_config        
        
        for cell in nb.cells:
            matches = self.pattern.findall(cell.source)
            for m in matches:
                if m.strip() in config:
                    cell.source = cell.source.replace('{{' + m + '}}', config[m.strip()])
        
        nb.cells = nb.cells[1:]
        nb.metadata['scramble_config'] = config
        return nb, resources