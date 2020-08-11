from datetime import date

from django.utils import timezone
from django.http import HttpResponse
from django.shortcuts import render,get_object_or_404
from django.views.generic import DetailView,ListView
from django.db.models import Q,F,Case, IntegerField, Value, When
from django.core.cache import cache

from .models import Post,Tag,Category
from config.models import SideBar
# Create your views here.

class CommonViewMixin:
    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        context.update({
            'sidebars':self.get_sidebars(),
        })
        context.update(Category.get_navs())
        return context

    def get_sidebars(self):
        return SideBar.objects.filter(status=SideBar.STATUS_SHOW);

class IndexView(CommonViewMixin,ListView):
    #queryset=Post.latest_posts()
    #非外键

    '''
    确定置顶 日期未失效2
    不置顶 （日期失效/未失效）/确定置顶 日期失效 0
    '''
    #queryset=Post.latest_posts().annotate(
    #    top=Case(
    #        When(topped_expired_time__lt=timezone.now(),is_top=True,then=Value(0)),
    #        default=Value(1),
    #        output_field=IntegerField(),
    #        ), 
    #).order_by('-top','-is_top','-id')

    '''
    确定置顶 日期未失效2
    不置顶 （日期失效/未失效）1
    确定置顶 日期失效 0
    '''
    #queryset=Post.latest_posts().annotate(
    #    top=Case(
    #        When(topped_expired_time__lt=timezone.now(),is_top=True,then=Value(0)),
    #        When(is_top=False,then=Value(1)),
    #        default=Value(2),
    #        output_field=IntegerField(),
    #        ), 
    #).order_by('-top','-id')

    #外键形式
    '''
    确定置顶 日期未失效2
    不置顶 （日期失效/未失效）/确定置顶 日期失效 / top外键为Null 0
    '''
    #queryset=Post.latest_posts().annotate(
    #    toptop=Case(
    #        When(top__topped_expired_time__lt=timezone.now(),top__is_top=True,then=Value(0)),
    #        default=Value(1),
    #        output_field=IntegerField(),
    #        ), 
    #).order_by('-toptop','-top','-id')

    '''
    确定置顶 日期未失效 2
    不置顶 （日期失效/未失效）/top外键为Null 1
    确定置顶 日期失效 0
    '''
    queryset=Post.latest_posts().annotate(
        toptop=Case(
            When(top__topped_expired_time__lt=timezone.now(),top__is_top=True,then=Value(0)),
            When(Q(top__is_top=False)|Q(top__isnull=True),then=Value(1)),
            default=Value(2),
            output_field=IntegerField(),
            ), 
    ).order_by('-toptop','-id')

    print(queryset.query)
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
