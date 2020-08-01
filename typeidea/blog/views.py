from datetime import date

from django.http import HttpResponse
from django.shortcuts import render,get_object_or_404
from django.views.generic import DetailView,ListView
from django.db.models import Q,F
from django.core.cache import cache
from django.template.loader import render_to_string


from .models import Post,Tag,Category
from config.models import SideBar
# Create your views here.

def content_html(self):
    """ 通过直接渲染模板 """
    from blog.models import Post  # 避免循环引用
    from comment.models import Comment

    result = ''
    if self.display_type == self.DISPLAY_HTML:
        result = self.content
    elif self.display_type == self.DISPLAY_LATEST:
        context = {
            'posts': Post.latest_posts(with_related=False)
        }
        result = render_to_string('config/blocks/sidebar_posts.html', context)
    elif self.display_type == self.DISPLAY_HOT:
        context = {
            'posts': Post.hot_posts()
        }
        result = render_to_string('config/blocks/sidebar_posts.html', context)
    elif self.display_type == self.DISPLAY_COMMENT:
        context = {
            'comments': Comment.objects.filter(status=Comment.STATUS_NORMAL)
        }
        result = render_to_string('config/blocks/sidebar_comments.html', context)
    return result

class CommonViewMixin:
    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        
        context.update({
            'sidebars':self.get_sidebars(),
        })
        #context.update({
        #    'sidebars':SideBar.get_all(),
        #})
        context.update(Category.get_navs())
        return context

    def get_sidebars(self):
        #view层处理Sidebar
        #sidebars= []
        #sidebars=SideBar.get_all()

        #sidebars=SideBar.get_all()
        sidebars=SideBar.objects.filter(status=SideBar.STATUS_SHOW)

        for sidebar in sidebars:
            sidebar.content_html=content_html(sidebar)

        return sidebars;

class IndexView(CommonViewMixin,ListView):
    queryset=Post.latest_posts()
    paginate_by=5
    context_object_name='post_list'
    template_name='blog/list.html'

class PostListView(ListView):
    queryset=Post.latest_posts()
    paginate_by=1
    context_object_name='post_list'
    template_name='blog/list.html'

def post_list(request,category_id=None,tag_id=None):
    tag=None
    category=None

    if tag_id:
        post_list,tag=Post.get_by_tag(tag_id)
    elif category_id:
        post_list,category=Post.get_by_category(category_id)
    else:
        post_list=Post.latest_posts()

    context={
        'category':category,
        'tag':tag,
        'post_list':post_list,
    }
    context.update(Category.get_navs())
    context.update({'sidebars':SideBar.get_all()})
    return render(request,'blog/list.html',context=context)

class PostDetailView(CommonViewMixin,DetailView):
    queryset=Post.latest_posts()
    template_name='blog/detail.html'
    context_object_name='post'
    pk_url_kwarg='post_id'

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        self.handle_visited()
        return response

    def get_object(self,queryset=None):
        pk=self.kwargs.get(self.pk_url_kwarg)
        key='detail:{}'.format(pk)
        print(key)
        obj=cache.get(key)
        if not obj:
            print('hit db')
            obj=super().get_object(queryset)
            cache.set(key,obj,60*5)
        return obj

    def handle_visited(self):
        increase_pv = False
        increase_uv = False
        uid = self.request.uid
        pv_key = 'pv:%s:%s' % (uid, self.request.path)
        if not cache.get(pv_key):
            increase_pv = True
            cache.set(pv_key, 1, 1*60)  # 1分钟有效

        uv_key = 'uv:%s:%s:%s' % (uid, str(date.today()), self.request.path)
        if not cache.get(uv_key):
            increase_uv = True
            cache.set(uv_key, 1, 24*60*60)  # 24小时有效

        if increase_pv and increase_uv:
            Post.objects.filter(pk=self.object.id).update(pv=F('pv') + 1, uv=F('uv') + 1)
        elif increase_pv:
            Post.objects.filter(pk=self.object.id).update(pv=F('pv') + 1)
        elif increase_uv:
            Post.objects.filter(pk=self.object.id).update(uv=F('uv') + 1)
    
def post_detail(request,post_id):
    try:
        post=Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        post=None
    context={'post':post}
    context.update(Category.get_navs())
    context.update({'sidebars':SideBar.get_all()})
    return render(request,'blog/detail.html',context=context)

class CategoryView(IndexView):
    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        category_id=self.kwargs.get('category_id')
        category=get_object_or_404(Category,pk=category_id)
        context.update({
            'category':category,
        })
        return context

    def get_queryset(self):
        '''重写queryset，根据分类过滤'''
        queryset=super().get_queryset()
        category_id=self.kwargs.get('category_id')
        return queryset.filter(category_id=category_id)

class TagView(IndexView):
    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        tag_id=self.kwargs.get('tag_id')
        tag=get_object_or_404(Tag,pk=tag_id)
        context.update({
            'tag':tag,
        })
        return context

    def get_queryset(self):
        '''重写queryset，根据分类过滤'''
        queryset=super().get_queryset()
        tag_id=self.kwargs.get('tag_id')
        return queryset.filter(tag__id=tag_id)

class SearchView(IndexView):
    def get_context_data(self):
        context=super().get_context_data()
        context.update({
            'keyword':self.request.GET.get('keyword','')
        })
        return context

    def get_queryset(self):
        queryset=super().get_queryset()
        keyword=self.request.GET.get('keyword')
        if not keyword:
            return queryset
        return queryset.filter(Q(title__icontains=keyword)|Q(desc__icontains=keyword))

class AuthorView(IndexView):
    def get_queryset(self):
        queryset=super().get_queryset()
        author_id=self.kwargs.get('owner_id')
        return queryset.filter(owner_id=author_id)
