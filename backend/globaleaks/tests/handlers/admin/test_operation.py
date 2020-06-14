# -*- coding: utf-8
from globaleaks import models
from globaleaks.handlers.admin import user
from globaleaks.handlers.admin.operation import AdminOperationHandler
from globaleaks.orm import tw
from globaleaks.jobs import delivery
from globaleaks.rest import errors
from globaleaks.state import State
from globaleaks.tests import helpers

from twisted.internet import defer, reactor



class TestHostnameConfig(helpers.TestHandler):
    _handler = AdminOperationHandler

    @defer.inlineCallbacks
    def test_put(self):
        State.tenant_cache[1].anonymize_outgoing_connections = False

        # Add a file to the tmp dir
        with open('./robots.txt', 'w') as f:
            f.write("User-agent: *\n" +
                    "Allow: /\n" +
                    "Sitemap: http://localhost/sitemap.xml")

        # Start the HTTP server proxy requests will be forwarded to.
        self.pp = helpers.SimpleServerPP()

        # An extended SimpleHTTPServer to handle the addition of the globaleaks header
        e = "" + \
        "from SimpleHTTPServer import SimpleHTTPRequestHandler as rH; " + \
        "from SimpleHTTPServer import test as t; " + \
        "of = rH.end_headers; rH.end_headers = lambda s: s.send_header('Server', 'GlobaLeaks') or of(s); " + \
        "t(HandlerClass=rH)"

        yield reactor.spawnProcess(self.pp, 'python', args=['python', '-c', e, '43434'], usePTY=True)

        yield self.pp.start_defer

        for value in ['onion', 'localhost', 'antani.onion', 'antani.localhost']:
            handler = self.request({'operation': 'set_hostname', 'args': {'value': value}}, role='admin')
            yield self.assertFailure(handler.put(), errors.InputValidationError)

        handler = self.request({'operation': 'set_hostname', 'args': {'value': 'antani.gov'}}, role='admin')
        yield handler.put()

    @defer.inlineCallbacks
    def tearDown(self):
        if hasattr(self, 'pp'):
            self.pp.transport.loseConnection()
            self.pp.transport.signalProcess('KILL')

        yield super(TestHostnameConfig, self).tearDown()


class TestAdminPasswordReset(helpers.TestHandlerWithPopulatedDB):
    _handler = AdminOperationHandler

    @defer.inlineCallbacks
    def setUp(self):
        yield helpers.TestHandlerWithPopulatedDB.setUp(self)

        for r in (yield tw(user.db_get_users, 1, 'receiver', 'en')):
            if r['pgp_key_fingerprint'] == 'BFB3C82D1B5F6A94BDAC55C6E70460ABF9A4C8C1':
                self.user = r
                return

    @defer.inlineCallbacks
    def test_put(self):
        data_request = {
            'operation': 'reset_user_password',
            'args': {
                'value': self.user['id']
            }
        }

        handler = self.request(data_request, role='admin')

        yield handler.put()


class TestAdminResetSubmissions(helpers.TestHandlerWithPopulatedDB):
    _handler = AdminOperationHandler

    @defer.inlineCallbacks
    def setUp(self):
        yield helpers.TestHandlerWithPopulatedDB.setUp(self)
        yield self.perform_full_submission_actions()
        yield delivery.Delivery().run()

        for r in (yield tw(user.db_get_users, 1, 'receiver', 'en')):
            if r['pgp_key_fingerprint'] == 'BFB3C82D1B5F6A94BDAC55C6E70460ABF9A4C8C1':
                self.user = r
                return

    @defer.inlineCallbacks
    def test_put(self):
        yield self.test_model_count(models.InternalTip, 2)
        yield self.test_model_count(models.ReceiverTip, 4)
        yield self.test_model_count(models.InternalFile, 4)
        yield self.test_model_count(models.ReceiverFile, 8)
        yield self.test_model_count(models.Comment, 6)
        yield self.test_model_count(models.Message, 8)
        yield self.test_model_count(models.Mail, 2)
        yield self.test_model_count(models.SecureFileDelete, 0)

        data_request = {
            'operation': 'reset_submissions',
            'args': {}
        }

        handler = self.request(data_request, role='admin')

        yield handler.put()

        yield self.test_model_count(models.InternalTip, 0)
        yield self.test_model_count(models.ReceiverTip, 0)
        yield self.test_model_count(models.InternalFile, 0)
        yield self.test_model_count(models.ReceiverFile, 0)
        yield self.test_model_count(models.Comment, 0)
        yield self.test_model_count(models.Message, 0)
        yield self.test_model_count(models.Mail, 2)
        yield self.test_model_count(models.SecureFileDelete, 8)


class TestAdminOperations(helpers.TestHandlerWithPopulatedDB):
    _handler = AdminOperationHandler

    def _test_operation_handler(self, operation):
        data_request = {
            'operation': operation,
            'args': {}
        }

        handler = self.request(data_request, role='admin')

        return handler.put()


    def test_admin_test_mail(self):
        return self._test_operation_handler('test_mail')

    def test_admin_test_smtp_settings(self):
        return self._test_operation_handler('reset_smtp_settings')

    def test_admin_test_reset_templates(self):
        return self._test_operation_handler('reset_templates')
