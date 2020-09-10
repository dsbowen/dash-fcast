from .moments import Moments
from .table import Table

import json

dist_classes = {
    'moments': Moments,
    'table': Table
}

def load_distributions(dist_states):
    return [load_distribution(state) for state in dist_states]

def load_distribution(dist_state):
    return dist_classes[json.loads(dist_state)['cls']].load(dist_state)