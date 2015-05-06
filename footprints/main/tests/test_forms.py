from django import forms
from django.test.testcases import TestCase
from haystack.query import EmptySearchQuerySet

from footprints.main.forms import FootprintSearchForm
from footprints.main.tests.factories import FootprintFactory


class SearchFormTest(TestCase):

    def test_init(self):
        form = FootprintSearchForm()

        self.assertEquals(type(form.fields['models']),
                          forms.MultipleChoiceField)

        self.assertEquals(form.fields['q'].widget.attrs['class'],
                          'form-control')

        self.assertEquals(form.fields['q'].widget.attrs['placeholder'],
                          'Titles, People, Places')

    def test_search(self):
        footprint1 = FootprintFactory(title='Alpha')
        footprint2 = FootprintFactory(title='Beta')
        footprint3 = FootprintFactory(title='Gamma')

        form = FootprintSearchForm()
        sqs = form.search()
        self.assertEquals(sqs.count(), 0)

        form.is_bound = True
        sqs = form.search()
        # self.assertEquals(sqs.count(), 3)

#     def search(self):
#         if not self.cleaned_data.get('q'):
#             sqs = self.searchqueryset.all()
#         else:
#             sqs = self.searchqueryset.auto_query(self.cleaned_data['q'])
# 
#         sqs = sqs.exclude(django_ct__in=["main.imprint",
#                                          "main.place",
#                                          "main.person"])
# 
#         if self.load_all:
#             sqs = sqs.load_all()
# 
#         sqs = sqs.models(*self.get_models())
#         sqs = sqs.order_by('sort_by')
#         return sqs
