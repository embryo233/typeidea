from admin_tools.dashboard.modules import RecentActions

from django.contrib.admin.models import LogEntry

from django.contrib.admin.utils import quote

from django.urls import NoReverseMatch, reverse

from types import MethodType

def get_admin_url(self):
    """
    Returns the admin URL to edit the object represented by this log entry.
    """
    if self.content_type and self.object_id:
        url_name = 'admin:%s_%s_change' % (self.content_type.app_label, self.content_type.model)
        try:
            return reverse(url_name, args=(quote(self.object_id),),current_app=self.current_app)
        except NoReverseMatch:
            pass
    return None

class MyRecentActions(RecentActions):
    def __init__(self, title=None, limit=10, include_list=None,
                 exclude_list=None, **kwargs):
        #直接类名调用
        #RecentActions.__init__(self, title, limit, include_list,
        #         exclude_list, **kwargs)

        #Python2.x写法super(Class, self).xxx
        #super(RecentActions,self).__init__(title, limit, include_list,
        #         exclude_list, **kwargs)

        #Python3.x写法super().xxx
        super().__init__(title, limit, include_list,
                 exclude_list, **kwargs)


    def init_with_context(self, context):

        if self._initialized:
            return
        from django.db.models import Q
        from django.contrib.admin.models import LogEntry

        #request = context['request']
        request=context.get('request')
        current_app=request.current_app

        #RecentActions.init_with_context(self, context)
        def get_qset(list):
            # Import this here to silence RemovedInDjango19Warning. See #15
            from django.contrib.contenttypes.models import ContentType

            qset = None
            for contenttype in list:
                if isinstance(contenttype, ContentType):
                    current_qset = Q(content_type__id=contenttype.id)
                else:
                    try:
                        app_label, model = contenttype.split('.')
                    except:
                        raise ValueError(
                            'Invalid contenttype: "%s"' % contenttype
                        )
                    current_qset = Q(
                        content_type__app_label=app_label,
                        content_type__model=model
                    )
                if qset is None:
                    qset = current_qset
                else:
                    qset = qset | current_qset
            return qset

        if request.user is None:
            qs = LogEntry.objects.all()
        else:
            qs = LogEntry.objects.filter(user__pk__exact=request.user.pk)

        if self.include_list:
            qs = qs.filter(get_qset(self.include_list))
        if self.exclude_list:
            qs = qs.exclude(get_qset(self.exclude_list))

        self.children = qs.select_related('content_type', 'user')[:self.limit]
        for c in self.children:
            c.current_app=current_app
            c.get_admin_url=MethodType(get_admin_url,c)

        if not len(self.children):
            self.pre_content = _('No recent actions.')
        self._initialized = True


