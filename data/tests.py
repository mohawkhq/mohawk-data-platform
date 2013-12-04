import random

from django.test import TestCase
from django.test.utils import override_settings
from django.conf.urls import url, patterns, include

from data.models import Model, Application


urlpatterns = patterns("",

    url(r"^", include("data.urls", namespace="data")),

)


@override_settings(ROOT_URLCONF="data.tests")
class TestData(TestCase):

    maxDiff = None

    def setUp(self):
        self.application = Application.objects.create(
            name = "Test Application",
        )
        self.model = Model.objects.create(
            name = "Test Model",
        )
        self.model.field_set.create(
            name = "Name",
            type = "text",
        )
        self.instance = self.model.instance_set.create(
            name = "Test Instance",
            data = {
                "Name": "Test Instance",
            },
        )
        self.model2 = Model.objects.create(
            name = "Test Model 2",
        )
        self.model2.applications.add(self.application)
        self.model2.field_set.create(
            name = "Name",
            type = "text",
        )
        self.instance2 = self.model2.instance_set.create(
            name = "Test Instance 2",
            data = {
                "Name": "Test Instance 2",
            },
        )

    def getJsonForInstance(self, instance):
        instance_data = instance.data
        instance_data["_id"] = instance.external_id
        instance_data["_date_created"] = instance.date_created.isoformat()
        instance_data["_date_modified"] = instance.date_modified.isoformat()
        instance_data["_model"] = instance.model.external_id
        return instance_data

    def assertJsonResponse(self, url, expected_data, status=200):
        response = self.client.get(url)
        self.assertEqual(response.status_code, status)
        self.assertJSONEqual(response.content, expected_data)

    def assertNotFoundResponse(self, url):
        self.assertJsonResponse(url, {
            "status": "Not found",
            "message": "The resource you attempted to access does not exist.",
        }, status=404)

    def testIndexView(self):
        random.seed("test")
        self.assertJsonResponse("/", {
            "status": "OK",
            "message": "There are 10 types of people in the world: those who understand binary, and those who don't.",
        })

    def testApplicationInstanceListApiView(self):
        self.assertJsonResponse("/a/{}.json".format(self.application.external_id), {
            "instances": [self.getJsonForInstance(self.instance2)],
            "status": "OK",
            "message": "Instances within application Test Application were successfully loaded.",
        })

    def testApplicationInstanceListApiViewNotFound(self):
        self.assertNotFoundResponse("/a/bad_id.json")

    def testInstanceListApiView(self):
        self.assertJsonResponse("/{}.json".format(self.model.external_id), {
            "instances": [self.getJsonForInstance(self.instance)],
            "status": "OK",
            "message": "Instances of Test Model were successfully loaded.",
        })

    def testInstanceListApiViewNotFound(self):
        self.assertNotFoundResponse("/bad_id.json")

    def testInstanceDetailApiView(self):
        self.assertJsonResponse("/{}/{}.json".format(self.model.external_id, self.instance.external_id), {
            "instance": self.getJsonForInstance(self.instance),
            "status": "OK",
            "message": "Instance of Test Model was successfully loaded.",
        })

    def testInstanceDetailApiViewNotFound(self):
        self.assertNotFoundResponse("/{}/bad_id.json".format(self.model.external_id))
        self.assertNotFoundResponse("/bad_id/bad_id.json")
