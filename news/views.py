from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import PostForm
from .models import Post, Category
from .filters import PostsFilter
from datetime import datetime
from django.views.generic import TemplateView



# Создаем свой класс, который наследуется от ListView.
class PostsList(ListView):
    # Указываем модель, объекты которой мы будем выводить
    model = Post
    # Указываем имя шаблона, в котором будут все инструкции о том,
    # как именно пользователю должны быть показаны наши объекты
    template_name = 'post_list.html'
    # Это имя списка, в котором будут лежать все объекты.
    # Его надо указать, чтобы обратиться к списку объектов в html-шаблоне.
    context_object_name = 'posts'
    ordering = '-dateCreation'
    paginate_by = 5


# Создаем свой класс, который наследуется от DetailView.
class PostDetail(DetailView):
    # Модель всё та же, но мы хотим получать информацию по отдельной новости
    model = Post
    # Используем другой шаблон html
    template_name = 'post_detail.html'
    # Название объекта, в котором будет выбранная пользователем новость
    context_object_name = 'post'

class PostsSearch(ListView):
    model = Post
    template_name = 'post_search.html'
    context_object_name = 'posts'
    ordering = '-dateCreation'
    paginate_by = 5

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostsFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context


class PostDetail(DetailView):
    model = Post
    template_name = 'post_detail.html'
    context_object_name = 'posts'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()
        return context


class PostCreate(CreateView):
    form_class = PostForm
    model = Post
    template_name = 'post_create.html'
    permission_required = ('news.add_post',)


    def form_valid(self, form):
        post = form.save(commit=False)
        if self.request.method == 'POST':
            if self.request.path == '/news/articles/create/':
                post.post_type = 'AR'
                form.instance.author = self.request.user.author
        post.save()
        send_email_task.delay(post.pk)
        return super().form_valid(form)

    def get_type(self):
        if self.request.path == '/news/create/':
            return _('Adding news')
        return _('Adding article')


class PostUpdate(UpdateView):
    form_class = PostForm
    model = Post
    template_name = 'post_create.html'
    context_object_name = 'edit'


class PostDelete(DeleteView):
    model = Post
    template_name = 'post_delete.html'
    context_object_name = 'delete'


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'personal.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_authors'] = not self.request.user.groups.filter(name='authors').exists()
        return context


class CategoryDetail(ListView):
    model = Category
    template_name = 'category_list.html'
    context_object_name = 'categories'
    ordering = 'categoryName'
    paginate_by = 10


class PostByCategoryListView(ListView):
    model = Post
    template_name = 'post_list_by_category.html'
    context_object_name = 'posts'
    category = None

    def get_queryset(self):
        self.category = Category.objects.get(pk=self.kwargs['pk'])
        queryset = Post.objects.all().filter(postCategory__pk=self.category.pk)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categoryName'] = self.category.categoryName
        context['is_not_subscribed'] = self.request.user not in self.category.subscribers.all()
        context['category'] = self.category
        return context


@login_required
def subscribe(request, pk):
    user = request.user
    category = Category.objects.get(id=pk)
    category.subscribers.add(user)
    message = "Вы успешно подписались на рассылку новостей категории"
    return render(request, 'subscribe.html', {'category': category, 'message': message})







