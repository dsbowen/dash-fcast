import json

def get_changed_cell(curr_records, prev_records):
    records = zip(curr_records, prev_records)
    for i, (curr_record, prev_record) in enumerate(records):
        keys = set(list(curr_record.keys()) + list(prev_record.keys()))
        for key in keys:
            if curr_record.get(key) != prev_record.get(key):
                return i, key
    return None, None

def get_deleted_row(curr_records, prev_records):
    records = zip(curr_records, prev_records)
    for i, (curr_record, prev_record) in enumerate(records):
        if curr_record != prev_record:
            return i
    # last row was deleted
    return len(curr_records)

def get_trigger_ids(ctx):
    """
    Parameters
    ----------
    ctx : dash.callback_context

    Returns
    -------
    ids : list
        List of ids (str) which triggered the callback. 
    """
    def get_trigger_id(component):
        id = component['prop_id'].split('.')[0]
        try:
            # id is dictionary
            return json.loads(id)
        except:
            # id is string
            return id

    return [get_trigger_id(component) for component in ctx.triggered]

def get_dist_trigger_ids(ctx):
    """
    Parameters
    ----------
    ctx : dash.callback_context

    Returns
    -------
    ids : list
        List of smoother ids (str) which triggered the callback.
    """
    trigger_ids = get_trigger_ids(ctx)
    return [
        id['dist-id'] for id in trigger_ids 
        if isinstance(id, dict) and id.get('dist-cls')
    ]

def update_records(curr_records, updates):
    """
    Inplace update of current records with updates.

    Parameters
    ----------
    curr_records : list of dicts
        Current records (records formatted).

    updates : list of dicts
        Updates to the records (records format).
    """
    assert len(curr_records) == len(updates), (
        'Current records and updates must be of the same length'
    )
    [curr.update(new) for curr, new in zip(curr_records, updates)]

def records_to_dict(records):
    data = {}
    for i, record in enumerate(records):
        for key, item in record.items():
            if key not in data:
                data[key] = [None] * i
            data[key].append(item)
    return data