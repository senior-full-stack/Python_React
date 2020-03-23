def get_dates(range_start, range_end, count):
    from datetime import datetime
    import random
    dates = []
    for x in range(0, count):
        epoch = random.randrange(range_start, range_end)
        dates.append(datetime.fromtimestamp(epoch))
    return dates