from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    ProfileView,
    TaskDetailDelete,
    TaskListById,
    TaskListCreateView,
    TaskListUpdate,
    TaskListView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("tasks/", TaskListCreateView.as_view(), name="task-list-create"),
    path("tasks_update/", TaskListUpdate.as_view(), name="tasks_update"),
    path("tasklist_view/", TaskListView.as_view(), name="TaskListView"),
    path("tasklist_id/", TaskListById.as_view(), name="TaskListById"),
    path("taskdetail_delete/", TaskDetailDelete.as_view(), name="TaskDetailDelete"),
]
