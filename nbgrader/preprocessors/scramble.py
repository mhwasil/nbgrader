import random
import re
from . import NbGraderPreprocessor


class Scramble(NbGraderPreprocessor):
    
    def __init__(self, **kw):
        self.pattern = re.compile('{{([^{]+)}}')
        self.rand = random.Random()
        if kw is not None:
            if 'seed' in kw:
                self.rand = random.Random(kw['seed'])
        
    def get_scramble_info(self, nb):
        info = {
            'constraints': [],
            'vals': {}
        }
        if len(nb.cells) < 1 or '%% scramble' not in nb.cells[0].source:
            return info
        for line in nb.cells[0].source.split('\n'):
            split = line.split('=')
            if len(split) > 1:
                varname = split[0].strip()
                args = split[1].strip().split('|')
                info['vals'][varname] = args
            elif 'fix(' in line:
                stripped = line.replace('fix(', '').replace(')', '').strip()
                stripped = [s.strip() for s in stripped.split(',')]
                info['constraints'].append(stripped)

        groups = []
        for v in info['vals']:
            if not any([v in c for c in info['constraints']]):
                groups.append([v])

        groups.extend(info['constraints'])
        info['groups'] = groups
        return info
    
    def sample_config(self, info):
        sampled = dict()

        for group in info['groups']:
            length = len(info['vals'][group[0]])
            idx = self.rand.randint(0, length-1)
            for item in group:
                sampled[item] = info['vals'][item][idx]

        return sampled        
    
    def preprocess(self, nb, resources):
        info = self.get_scramble_info(nb)
        if len(info['vals']) < 1:
            return nb, resources
        
        config = self.sample_config(info)
        resources['scramble_config'] = config
        
        for cell in nb.cells:
            matches = self.pattern.findall(cell.source)
            for m in matches:
                if m.strip() in config:
                    cell.source = cell.source.replace('{{' + m + '}}', config[m.strip()])
        
        nb.cells = nb.cells[1:]
        nb.metadata['scramble_config'] = config
        return nb, resources
        