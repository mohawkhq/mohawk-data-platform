import json, random
from functools import wraps

from django.views import generic
from django.http import HttpResponse, Http404
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from cross_origin.views import AccessControlMixin

from data.models import Application, Model, Instance


def json_response(request, data, status=200):
    encoded_data = json.dumps(data, separators=(u",", u":")).encode("utf-8")
    mime_type = "application/json"
    # Allow JSONP.
    jsonp_callback = request.GET.get("callback")
    if jsonp_callback:
        encoded_data = "{jsonp_callback}({encoded_data});".format(
            jsonp_callback = jsonp_callback.encode("utf-8"),
            encoded_data = encoded_data,
        )
        mime_type = "application/javascript"
    # Write the response.
    response = HttpResponse(encoded_data, status=status)
    response["Content-Type"] = "{mime_type}; charset=utf-8".format(
        mime_type = mime_type,
    )
    response["Content-Length"] = str(len(encoded_data))
    return response


def json_error_response(func):
    @wraps(func)
    def do_json_error_response(self, request, *args, **kwargs):
        try:
            return func(self, request, *args, **kwargs)
        except PermissionDenied:
            return json_response(request, {
                "status": "Permission denied",
                "message": "You do not have permission to access this resource.",
            }, status=403)
        except Http404:
            return json_response(request, {
                "status": "Not found",
                "message": "The resource you attempted to access does not exist.",
            }, status=404)
    return do_json_error_response


INDEX_MESSAGES = (
    "Any fool can use a computer. Many do.",
    "There are 10 types of people in the world: those who understand binary, and those who don't.",
    "If brute force doesn't solve your problems, then you aren't using enough.",
    "My software never has bugs. It just develops random features.",
    "Programmers are tools for converting caffeine into code.",
    "If at first you don't succeed; call it version 1.0",
)


class IndexView(AccessControlMixin, generic.View):

    def get(self, request):
        return json_response(request, {
            "status": "OK",
            "message": random.choice(INDEX_MESSAGES),
        })


class InstanceApiView(AccessControlMixin, generic.View):

    def get_instance_set(self):
        return Instance.objects.filter(
            model__is_online = True,
            is_online = True,
        ).values_list(
            "external_id",
            "date_created",
            "date_modified",
            "data",
            "model__external_id",
        ).order_by()  # Don't apply any ordering, to speed up access.

    def format_instance_data(self, instance_tuple):
        # Pull apart the instance tuple.
        external_id, date_created, date_modified, instance_data, model_external_id = instance_tuple
        # Coerce the instance dict.
        if isinstance(instance_data, basestring):
            instance_data = json.loads(instance_data)
        # Create the instance dict.
        instance_data["_id"] = external_id
        instance_data["_date_created"] = date_created.isoformat()
        instance_data["_date_modified"] = date_modified.isoformat()
        instance_data["_model"] = model_external_id
        return instance_data


class ApplicationInstanceListView(InstanceApiView):

    def get_instance_set(self):
        return super(ApplicationInstanceListView, self).get_instance_set().filter(
            model__applications = self.application,
        )

    @json_error_response
    def dispatch(self, request, application_external_id, **kwargs):
        # Check the application exists.
        self.application = get_object_or_404(Application,
            is_online = True,
            external_id = application_external_id,
        )
        # Dispatch the response.
        return super(ApplicationInstanceListView, self).dispatch(request, application_external_id=application_external_id, **kwargs)

    def get(self, request, application_external_id):
        return json_response(request, {
            "status": "OK",
            "message": u"Instances within application {application} were successfully loaded.".format(
                application = self.application,
            ),
            "instances": map(self.format_instance_data, self.get_instance_set().iterator()),
        })


class ModelApiView(InstanceApiView):

    def get_instance_set(self):
        return super(ModelApiView, self).get_instance_set().filter(
            model = self.model,
        )

    @json_error_response
    def dispatch(self, request, model_external_id, **kwargs):
        # Check the model exists.
        self.model = get_object_or_404(Model,
            is_online = True,
            external_id = model_external_id,
        )
        # Dispatch the response.
        return super(ModelApiView, self).dispatch(request, model_external_id=model_external_id, **kwargs)


class InstanceListView(ModelApiView):

    def get(self, request, model_external_id):
        return json_response(request, {
            "status": "OK",
            "message": u"Instances of {model} were successfully loaded.".format(
                model = self.model,
            ),
            "instances": map(self.format_instance_data, self.get_instance_set().iterator()),
        })


class InstanceDetailView(ModelApiView):

    def get(self, request, model_external_id, instance_external_id):
        # Load the instance.
        instance = get_object_or_404(self.get_instance_set(),
            external_id = instance_external_id,
        )
        # Render the instance.
        return json_response(request, {
            "status": "OK",
            "message": u"Instance of {model} was successfully loaded.".format(
                model = self.model,
            ),
            "instance": self.format_instance_data(instance),
        })
