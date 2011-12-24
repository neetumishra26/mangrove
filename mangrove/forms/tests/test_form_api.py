import unittest
from mangrove.forms.fields import TextField
from mangrove.forms import forms

class TestFormAPI(unittest.TestCase):

    def test_create_new_form(self):
        class FooForm(forms.Form):
            code = "bar"
            name = TextField("foo", "f", "What is foo?")

        form = FooForm()
        self.assertEqual(1, len(form.fields))


    def test_create_new_form_from_dct(self):
        dct = {
            'code': "reg",
            'fields': [{
                '_class': "TextField",
                'name': "name",
                "code": "na",
                "label": "What is the name?",
                "default":"",
            }]
        }
        form = forms.Form.build_from_dct(dct)
        self.assertEqual(1, len(form.fields))
        self.assertEqual("reg", form.code)

    def test_get_hold_of_field_from_form(self):
        dct = {
            'code': "reg",
            'fields': [{
                '_class': "TextField",
                'name': "name",
                "code": "na",
                "label": "What is the name?",
                "default":"",
            }]
        }
        form = forms.Form.build_from_dct(dct)
        self.assertEqual("na", form['name'].code)
