import xadmin
from xadmin.layout import Row,Fieldset
from xadmin.filters import (
    manager,ListFieldFilter,
    RelatedFieldListFilter,MultiSelectFieldListFilter
)
from xadmin.layout import Row, Fieldset, Container

from django.contrib.admin.models import LogEntry
#from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.conf import settings

from .models import Post,Category,Tag
from .adminxforms import PostAdminForm
from typeidea.base_adminx import BaseOwnerAdmin
#from typeidea.custom_site import custom_site

# Register your models here.

class PostInline():
    form_layout=(
        Container(
            Row('title','desc')
        )
    )
    extra=1
    model=Post

@xadmin.sites.register(Category)
class CategoryAdmin(BaseOwnerAdmin):
    #inlines=[PostInline,]
    list_display=('name','owner','status','is_nav','created_time','post_count')
    fields=('name','status','is_nav')
    search_fields=['name','post__title']
    relfield_style = 'fk-ajax'


    def post_count(self,obj):
        return obj.post_set.count()
    post_count.short_description='文章数量'

@xadmin.sites.register(Tag)
class TagAdmin(BaseOwnerAdmin):
    list_display=('name','status','created_time')
    fields=('name','status')
    search_fields=['name','post__title']
    #relfield_style = 'fk-ajax'

#加上自定义过滤器后反而不是搜索框
#class CategoryOwnerFilter(RelatedFieldListFilter):
#
#    @classmethod
#    def test(cls, field, request, params, model, admin_view, field_path):
#        return field.name == 'category'
#
#    def __init__(self, field, request, params, model, model_admin, field_path):
#        super().__init__(field, request, params, model, model_admin, field_path)
#        # 重新获取lookup_choices，根据owner过滤
#        self.lookup_choices = Category.objects.filter(owner=request.user).values_list('id', 'name')

#manager.register(CategoryOwnerFilter, take_priority=True)

class TagOwnerFilter(MultiSelectFieldListFilter):

    @classmethod
    def test(cls, field, request, params, model, admin_view, field_path):
        return field.name == 'tag'
        #return True

    def __init__(self, field, request, params, model, model_admin, field_path,field_order_by=None,field_limit=None,sort_key=None,cache_config=None):
        super().__init__(field, request, params, model, model_admin, field_path,field_order_by,field_limit,sort_key,cache_config)
        queryset = self.admin_view.queryset().exclude(**{"%s__isnull" % field_path: True}).values_list(field_path, flat=True).order_by(field_path).distinct()
        for it in queryset:
            print(it)
        self.lookup_choices = [str(it) for it in queryset.values_list('tag__name', flat=True) if str(it).strip() != ""]




manager.register(TagOwnerFilter, take_priority=True)

@xadmin.sites.register(Post)
class PostAdmin(BaseOwnerAdmin):
    form=PostAdminForm
    list_display=[
        'title','category','tag','status',
        'created_time','owner','operator','is_top',
    ]
    
    list_display_links=[]

    #list_filter=[CategoryOwnerFilter]

    list_filter=[
       'category',
       'tag',
       #('category', MultiSelectFieldListFilter),
       #('tag', MultiSelectFieldListFilter),
    ]
    search_fields=[
        'title',
        'category__name',
        'tag__name'
    ]

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

    form_layout = (
        Fieldset(
            '基础信息',
            Row("title", "category"),
            'status',
            'tag','is_top',
        ),
        Fieldset(
            '内容信息',
            'desc',
            'is_md',
            'content_ck',
            'content_md',
            'content',
        )
    )


    #filter_horizontal = ('tag', )
    #filter_vertical = ('tag', )
    #style_fields = {'tag': 'm2m_transfer'}

    def operator(self,obj):
        return format_html(
            '<a href="{}">编辑</a>',
            #reverse('cus_admin:blog_post_change',args=(obj.id,))
            reverse('xadmin:blog_post_change',args=(obj.id,))
        )
    operator.short_description='操作'

    #class Media:
    #    css = {
    #        'all': ("https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css", ),
    #    }
    #    js = ('https://cdn.jsdelivr.net/npm/bootstrap@4.5.0/dist/js/bootstrap.min.js', )

    #@property
    #def media(self):
    #    media=super().media
    #    media.add_js(['https://cdn.jsdelivr.net/npm/bootstrap@4.5.0/dist/js/bootstrap.min.js'])
    #    media.add_css({'all': ("https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css",),
    #    })
    #    return media

    #自定义CSS JS 放在/xadmin/static/xadmin/对应的目录下 并且以xadmin.开头
    #def get_media(self):
    #    media = super().get_media()
    #    #media += self.vendor('xadmin.select2.min.js')
    #    return media
