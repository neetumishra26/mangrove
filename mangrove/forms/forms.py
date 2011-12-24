from collections import OrderedDict
from copy import deepcopy

from mangrove.forms.fields import Field
from mangrove.forms.fields import TextField

def get_declared_fields(bases, attrs):
    fields = [(field_name, attrs.pop(field_name)) for field_name, obj in attrs.items() if isinstance(obj, Field)]

    for base in bases[::-1]:
        if hasattr(base, 'base_fields'):
            fields = base.base_fields.items() + fields

    return OrderedDict(fields)

class MangroveFormMetaclass(type):
    def __new__(cls, name, bases, attrs):
        attrs['base_fields'] = get_declared_fields(bases, attrs)
        return super(MangroveFormMetaclass,
                     cls).__new__(cls, name, bases, attrs)

class BaseForm(object):

    def __init__(self):
        self.fields = deepcopy(self.base_fields)

    def __getitem__(self, name):
        field = self.fields[name]
        return field

class Form(BaseForm):
    __metaclass__ = MangroveFormMetaclass

    @classmethod
    def build_from_dct(cls, dct):
        attrs = {'code': dct['code']}
        fields = []
        for field_json in dct['fields']:
            field_class_name = field_json.pop('_class')
            field = type(field_class_name, (eval(field_class_name),Field,), {})(**field_json)
            fields.append((field.name, field))
        attrs['base_fields'] = OrderedDict(fields)
        return type('Form', (BaseForm,), attrs)()

