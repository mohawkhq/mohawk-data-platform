import posixpath

from django.contrib import admin
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Q
from django.contrib.staticfiles.storage import staticfiles_storage

from data.models import Application, File, Model, Field, Instance
from data.forms import form_for_model, form_name_for_field, FieldForm


class ApplicationAdmin(admin.ModelAdmin):

    date_hierarchy = "date_modified"

    search_fields = ("name", "=external_id",)

    list_display = ("name", "external_id", "is_online", "date_created", "date_modified",)

    list_filter = ("is_online",)

    fieldsets = (
        (None, {
            "fields": (("name", "is_online",), "external_id",),
        }),
    )

admin.site.register(Application, ApplicationAdmin)


class FileAdmin(admin.ModelAdmin):

    date_hierarchy = "date_modified"

    search_fields = ("name",)

    list_display = ("get_preview", "name", "date_created", "date_modified",)

    fieldsets = (
        (None, {
            "fields": ("name", "file",),
        }),
    )

    def get_preview(self, obj):
        # Get the file extension.
        url = obj.file.url
        _, extension = posixpath.splitext(url)
        extension = extension.lower()
        # Render an image if appropriate file type.
        if extension in (".png", ".jpg", ".jpeg", ".gif"):
            url = url
        else:
            url = staticfiles_storage.url("data/img/document.png")
        return u'<div style="width: 100px; height: 75px; background-image: url({url}); background-repeat: no-repeat; background-size: contain; background-position: center center)"></div>'.format(
            url = url,
        )
    get_preview.allow_tags = True
    get_preview.short_description = "file"
    get_preview.admin_order_field = ("name",)

admin.site.register(File, FileAdmin)


class FieldInline(admin.TabularInline):

    fields = ("name", "type", "type_params", "order",)

    extra = 0

    model = Field

    form = FieldForm


class ModelAdmin(admin.ModelAdmin):

    date_hierarchy = "date_modified"

    search_fields = ("name", "=external_id",)

    list_display = ("name", "external_id", "is_online", "date_created", "date_modified",)

    list_filter = ("is_online", "applications",)

    fieldsets = (
        (None, {
            "fields": (("name", "is_online",), "external_id",),
        }),
        ("Applications", {
            "fields": ("applications",),
            "classes": ("collapse",),
        }),
        ("Administrators", {
            "fields": ("admin_users", "admin_groups",),
            "classes": ("collapse",),
        }),
    )

    inlines = (FieldInline,)

    filter_horizontal = ("admin_users", "admin_groups", "applications",)

admin.site.register(Model, ModelAdmin)


def models_for_user(user):
    model_list = Model.objects.all()
    # Model admins can see everything.
    if not user.has_perm("data.change_model"):
        model_list = model_list.filter(
            Q(admin_users = user) | Q(admin_groups__user = user),
        ).distinct()
    # All done!
    return model_list


class ModelListFilter(admin.SimpleListFilter):
    
    title = "model"
    
    parameter_name = "model"
    
    def lookups(self, request, model_admin):
        return [
            (unicode(model.id), unicode(model))
            for model
            in models_for_user(request.user)
        ]
        
    def queryset(self, request, queryset):
        value = self.value()
        if value is not None:
            queryset = queryset.filter(
                model__id = value,
            )
        return queryset


class ApplicationListFiler(admin.SimpleListFilter):

    title = "application"
    
    parameter_name = "application"
    
    def lookups(self, request, model_admin):
        return [
            (unicode(application.id), unicode(application))
            for application
            in Application.objects.filter(
                model__in = models_for_user(request.user),
            ).distinct()
        ]
        
    def queryset(self, request, queryset):
        value = self.value()
        if value is not None:
            queryset = queryset.filter(
                model__applications__id = value,
            )
        return queryset


class InstanceAdmin(admin.ModelAdmin):

    date_hierarchy = "date_modified"

    search_fields = ("name", "=external_id",)

    list_display = ("name", "model", "external_id", "is_online", "date_created", "date_modified",)

    list_filter = ("is_online", ModelListFilter, ApplicationListFiler,)

    raw_id_fields = ("model",)

    def get_model_list(self, request):
        return models_for_user(request.user)

    def get_model_for_request(self, request, obj):
        if obj:
            return obj.model
        try:
            model_id = request.GET["model"]
        except KeyError:
            return None
        return get_object_or_404(self.get_model_list(request), id=model_id)

    def get_queryset(self, request):
        return super(InstanceAdmin, self).get_queryset(request).filter(
            model__in = self.get_model_list(request),
        )

    def get_form(self, request, obj=None, **kwargs):
        model = self.get_model_for_request(request, obj)
        # Create the appropriate form.
        form = form_for_model(model)
        return super(InstanceAdmin, self).get_form(request, obj, form=form) 

    def get_fieldsets(self, request, obj=None):
        model = self.get_model_for_request(request, obj)
        # List the fieldsets.
        return (
            (None, {
                "fields": (("external_id", "is_online",),),
            }),
            ("Properties", {
                "fields": [
                    form_name_for_field(field)
                    for field
                    in model.field_set.all()
                ]
            }),
        )

    def add_view(self, request, form_url='', extra_context=None):
        model = self.get_model_for_request(request, None)
        # If we have a model, then we can generate a per-model form.
        if model:
            return super(InstanceAdmin, self).add_view(request, form_url, extra_context)
        # Without a model, we have to present a model chooser to the user.
        model_list = self.get_model_list(request)
        if len(model_list) > 1:
            return render(request, "admin/data/instance/model_list.html", {
                "title": "Choose model to add",
                "model_list": Model.objects.all(),
                "opts": self.model._meta,
            })
        else:
            return redirect(request.path + "?model={model_id}".format(
                model_id = model_list[0].id,
            ))

    def response_add(self, request, obj, post_url_continue=None):
        if "_addanother" in request.POST:
            self.message_user(request, u'The instance "{obj}" was added successfully. You may add another instance below.'.format(
                obj = obj,
            ))
            return redirect(request.build_absolute_uri())
        return super(InstanceAdmin, self).response_add(request, obj, post_url_continue)

    def has_add_permission(self, request):
        return super(InstanceAdmin, self).has_add_permission(request) and self.get_model_list(request).exists()

    def can_access_instance(self, request, obj):
        return (obj is None) or (obj is not None and self.get_model_list(request).filter(id=obj.model_id).exists())

    def has_change_permission(self, request, obj=None):
        return super(InstanceAdmin, self).has_change_permission(request, obj) and self.can_access_instance(request, obj)

    def has_delete_permission(self, request, obj=None):
        return super(InstanceAdmin, self).has_delete_permission(request, obj) and self.can_access_instance(request, obj)


admin.site.register(Instance, InstanceAdmin)
