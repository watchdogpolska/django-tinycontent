from django import template
from django.template.loader import render_to_string
from django.template.base import TemplateSyntaxError
from django.utils.encoding import force_text
from django.conf import settings
from tinycontent.models import TinyContent
from datetime import datetime
register = template.Library()


def check_edit_mode(request):
    if not getattr(settings, 'TINYCONTENT_EDIT_MODE', False):
        return True
    z = request.session.get('tinycontent_edit', -1)
    if datetime.now() < datetime.fromtimestamp(z):
        return True
    return False


class TinyContentNode(template.Node):
    def __init__(self, args, nodelist):
        self.args = args
        self.nodelist = nodelist

    def get_name(self, context):
        return ':'.join(x.resolve(context) for x in self.args)

    def render(self, context):
        context.update({'tinycontent_edit': check_edit_mode(context['request'])})
        try:
            name = self.get_name(context)
            obj = TinyContent.get_content_by_name(name)
            return render_to_string('tinycontent/tinycontent.html',
                                    {'obj': obj},
                                    context)
        except TinyContent.DoesNotExist:
            rval = self.nodelist.render(context)
            rval += render_to_string('tinycontent/tinycontent_add.html',
                                     {'name': name},
                                     context)
            return rval


@register.tag
def tinycontent(parser, token):
    parts = token.split_contents()[1:]

    if not parts:
        raise TemplateSyntaxError("'tinycontent' tag takes arguments.")

    args = [parser.compile_filter(x) for x in parts]
    nodelist = parser.parse(('endtinycontent',))
    parser.delete_first_token()
    return TinyContentNode(args, nodelist)


@register.simple_tag(takes_context=True)
def tinycontent_simple(context, *args):
    context.update({'tinycontent_edit': check_edit_mode(context['request'])})
    if not args:
        raise TemplateSyntaxError("'tinycontent' tag takes arguments.")

    content_name = u':'.join(map(force_text, args))
    try:
        obj = TinyContent.get_content_by_name(content_name)
        return render_to_string('tinycontent/tinycontent.html',
                                {'obj': obj},
                                context)
    except TinyContent.DoesNotExist:
        return render_to_string('tinycontent/tinycontent_add.html',
                                {'name': content_name},
                                context)
