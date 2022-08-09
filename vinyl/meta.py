from django.db.models import ForeignKey, OneToOneField, ManyToManyField
from django.db.models.query_utils import DeferredAttribute

from vinyl.model import VinylModel

# (<django.db.models.fields.BigAutoField: id>,
#  <django.db.models.fields.CharField: f>,
#  <django.db.models.fields.related.OneToOneField: a_ptr>,
#  <django.db.models.fields.related.OneToOneField: b_ptr>,
#  <django.db.models.fields.related.ForeignKey: title>,
#  <django.db.models.fields.IntegerField: x>,
#  <django.db.models.fields.DateTimeField: created>)

# class VinylMeta(type):

# FIXME check django.db.models.fields.related_descriptors
def get_field(val):
    if (field := getattr(val, 'field', None)) and field.__module__.startswith('django.db.models.fields'):
        return field



def copy_namespace(model):
    ns = {}
    model_vars = {
        field.name: getattr(model, field.name)
        for field in model._meta.fields
    }
    model_vars.update(vars(model))
    for key, val in model_vars.items():
        if hasattr(val, 'field') and val.__module__ == 'django.db.models.fields.related_descriptors':
            ns[key] = val # TODO modify
    return ns


def make_vinyl_model(model):
    print('make')
    if hasattr(model, 'vinyl_model'):
        return model.vinyl_model
    ns = copy_namespace(model)
    bases = (VinylModel,)
    newcls = model.vinyl_model = type(model.__name__, bases, ns)
    newcls._model = model
    return newcls

# def __new__(metacls, name, bases, namespace, *, model):
#     MODULE = 'django.db.models.fields.related_descriptors'
#     ns = dict(namespace)
#     ns['_model'] = model
#     #TODO
#     for field in model._meta.fields:
#         if isinstance(field, (ForeignKey, OneToOneField)):
#             ns[field.name] = FKeyProxy(field.name, getattr(model, field.name))
#
#
#     for key, val in namespace.items():
#         if isinstance(val, DeferredAttribute) or val.__class__.__module__ == MODULE:
#             # print(key, val)
#             if val.__class__.__name__.endswith('ToManyDescriptor'):
#                 new_val = ManagerProxy(key, val)
#             elif val.__class__.__name__.endswith('ToOneDescriptor'):
#                 new_val = FKeyProxy(key, val)
#             else:
#                 new_val = FKeyProxy(key, val)
#             ns[key] = new_val
#     cls = super().__new__(metacls, name, bases, ns)
#     return cls
#