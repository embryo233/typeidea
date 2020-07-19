from django.contrib.admin.models import LogEntry

from django.contrib.admin.utils import quote

from django.urls import NoReverseMatch, reverse
class MyLogEntry(LogEntry):

    #current_app=None
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
