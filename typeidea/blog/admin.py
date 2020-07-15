from django.contrib.admin.models import LogEntry
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Post,Category,Tag
from .adminforms import PostAdminForm

from typeidea.base_admin import BaseOwnerAdmin
from typeidea.custom_site import custom_site
# Register your models here.

class PostInline(admin.TabularInline):
    fields=('title','desc')
    extra=3
    model=Post

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
    ''' 自定义过滤器只展示当前用户分类 '''

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
        'created_time','owner','operator'
    ]
    list_display_links=[]

    list_filter=[CategoryOwnerFilter,TagOwnerFilter]
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

