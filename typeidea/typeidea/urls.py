"""typeidea URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import xadmin
from rest_framework.routers import DefaultRouter
from rest_framework.documentation import include_docs_urls
from django.conf import settings
from django.contrib import admin
from django.urls import path,re_path,include
from django.contrib.sitemaps import views as sitemap_views
from django.conf.urls.static import static

from blog.views import (
    post_list,post_detail,
    IndexView,CategoryView,TagView,
    PostDetailView,SearchView,AuthorView,
)
from config.views import LinkListView
from comment.views import CommentView
from .custom_site import custom_site
from blog.rss import LatestPostFeed
from blog.sitemap import PostSitemap
from .autocomplete import CategoryAutocomplete,TagAutocomplete
from blog.apis import PostViewSet,CategoryViewSet

router=DefaultRouter()
router.register(r'post',PostViewSet,basename='api-post')
router.register(r'category',CategoryViewSet,basename='api-category')

'''
url(r'^', include(router.urls)),
url(r'^api/', include((router.urls, 'app_name'))),
url(r'^api/', include((router.urls, 'app_name'), namespace='instance_name')),
'''

urlpatterns = [
    path('super_admin/', admin.site.urls,name='super-admin'),
    path('admin/', custom_site.urls,name='admin'),
    path('xadmin/', xadmin.site.urls,name='xadmin'),
    path('',IndexView.as_view(),name='index'),
    path('category/<int:category_id>/',CategoryView.as_view(),name='category-list'),
    path('tag/<int:tag_id>/',TagView.as_view(),name='tag-list'),
    path('post/<int:post_id>/',PostDetailView.as_view(),name='post-detail'),
    path('search/',SearchView.as_view(),name='search'),
    path('author/<int:owner_id>/',AuthorView.as_view(),name='author'),
    path('links/',LinkListView.as_view(),name='links'),
    path('comment/',CommentView.as_view(),name='comment'),
    re_path(r'^rss|feed/', LatestPostFeed(), name='rss'),
    re_path(r'^sitemap\.xml$', sitemap_views.sitemap, {'sitemaps': {'posts': PostSitemap}}),
    path('category-autocomplete/', CategoryAutocomplete.as_view(), name='category-autocomplete'),
    path('tag-autocomplete/', TagAutocomplete.as_view(), name='tag-autocomplete'),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    #path('api/post/',post_list,name='post-list'),
    #path('api/post/',PostList.as_view(),name='post-list'),

    #path('api/', include(router.urls,namespace='api')),无效

    path('api/', include((router.urls, 'blog'), namespace='api')),
    #path('api/', include((router.urls, 'blog'))),
    #path('api/', include(router.urls)),

    path('api/docs/',include_docs_urls(title='typeidea apis')),

    ]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
