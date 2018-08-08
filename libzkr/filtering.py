#parses filter and exclude arguments sent with request through get args
#and returns queryset with those applied
def filter_exclude_sort(queryset, args_dict):
    order_by = ''
    for arg, value in args_dict.items():
        if arg.startswith('filter__'):
            queryset = queryset.filter(**{arg[8:]: value})
            print(arg, value)
        if arg.startswith('exclude__'):
            print(arg, value)
            queryset = queryset.exclude(**{arg[9:]: value})
        if arg == 'sort':
            order_by = value
    if order_by:
        queryset = queryset.order_by(order_by)
    return queryset

