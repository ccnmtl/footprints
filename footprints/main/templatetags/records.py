from django import template

from footprints.main.models import get_model_fields


register = template.Library()


class GetRecordFieldNode(template.Node):
    def __init__(self, instance, var_name):
        self.instance = instance
        self.var_name = var_name

    def render(self, context):
        instance = context[self.instance]
        fields = []
        for field in get_model_fields(instance):
            fields.append(getattr(instance, field))
        context[self.var_name] = fields
        return ''


@register.tag('get_record_fields')
def get_record_fields(parser, token):
    instance = token.split_contents()[1:][0]
    var_name = token.split_contents()[1:][2]
    return GetRecordFieldNode(instance, var_name)
