"""# Distributions"""

from .moments import Moments
from .table import Table

import json

# maps distribution class name to distribution class
# distribution class name is stored in the state dictionary with a 'cls' key
dist_classes = {
    'Moments': Moments,
    'Table': Table,
}

def load_distributions(dist_states):
    """
    Parameters
    ----------
    dist_states : list of JSON dictionaries
        List of distribution state dictionaries.

    Returns
    -------
    distributions : list of distributions
        List of distributions recovered from the state dictionaries.
    """
    return [load_distribution(state) for state in dist_states]

def load_distribution(dist_state):
    """
    Parameters
    ----------
    dist_state : JSON dictionary
        Distribution state dictionary.

    Returns
    -------
    distribution : 
        Distribution recovered from the state dictionary.
    """
    return dist_classes[json.loads(dist_state)['cls']].load(dist_state)