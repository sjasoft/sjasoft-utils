from decimal import Decimal
from types import GeneratorType
import uuid


def dataframe_sum(df, *fields):
    if fields:
        return df.groupby(fields).agg('sum').to_dict(orient='records')
    else:
        return df.drop(columns='calendar_day').sum().to_dict()
def value_fixer(value_test, fix):
    '''
    Generalized value fixer
    :param value_test: tests for whether a scalar value needs fixing
    :param fix: function that fixes the value
    :returns: function for fixing the object by these criteria which creats a new fixed object
    '''

    def fix_it(obj):
        if isinstance(obj, dict):
            return {k: fix_it(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [fix_it(v) for v in obj]
        elif isinstance(obj, tuple):
            return tuple([fix_it(v) for v in obj])
        elif isinstance(obj, GeneratorType):
            return (fix_it(v) for v in obj)
        else:
            return fix(obj) if value_test(obj) else obj

    return fix_it


def value_dropper(drop_test, sentinel=None):
    if sentinel is None:
        sentinel = uuid.uuid4().hex
    to_be_discarded = lambda x: (x == sentinel) or drop_test(x)

    def drop_filtered(obj):
        temp = obj
        if isinstance(obj, dict):
            temp = {k: v for k, v in {k: drop_filtered(v) for k, v in obj.items()}.items() if not to_be_discarded(v)}
        elif isinstance(obj, list) or isinstance(obj, tuple):
            temp = [i for i in [drop_filtered(l) for l in obj] if not to_be_discarded(i)]
            if isinstance(obj, tuple):
                temp = tuple(temp)
        return sentinel if drop_test(temp) else temp

    def drop_bad_values(obj):
        filtered = drop_filtered(obj)
        return None if (filtered == sentinel) else filtered

    return drop_bad_values


def decimal_fix(d):
    return float(d) if (d % 1) else int(d)


def to_decimal(d):
    return Decimal(str(d)) if isinstance(d, float) else d


remove_falsey = value_dropper(drop_test=lambda o: o == '')
float_to_int = value_fixer(value_test=lambda o: isinstance(o, float), fix=int)

clear_dict = remove_falsey


def simply_flatten(obj):
    '''
    returns a list of the scalar leaf objects.
    '''
    flat = []

    def flatten(x):
        if isinstance(x, dict):
            for v in x.values():
                flatten(v)
        elif isinstance(x, list) or isinstance(x, tuple):
            for v in x:
                flatten(v)
        else:
            flat.append(x)

    flatten(obj)
    return flat

def get_or_default(src, field, default):
    val = src.get(field)
    if val is None:
        return default
    return val

def adder_if(target, is_valid=None):
    '''
    Creates and returns a closure which will add a value (at key if target is dict) to target if it is
    valid.
    :param target: the dict, list or set to optionally add to
    :param is_valid: value validity check defaults to not None
    :return: function accepting a value for list and set or a key and value for dict
    '''
    is_valid = is_valid or (lambda v: v is not None)
    dict_add = lambda k, v: target.update({k: v}) if is_valid(v) else None
    list_add = lambda v: target.append(v) if is_valid(v) else None
    set_add = lambda v: target.add(v) if is_valid(v) else None

    if isinstance(target, dict):
        return dict_add
    elif isinstance(target, list):
        return list_add
    elif isinstance(target, set):
        return set_add
