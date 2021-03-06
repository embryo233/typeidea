from mistune import markdown

from django.utils.functional import cached_property
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import models
from django.db.models import Avg,Max,Min,Count,Sum  #   引入函数

from django.conf import settings
from django.core.cache import cache
from django.db.models.signals import pre_save,post_save
from django.dispatch import receiver,Signal

post_markdown=Signal(providing_args=['content','content_html'])

class Category(models.Model):
    STATUS_NORMAL = 1
    STATUS_DELETE = 0
    STATUS_ITEMS = (
        (STATUS_NORMAL, '正常'),
        (STATUS_DELETE, '删除'),
    )

    name = models.CharField(max_length=50, verbose_name="名称")
    status = models.PositiveIntegerField(default=STATUS_NORMAL, choices=STATUS_ITEMS, verbose_name="状态")
    is_nav = models.BooleanField(default=False, verbose_name="是否为导航")
    owner = models.ForeignKey(User, verbose_name="作者", on_delete=models.DO_NOTHING)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = verbose_name_plural = '分类'

    def __str__(self):
        return self.name

    @classmethod
    def get_navs(cls):
        categories=cls.objects.filter(status=cls.STATUS_NORMAL)
        #categories=Category.objects.filter(status=cls.STATUS_NORMAL).annotate(c=Count('post__title'))

        #nav_categories=[]
        #normal_categories=[]
        nav_categories=categories.filter(is_nav=True)
        normal_categories=categories.filter(is_nav=False).annotate(c=Count('post__id'))[:100]

        #for cate in categories:
        #    if cate.is_nav:
        #        nav_categories.append(cate)
        #    else:
        #        normal_categories.append(cate)
        #        if len(normal_categories)>=100:
        #            break
        return {
            'navs':nav_categories,
            'categories':normal_categories,
        }


class Tag(models.Model):
    STATUS_NORMAL = 1
    STATUS_DELETE = 0
    STATUS_ITEMS = (
        (STATUS_NORMAL, '正常'),
        (STATUS_DELETE, '删除'),
    )

    name = models.CharField(max_length=10, verbose_name="名称")
    status = models.PositiveIntegerField(default=STATUS_NORMAL, choices=STATUS_ITEMS, verbose_name="状态")
    owner = models.ForeignKey(User, verbose_name="作者", on_delete=models.DO_NOTHING)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = verbose_name_plural = '标签'
        ordering = ['-id']

    def __str__(self):
        return self.name

class ToppedPosts(models.Model):
    title=models.CharField(max_length=255,verbose_name="标题")
    post_id=models.PositiveIntegerField(unique=True,verbose_name="关联文章ID")

    class Meta:
        verbose_name = verbose_name_plural = "置顶文章"

class Post(models.Model):
    STATUS_NORMAL = 1
    STATUS_DELETE = 0
    STATUS_DRAFT = 2
    STATUS_ITEMS = (
        (STATUS_NORMAL, '正常'),
        (STATUS_DELETE, '删除'),
        (STATUS_DRAFT, '草稿'),
    )

    title = models.CharField(max_length=255, verbose_name="标题")
    desc = models.CharField(max_length=1024, blank=True, verbose_name="摘要")
    content = models.TextField(verbose_name="正文", help_text="正文必须为MarkDown格式")
    content_html = models.TextField(verbose_name="正文html代码", blank=True, editable=False)
    status = models.PositiveIntegerField(default=STATUS_NORMAL, choices=STATUS_ITEMS, verbose_name="状态")
    is_md = models.BooleanField(default=False, verbose_name="markdown语法")
    category = models.ForeignKey(Category, verbose_name="分类", on_delete=models.DO_NOTHING)
    tag = models.ManyToManyField(Tag, verbose_name="标签")
    owner = models.ForeignKey(User, verbose_name="作者", on_delete=models.DO_NOTHING)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    is_top=models.BooleanField(default=False,verbose_name="置顶")

    pv = models.PositiveIntegerField(default=1)
    uv = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = verbose_name_plural = "文章"
        ordering = ['-id']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.content_html = markdown(self.content)
        if self.is_md:
            self.content_html = markdown(self.content)
        else:
            self.content_html = self.content

        post_markdown.send(sender=self.__class__,content=self.content,content_html=self.content_html)

        super().save(*args, **kwargs)

    @staticmethod
    def get_by_tag(tag_id):
        try:
            tag = Tag.objects.get(id=tag_id)
        except Tag.DoesNotExist:
            tag = None
            post_list = []
        else:
            post_list = tag.post_set.filter(status=Post.STATUS_NORMAL)\
                .select_related('owner', 'category')
        return post_list, tag

    @staticmethod
    def get_by_category(category_id):
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            category = None
            post_list = []
        else:
            post_list = category.post_set.filter(status=Post.STATUS_NORMAL)\
                .select_related('owner', 'category')
        return post_list, category

    @classmethod
    def latest_posts(cls,with_related=True):
        queryset=cls.objects.filter(status=cls.STATUS_NORMAL)
        if with_related:
            queryset=queryset.select_related('owner','category').prefetch_related('tag')
        return queryset

    @classmethod
    def hot_posts(cls):
        result = cache.get('hot_posts')
        if not result:
            result = cls.objects.filter(status=cls.STATUS_NORMAL).order_by('-pv').only('id','title')
            cache.set('hot_posts', result, 10 * 60)
        return result

    @classmethod
    def get_topped_posts(cls):
        return cls.objects.filter(status=cls.STATUS_NORMAL,is_top=True)

    @cached_property
    def tags(self):
        return ','.join(self.tag.values_list('name',flat=True))
    tags.short_description='标签'

@receiver(pre_save,sender=Post)
def delete_detail_cache(sender,instance=None,**kwargs):
    key=settings.DETAIL_CACHE_KEY.format(str(instance.id))
    cache.delete(key)
    print('delete',key)

@receiver(post_save,sender=Post)
def reset_detail_cache(sender,instance=None,**kwargs):
    key=settings.DETAIL_CACHE_KEY.format(str(instance.id))
    cache.set(key,instance,settings.FIVE_MINUTE)
    if instance.is_top:
        try:
            topped_post=ToppedPosts.objects.get(post_id=instance.id)
        except ToppedPosts.DoesNotExist:
            topped_post=ToppedPosts(title=instance.title,post_id=instance.id)
            topped_post.save()
    else:
        try:
            topped_post=ToppedPosts.objects.get(post_id=instance.id)
            topped_post.delete()
        except ToppedPosts.DoesNotExist:
            print('不存在')
    print('reset',key)

@receiver(post_markdown,sender=Post)
def post_markdown_callback(sender,instance=None,**kwargs):
    print('after markdown')
