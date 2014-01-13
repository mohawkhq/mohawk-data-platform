import collections
from functools import wraps

from django import forms
from django.core.exceptions import ValidationError
from django.db.models.fields.related import ManyToOneRel
from django.contrib import admin
from django.contrib.admin.widgets import AdminTextInputWidget, AdminTextareaWidget, ForeignKeyRawIdWidget, ManyToManyRawIdWidget, AdminDateWidget, AdminTimeWidget, AdminSplitDateTime
from django.utils import dateparse


class Field(object):

    form_class = forms.CharField

    widget = None

    @classmethod
    def clean_type_params(cls, **type_params):
        """Validates and cleans the type params supplied by the FieldForm."""
        if type_params:
            raise ValidationError("Unknown parameter '{name}'.".format(
                name = type_params.keys()[0],
            ))
        return {}

    def __init__(self, **type_params):
        if type_params:
            raise ValueError("Unexpected type params {type_params!r}.".format(
                type_params = type_params,
            ))

    def form_field(self, **kwargs):
        """Returns an instantiated form field."""
        form_class = kwargs.pop("form_class", self.form_class)
        kwargs.setdefault("widget", self.widget)
        return form_class(**kwargs)

    def serialize(self, value):
        """
        Serializes the value to a json representation.

        The value will be of the type returned by the form field's clean() method.
        """
        return value

    def deserialize(self, value):
        """
        Unserializes the value from a json representation.

        The returned value must be parseable by the form_field.
        """
        return value


class RequiredFieldMixin(object):

    """A field that has a 'required' parameter, defaulting to true."""

    @classmethod
    def clean_type_params(cls, **type_params):
        required = type_params.pop("required", True)
        if not isinstance(required, bool):
            raise ValidationError("Parameter 'required' should be a boolean.")
        type_params = super(RequiredFieldMixin, cls).clean_type_params(**type_params)
        type_params["required"] = required
        return type_params

    def __init__(self, required, **type_params):
        self.required = required
        super(RequiredFieldMixin, self).__init__(**type_params)

    def form_field(self, **kwargs):
        kwargs.setdefault("required", self.required)
        return super(RequiredFieldMixin, self).form_field(**kwargs)


class ChoiceFieldMixin(object):

    """A field that takes an optional 'choices' parameter."""

    @classmethod
    def clean_type_params(cls, **type_params):
        choices = type_params.pop("choices", None)
        # Validate the choices.
        if choices is not None:
            if not isinstance(choices, (tuple, list)):
                raise ValidationError("Parameter 'choices' should be a list.")
            for choice in choices:
                if not isinstance(choice, (tuple, list)) and not len(choice) == 2:
                    raise ValidationError("Each choice should be a list containing [value, label].")
        # All done!
        type_params = super(ChoiceFieldMixin, cls).clean_type_params(**type_params)
        type_params["choices"] = choices
        return type_params
        
    def __init__(self, choices=None, **type_params):
        self.choices = choices
        super(ChoiceFieldMixin, self).__init__(**type_params)

    def form_field(self, **kwargs):
        if self.choices is not None:
            kwargs.setdefault("form_class", forms.ChoiceField)
            kwargs.setdefault("choices", self.choices)
        return super(ChoiceFieldMixin, self).form_field(**kwargs)


def ignores_none(func):
    @wraps(func)
    def do_ignores_none(self, value):
        if value is None:
            return None
        return func(self, value)
    return do_ignores_none


# Simple fields.

class TextField(RequiredFieldMixin, ChoiceFieldMixin, Field):

    widget = AdminTextInputWidget


class LongTextField(RequiredFieldMixin, Field):

    widget = AdminTextareaWidget


class IntegerField(RequiredFieldMixin, ChoiceFieldMixin, Field):

    form_class = forms.IntegerField


class FloatField(RequiredFieldMixin, Field):

    form_class = forms.FloatField


class DateField(RequiredFieldMixin, Field):

    form_class = forms.DateField

    widget = AdminDateWidget

    @ignores_none
    def deserialize(self, value):
        value = super(DateField, self).deserialize(value)
        return dateparse.parse_date(value)

    @ignores_none
    def serialize(self, value):
        value = super(DateField, self).serialize(value)
        return value.isoformat()


class TimeField(RequiredFieldMixin, Field):

    form_class = forms.TimeField

    widget = AdminTimeWidget

    @ignores_none
    def deserialize(self, value):
        value = super(TimeField, self).deserialize(value)
        return dateparse.parse_time(value)

    @ignores_none
    def serialize(self, value):
        value = super(TimeField, self).serialize(value)
        return value.isoformat()


class DateTimeField(RequiredFieldMixin, Field):

    form_class = forms.DateTimeField

    widget = AdminSplitDateTime

    @ignores_none
    def deserialize(self, value):
        value = super(DateTimeField, self).deserialize(value)
        return dateparse.parse_datetime(value)

    @ignores_none
    def serialize(self, value):
        value = super(DateTimeField, self).serialize(value)
        return value.isoformat()


class BooleanField(Field):

    form_class = forms.BooleanField

    def form_field(self, **kwargs):
        kwargs.setdefault("required", False)
        return super(BooleanField, self).form_field(**kwargs)


# File fields.

class FileField(RequiredFieldMixin, Field):

    form_class = forms.ModelChoiceField

    widget = ForeignKeyRawIdWidget

    def form_field(self, **kwargs):
        from data.models import File
        # Create the widget.
        widget = self.widget(
            rel = ManyToOneRel(
                field = None,
                to = File,
                field_name = "id",
            ),
            admin_site = admin.site,
        )
        kwargs["widget"] = widget
        # Add in extra required arguments.
        kwargs["queryset"] = File.objects.all()
        # All done!
        return super(FileField, self).form_field(**kwargs)

    @ignores_none
    def deserialize(self, value):
        from data.models import File
        value = super(FileField, self).deserialize(value)
        storage = File._meta.get_field("file").storage
        root = storage.url("/")
        try:
            # HACK: Converting a stored URL into a file name.
            # Not elegant, but allows a denormalized file to be
            # stored in the JSON.
            return File.objects.filter(file=value[len(root):])[0]
        except IndexError:
            return None

    @ignores_none
    def serialize(self, value):
        value = super(FileField, self).serialize(value)
        return value.file.url


# Relations.

class ModelField(RequiredFieldMixin, Field):

    form_class = forms.ModelChoiceField

    widget = ForeignKeyRawIdWidget

    @classmethod
    def clean_type_params(cls, **type_params):
        from data.models import Model
        # Get the model ID.
        try:
            model_id = type_params.pop("model_id")
        except KeyError:
            raise ValidationError("Required parameter 'model_id' not provided.")
        # Validate the model ID.
        try:
            if isinstance(model_id, int):
                model = Model.objects.get(id=model_id)
            elif isinstance(model_id, basestring):
                model = Model.objects.get(external_id=model_id)
            else:
                raise ValidationError("Required parameter 'model_id' should be a number or a string.")
        except Model.DoesNotExist:
            raise ValidationError("Unknown model_id.")
        # Validate remaining type params.
        type_params = super(ModelField, cls).clean_type_params(**type_params)
        # Update type params.
        type_params["model_id"] = model.id
        return type_params

    def __init__(self, model_id, **type_params):
        super(ModelField, self).__init__(**type_params)
        self.model_id = model_id

    def form_field(self, **kwargs):
        from data.models import Instance
        kwargs.setdefault("queryset", Instance.objects.all().filter(
            model__id = self.model_id,
        ))
        # Create the widget.
        widget = self.widget(
            rel = ManyToOneRel(
                field = None,
                to = Instance,
                field_name = "id",
            ),
            admin_site = admin.site,
        )
        kwargs["widget"] = widget
        # HACK: Override URL parameters on widget.
        base_url_parameters = widget.url_parameters
        def url_parameters():
            params = base_url_parameters()
            params["model"] = self.model_id
            return params
        widget.url_parameters = url_parameters
        return super(ModelField, self).form_field(**kwargs)

    @ignores_none
    def serialize(self, value):
        return super(ModelField, self).serialize(value.external_id)

    @ignores_none
    def deserialize(self, value):
        from data.models import Instance
        try:
            return Instance.objects.get(
                model_id = self.model_id,
                external_id = super(ModelField, self).deserialize(value),
            )
        except Instance.DoesNotExist:
            return None


class MultiModelField(ModelField):

    form_class = forms.ModelMultipleChoiceField

    widget = ManyToManyRawIdWidget

    def deserialize(self, value):
        return filter(None, map(super(MultiModelField, self).deserialize, value or ()))

    def serialize(self, value):
        return filter(None, map(super(MultiModelField, self).serialize, value or ()))


fields = collections.OrderedDict((
    ("text", TextField),
    ("integer", IntegerField),
    ("float", FloatField),
    ("date", DateField),
    ("time", TimeField),
    ("datetime", DateTimeField),
    ("boolean", BooleanField),
    ("file", FileField),
    ("long text", LongTextField),
    ("model", ModelField),
    ("multi model", MultiModelField),
))
