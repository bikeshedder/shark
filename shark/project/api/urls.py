from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(
    "task-time-entry", views.TaskTimeEntryViewSet, basename="task-time-entry"
)
router.register("task", views.TaskViewSet, basename="task")

app_name = "project"
urlpatterns = router.urls
