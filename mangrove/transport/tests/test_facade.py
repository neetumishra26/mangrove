import unittest
from mock import Mock, patch
from mangrove.datastore.database import DatabaseManager
from mangrove.datastore.entity import Entity
from mangrove.form_model.field import TextField
from mangrove.form_model.form_model import FormModel
from mangrove.transport.facade import ActivityReportWorkFlow, RegistrationWorkFlow
from mangrove.transport.player.tests.test_web_player import DummyLocationTree

class TestActivityWorkFlow(unittest.TestCase):
    def setUp(self):
        self.form_model_mock = Mock(spec=FormModel)
        self.reporter_entity_mock = Mock(spec=Entity)

    def tearDown(self):
        pass

    def test_should_generate_default_code_if_short_code_is_empty_and_entity_is_reporter(self):
        activity_report = ActivityReportWorkFlow(form_model=self.form_model_mock, reporter_entity= self.reporter_entity_mock)
        self.form_model_mock.get_short_code = Mock(return_value=None)
        self.form_model_mock.entity_defaults_to_reporter = Mock(return_value=True)
        self.form_model_mock.entity_question = TextField(name="entity question", code="foo", label="bar", ddtype=Mock())
        self.reporter_entity_mock.short_code = 2
        self.assertEquals({'l':'None', 'foo':2}, activity_report.process({'l':'None'}))

    def test_should_not_generate_code_if_form_model_has_code_and_entity_type_is_reporter(self):
        activity_report = ActivityReportWorkFlow(form_model=self.form_model_mock, reporter_entity= self.reporter_entity_mock)
        self.form_model_mock.get_short_code = Mock(return_value='1')
        self.form_model_mock.entity_defaults_to_reporter = Mock(return_value=True)
        self.form_model_mock.entity_question = TextField(name="entity question", code="foo", label="bar", ddtype=Mock())
        self.assertEquals({'l':'None'}, activity_report.process({'l':'None'}))

    def test_should_not_generate_code_if_form_model_has_code_and_entity_type_is_not_reporter(self):
        activity_report = ActivityReportWorkFlow(form_model=self.form_model_mock, reporter_entity= self.reporter_entity_mock)
        self.form_model_mock.get_short_code = Mock(return_value='1')
        self.form_model_mock.entity_defaults_to_reporter = Mock(return_value=False)
        self.form_model_mock.entity_question = TextField(name="entity question", code="foo", label="bar", ddtype=Mock())
        self.assertEquals({'l':'None'}, activity_report.process({'l':'None'}))

    def test_should_not_generate_code_if_entity_type_is_reporter_and_form_model_dont_have_code(self):
        activity_report = ActivityReportWorkFlow(form_model=self.form_model_mock, reporter_entity= self.reporter_entity_mock)
        self.form_model_mock.get_short_code = Mock(return_value=None)
        self.form_model_mock.entity_defaults_to_reporter = Mock(return_value=False)
        self.form_model_mock.entity_question = TextField(name="entity question", code="foo", label="bar", ddtype=Mock())
        self.assertEquals({'l':'None'}, activity_report.process({'l':'None'}))

class TestRegistrationWorkFlow(unittest.TestCase):

    def setUp(self):
        self.dbm = Mock(spec=DatabaseManager)
        self.form_model_mock = Mock(spec=FormModel)
        self.get_entity_count = patch('mangrove.transport.facade.get_entity_count_for_type', new=dummy_get_entity_count_for_type,spec=True)
        self.get_entity_count.start()

    def tearDown(self):
        self.get_entity_count.stop()

    def test_should_generate_default_code_if_short_code_is_empty(self):
        registration_work_flow = RegistrationWorkFlow(self.dbm, self.form_model_mock, DummyLocationTree(), dummy_get_location_hierarchy)
        self.form_model_mock.get_short_code = Mock(return_value=None)
        self.form_model_mock.entity_type=['clinic']
        self.form_model_mock.entity_question = TextField(name="entity question", code="s", label="bar", ddtype=Mock())
        values = registration_work_flow.process({'t': 'clinic', 'l':'Pune'})
        self.assertEqual({'s': 'cli1', 't': 'clinic', 'g': '-12 60', 'l': [u'arantany']}, values)

    def test_should_set_geocode_if_location_and_short_code_both_are_given(self):
        self.form_model_mock.entity_type=['clinic']
        registration_work_flow = RegistrationWorkFlow(self.dbm, self.form_model_mock, DummyLocationTree(), get_location_hierarchy=dummy_get_location_hierarchy)
        self.assertEquals({'s':'cli1', 'l':['arantany'], 'g': '-12 60'}, registration_work_flow.process({'s':'cli1', 'l':'Pune'}))

    def test_should_set_geocode_if_only_location_is_given(self):
        registration_work_flow = RegistrationWorkFlow(self.dbm, self.form_model_mock, DummyLocationTree(), get_location_hierarchy=dummy_get_location_hierarchy)
        self.form_model_mock.get_short_code = Mock(return_value=None)
        self.form_model_mock.entity_type=['clinic']
        self.form_model_mock.entity_question = TextField(name="entity question", code="s", label="bar", ddtype=Mock())
        values = registration_work_flow.process({'t': 'clinic', 'l':'Pune'})
        self.assertEqual({'s': 'cli1', 't': 'clinic', 'g': '-12 60', 'l': [u'arantany']}, values)

    def test_should_set_location_if_geocode_and_short_code_both_are_given(self):
        registration_work_flow = RegistrationWorkFlow(self.dbm, self.form_model_mock, DummyLocationTree(), get_location_hierarchy=dummy_get_location_hierarchy)
        values = registration_work_flow.process({'s':'cli1', 'l':'None','g':'1 1'})
        self.assertEquals({'s':'cli1', 'l':[u'arantany'],'g':'1 1'}, values)

    def test_should_set_location_if_only_geocode_is_given(self):
        registration_work_flow = RegistrationWorkFlow(self.dbm, self.form_model_mock, DummyLocationTree(), get_location_hierarchy=dummy_get_location_hierarchy)
        self.form_model_mock.get_short_code = Mock(return_value=None)
        self.form_model_mock.entity_type=['clinic']
        self.form_model_mock.entity_question = TextField(name="entity question", code="s", label="bar", ddtype=Mock())
        values = registration_work_flow.process({'t': 'clinic', 'l':'None', 'g':'1 1'})
        self.assertEqual({'s': 'cli1', 't': 'clinic', 'g': '1 1', 'l': [u'arantany']}, values)


def dummy_get_entity_count_for_type(dbm, entity_type):
    return 0

def dummy_get_location_hierarchy(foo):
    return [u'arantany']

class DummyLocationTree(object):
    def get_location_hierarchy_for_geocode(self, lat, long ):
        return ['madagascar']

    def get_centroid(self, location_name, level):
        return 60, -12
