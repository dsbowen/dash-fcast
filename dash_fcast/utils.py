def get_changed_cells(curr_records, prev_records):
    changed_cells = []
    records = zip(curr_records, prev_records)
    for i, (curr_record, prev_record) in enumerate(records):
        keys = set(list(curr_record.keys()) + list(prev_record.keys()))
        for key in keys:
            if curr_record.get(key) != prev_record.get(key):
                changed_cells.append((i, key))
    return changed_cells

def list_orient(records):
    data = {}
    for i, record in enumerate(records):
        for key, item in record.items():
            if key not in data:
                data[key] = [None] * i
            data[key].append(item)
    return data