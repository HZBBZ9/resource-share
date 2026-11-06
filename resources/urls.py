from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('', views.ResourceListView.as_view(), name='resource-list'),
    path('my/', views.MyResourcesView.as_view(), name='my-resources'),
    path('new/', views.ResourceCreateView.as_view(), name='resource-create'),
    path('<int:pk>/', views.ResourceDetailView.as_view(), name='resource-detail'),
    path('<int:pk>/edit/', views.ResourceUpdateView.as_view(), name='resource-update'),
    path('<int:pk>/download/', views.download_resource, name='resource-download'),
    path('<int:pk>/delete/', views.ResourceDeleteView.as_view(), name='resource-delete'),

    # 登录 / 登出 / 注册
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
]
