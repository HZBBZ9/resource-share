from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import RegisterForm, ResourceForm
from .models import Resource


class ResourceListView(ListView):
    """资源列表页，支持关键词搜索、分类筛选和排序。"""

    model = Resource
    template_name = 'resources/resource_list.html'
    context_object_name = 'resources'
    paginate_by = 20

    def get_queryset(self):
        queryset = Resource.objects.select_related('uploader')
        q = self.request.GET.get('q', '').strip()
        category = self.request.GET.get('category', '').strip()
        sort = self.request.GET.get('sort', 'newest')
        if q:
            queryset = queryset.filter(title__icontains=q)
        if category and category != 'all':
            queryset = queryset.filter(category=category)
        if sort == 'downloads':
            queryset = queryset.order_by('-download_count', '-created_at')
        else:
            queryset = queryset.order_by('-created_at')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '').strip()
        context['category'] = self.request.GET.get('category', '').strip() or 'all'
        context['sort'] = self.request.GET.get('sort', 'newest')
        context['categories'] = Resource.CATEGORY_CHOICES
        return context


class MyResourcesView(LoginRequiredMixin, ListView):
    """当前用户上传的所有资料。"""

    model = Resource
    template_name = 'resources/my_resources.html'
    context_object_name = 'resources'
    paginate_by = 20

    def get_queryset(self):
        return Resource.objects.filter(uploader=self.request.user).select_related('uploader')


class ResourceDetailView(DetailView):
    model = Resource
    template_name = 'resources/resource_detail.html'
    context_object_name = 'resource'


class ResourceCreateView(LoginRequiredMixin, CreateView):
    """上传资料（需登录）。"""

    model = Resource
    form_class = ResourceForm
    template_name = 'resources/resource_form.html'

    def form_valid(self, form):
        form.instance.uploader = self.request.user
        return super().form_valid(form)


class ResourceUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """编辑自己的资料。"""

    model = Resource
    form_class = ResourceForm
    template_name = 'resources/resource_form.html'

    def test_func(self):
        resource = self.get_object()
        return resource.uploader == self.request.user or self.request.user.is_staff


class ResourceDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """删除自己的资料。"""

    model = Resource
    template_name = 'resources/resource_confirm_delete.html'
    success_url = reverse_lazy('resource-list')

    def test_func(self):
        resource = self.get_object()
        return resource.uploader == self.request.user or self.request.user.is_staff


@login_required
def download_resource(request, pk):
    """下载资料，计数 +1，并把文件作为附件返回。"""
    resource = get_object_or_404(Resource, pk=pk)
    resource.download_count += 1
    resource.save(update_fields=['download_count'])
    resource.file.open('rb')
    response = FileResponse(resource.file, as_attachment=True, filename=resource.file.name.split('/')[-1])
    return response


def register(request):
    """用户注册，注册后自动登录。"""
    if request.user.is_authenticated:
        return redirect('resource-list')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('resource-list')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})
