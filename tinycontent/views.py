import time
import datetime
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.views.generic import TemplateView
from django.conf import settings


class EnableEditModeView(TemplateView):
    http_method_names = [u'get', u'post', u'options', ]
    template_name = 'tinycontent/tinycontent_confirm.html'
    success_url = getattr(settings, 'TINYCONTENT_EDIT_MODE_SUCCESS', '/')

    @staticmethod
    def edit_mode_perm_check(user):
        if not getattr(settings, 'TINYCONTENT_EDIT_MODE', False):
            return False
        if user.has_perm('tinycontent.add_tinycontent'):
            return True
        if user.has_perm('tinycontent.change_tinycontent'):
            return True
        return False

    def get_end_time(self):
        d = datetime.datetime.now()+datetime.timedelta(seconds=10)
        return time.mktime(d.timetuple())

    def dispatch(self, request, *args, **kwargs):
        if not self.edit_mode_perm_check(request.user):
            return HttpResponseForbidden()
        return super(EnableEditModeView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return self.success_url

    def post(self, request, *args, **kwargs):
        request.session['tinycontent_edit'] = self.get_end_time()
        return HttpResponseRedirect(self.get_success_url())
