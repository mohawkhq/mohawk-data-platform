import posixpath

from django.db import models
from django.contrib.auth.models import User, Group

from jsonfield import JSONField

from data.fields import fields
from data import uuid


# Base classes.

class MetaMixin(models.Model):

    date_created = models.DateTimeField(
        auto_now_add = True,
        db_index = True,
    )

    date_modified = models.DateTimeField(
        auto_now = True,
        db_index = True,
    )

    class Meta:
        abstract = True


class NamedMixin(models.Model):

    name = models.CharField(
        max_length = 200,
    )

    def __unicode__(self):
        return self.name

    class Meta:
        abstract = True


class ExternalIdMixin(models.Model):

    external_id = models.CharField(
        "ID",
        max_length = 255,
        default = uuid.generate,
    )

    def __unicode__(self):
        return self.external_id

    class Meta:
        abstract = True


class OnlineMixin(models.Model):

    is_online = models.BooleanField(
        "online",
        default = True,
    )

    class Meta:
        abstract = True


# Data model.


class Application(NamedMixin, ExternalIdMixin, OnlineMixin, MetaMixin):

    class Meta:
        ordering = ("-date_modified",)
        unique_together = (
            ("external_id",),
        )


def file_upload_to(instance, filename):
    name, ext = posixpath.splitext(filename)
    name = uuid.generate()
    return posixpath.join("files", name + ext)


class File(NamedMixin, MetaMixin):

    file = models.FileField(
        upload_to = file_upload_to,
    )

    class Meta:
        ordering = ("-date_modified",)


class Model(NamedMixin, ExternalIdMixin, OnlineMixin, MetaMixin):

    admin_users = models.ManyToManyField(
        User,
        blank = True,
        verbose_name = "users",
    )

    admin_groups = models.ManyToManyField(
        Group,
        blank = True,
        verbose_name = "groups",
    )

    applications = models.ManyToManyField(
        Application,
        blank = True,
    )

    class Meta:
        ordering = ("-date_modified",)
        unique_together = (
            ("external_id",),
        )


class Field(NamedMixin):

    model = models.ForeignKey(
        Model,
    )

    type = models.CharField(
        max_length = 20,
        choices = zip(fields.keys(), fields.keys()),
        default = fields.keys()[0],
    )

    type_params = JSONField(
        "Parameters",
        blank = True,
        default = {},
    )

    def get_field_implementation(self):
        return fields[self.type](**self.type_params)

    order = models.IntegerField(
        default = 0,
    )

    class Meta:
        unique_together = (
            ("model", "name",),
        )
        ordering = ("order", "pk",)


# Instances of a data model.

class Instance(NamedMixin, ExternalIdMixin, OnlineMixin, MetaMixin):

    model = models.ForeignKey(
        Model,
    )

    data = JSONField(
        default = {},
        editable = False,
    )

    class Meta:
        ordering = ("-date_modified",)
        unique_together = (
            ("model", "external_id",),
        )
