from django.contrib.admin.models import LogEntry
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.db.models import Q

from .models import Post,Category,Tag,Top
from .adminforms import PostAdminForm

from typeidea.base_admin import BaseOwnerAdmin
from typeidea.custom_site import custom_site
# Register your models here.

class PostInline(admin.TabularInline):
    fields=('title','desc')
    extra=3
    model=Post

@admin.register(Top,site=custom_site)
class TopAdmin(admin.ModelAdmin):
    list_display=('is_top','topped_expired_time')
    fields=('is_top','topped_expired_time')

   
@admin.register(Category,site=custom_site)
class CategoryAdmin(BaseOwnerAdmin):
    inlines=[PostInline,]
    list_display=('name','owner','status','is_nav','created_time','post_count')
    fields=('name','status','is_nav')
    search_fields = ('name', 'id')

    def post_count(self,obj):
        return obj.post_set.count()
    post_count.short_description='文章数量'

@admin.register(Tag,site=custom_site)
class TagAdmin(BaseOwnerAdmin):
    list_display=('name','status','created_time')
    fields=('name','status')
    search_fields = ('name', 'id')

class TopOwnerFilter(admin.SimpleListFilter):
    ''' 自定义过滤器只展示当前文章置顶'''

    title='置顶过滤器'
    parameter_name='post_top'

    def lookups(self,request,model_admin):
        #return Category.objects.filter(owner=request.user).values_list('id','name')
        #return Post.objects.filter(owner=request.user).values_list('top__id','top__is_top').order_by('top').distinct()

        return [(0, False), (1, True)]

    def queryset(self,request,queryset):
        is_top=self.value()
        if is_top:
            #查询置顶设置为空或置顶外键为Null
            if is_top=='0':
                return queryset.filter(Q(top__is_top=self.value())|Q(top__isnull=True))
            else:
                return queryset.filter(top__is_top=self.value())
        return queryset

class CategoryOwnerFilter(admin.SimpleListFilter):
    ''' 自定义过滤器只展示当前用户分类 '''

    title='分类过滤器'
    parameter_name='owner_category'

    def lookups(self,request,model_admin):
        #return Category.objects.filter(owner=request.user).values_list('id','name')
        return Post.objects.filter(owner=request.user).values_list('category__id','category__name').order_by('category').distinct()

    def queryset(self,request,queryset):
        category_id=self.value()
        if category_id:
            return queryset.filter(category_id=self.value())
        return queryset

class TagOwnerFilter(admin.SimpleListFilter):
    ''' 自定义过滤器只展示当前用户标签'''

    title='标签过滤器'
    parameter_name='owner_tag'

    def lookups(self,request,model_admin):
        return Post.objects.filter(owner=request.user).values_list('tag__id','tag__name').order_by('tag').distinct()

    def queryset(self,request,queryset):
        tag_id=self.value()
        if tag_id:
            return queryset.filter(tag__id=self.value())
        return queryset

@admin.register(Post,site=custom_site)
class PostAdmin(BaseOwnerAdmin):
    form=PostAdminForm
    list_display=[
        'title','category','tags','status',
        'created_time','owner','operator',
        'top',
        #'top__is_top','top__topped_expired_time',
    ]
    list_display_links=[]

    list_filter=[CategoryOwnerFilter,TagOwnerFilter,TopOwnerFilter]
    autocomplete_fields = ['category','tag']
    search_fields=['title','category__name','tag__name']

    actions_on_top=True
    actions_on_bottom=True

    save_on_top=True

    exclude=('owner',)

    #fields=(
    #    ('category','title'),
    #    'desc',
    #    'status',
    #    'content',
    #    'tag',
    #)

    fieldsets = (
        ('基础配置', {
            'description': '基础配置描述',
            'fields': (
                ('title', 'category'),
                'status',
            ),
        }),
        ('内容', {
            'fields': (
            'desc',
            'is_md',
            'content_ck',
            'content_md',
            'content',

            ),
        }),
        ('额外信息', {
            'classes': ('wide',),
            'fields': ('tag', ),
        }),
        ('置顶相关', {
            'fields': ('top', ),
            #'fields': ('top__is_top','top__topped_expired_time', ),
        })
    )

    filter_horizontal = ('tag', )
    #filter_vertical = ('tag', )

    def operator(self,obj):
        return format_html(
            '<a href="{}">编辑</a>',
            reverse('cus_admin:blog_post_change',args=(obj.id,))
        )
    operator.short_description='操作'

    #class Media:
    #    css = {
    #        'all': ("https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css", ),
    #    }
    #    js = ('https://cdn.jsdelivr.net/npm/bootstrap@4.5.0/dist/js/bootstrap.min.js', )

@admin.register(LogEntry, site=custom_site)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ['object_repr', 'object_id', 'action_flag', 'user', 'change_message']

