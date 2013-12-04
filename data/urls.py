from django.conf.urls import url, patterns

from data import views


urlpatterns = patterns("data.views",

    url(r"^$", views.IndexView.as_view()),

    url(r"^a/(?P<application_external_id>[^/]{,255})\.json$", views.ApplicationInstanceListView.as_view()),

    url(r"^(?P<model_external_id>[^/]{,255})\.json$", views.InstanceListView.as_view()),

    url(r"^(?P<model_external_id>[^/]{,255})/(?P<instance_external_id>[^/]{,255})\.json", views.InstanceDetailView.as_view()),

)