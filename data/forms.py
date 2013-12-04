import collections

from django import forms
from django.forms.models import ModelFormMetaclass, ModelForm, ErrorList
from django.utils.encoding import force_text
from django.utils.functional import cached_property

from data.models import Instance, Field
from data.fields import fields


class FieldForm(ModelForm):

    def clean_type_params(self):
        field_type = self.cleaned_data.get("type")
        type_params = self.cleaned_data.get("type_params", {})
        # Try to initialize a form field.
        if field_type:
            field_impl = fields[field_type]
            type_params = field_impl.clean_type_params(**type_params)
        # All done!
        return type_params

    class Meta:
        model = Field


def form_name_for_field(field):
    return "_field_{name}".format(
        name = field.name,
    )


class InstanceFormBase(ModelForm):

    @classmethod
    def deserialize_instance_data(cls, instance):
        instance_data = instance.data
        return dict(
            (form_name_for_field(field), field_implementation.deserialize(instance_data.get(field.name, None)))
            for field, field_implementation
            in cls._field_implementations
        )

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, error_class=ErrorList, label_suffix=':',
                 empty_permitted=False, instance=None):
        # Set the initial.
        if instance:
            initial = initial or {}
            initial.update(self.deserialize_instance_data(instance))
        # All done!
        super(InstanceFormBase, self).__init__(data, files, auto_id, prefix, initial, error_class, label_suffix, empty_permitted, instance)

    @cached_property
    def instance_data(self):
        return collections.OrderedDict(
            (field.name, field_implementation.serialize(self.cleaned_data.get(form_name_for_field(field))))
            for field, field_implementation
            in self._field_implementations
        )

    def clean(self):
        data = self.cleaned_data
        # Validate unique instance ID and model.
        if self.instance.pk is not None:
            external_id = self.cleaned_data.get("external_id")
            matching_instance = Instance.objects.filter(
                model = self._model,
                external_id = external_id,
            ).exclude(
                pk = self.instance.pk,
            )
            if matching_instance.exists():
                raise forms.ValidationError("{model} with ID {external_id} already exists.".format(
                    model = self._model,
                    external_id = external_id,
                ))
        # All done!
        return data

    def save(self, commit=True):
        instance = super(InstanceFormBase, self).save(commit=False)
        instance.model = self._model
        # Set the instance data.
        instance_data = self.instance_data
        instance.name = force_text(next(iter(instance_data.values()), instance.external_id))
        instance.data = instance_data
        # Commit the model.
        if commit:
            instance.save()
            self.save_m2m()
        # Return the model.
        return instance

    class Meta:
        model = Instance


def form_for_model(model, base_form=InstanceFormBase):
    # Instantiate all field implementations.
    field_implementations = [
        (field, field.get_field_implementation())
        for field
        in model.field_set.all()
    ]
    # Start creating the form.
    form_attrs = {
        "_model": model,
        "_field_implementations": field_implementations,
    }
    # Assemble the fields.
    for field, field_impl in field_implementations:
        field_kwargs = {
            "label": field.name,
        }
        form_attrs[form_name_for_field(field)] = field_impl.form_field(**field_kwargs)
    # Create the form class.
    return ModelFormMetaclass("InstanceForm", (base_form,), form_attrs)
