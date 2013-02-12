import time, os

from twisted.python import log

from globaleaks.transactors.base import MacroOperation
from globaleaks.models.externaltip import File, ReceiverTip
from globaleaks.models.internaltip import InternalTip
from globaleaks.models.submission import Submission
from globaleaks.rest.errors import SubmissionConcluded
from globaleaks import settings
from globaleaks.settings import transact
from twisted.internet import fdesc


class FileOperations(MacroOperation):
    """
    README.md describe pattern and reasons
    """

    @transact
    def get_files(self, submission_gus):

        file_iface = File(self.store)

        filelist = file_iface.get_all_by_submission(submission_gus)

        self.returnData(filelist)
        self.returnCode(200)
        return self.prepareRetVals()


    def dump_single_file(self, client_file_desc, access_gus, context_gus):

        # compose file request as the dict expected in File._import_dict
        file_request = { 'filename' : client_file_desc.get('filename'),
                         'content_type' : client_file_desc.get('content_type'),
                         'file_size' : len(client_file_desc['body']),
                         'submission_gus' : access_gus,
                         'context_gus' : context_gus,
                         'description' : ''
        }

        file_iface = File(self.store)
        file_desc = file_iface.new(file_request)

        print "Created file from %s with file_gus %s" % (file_request['filename'], file_desc['file_gus'])

        # result = self._dump_file(client_file_desc, access_gus, file_desc['file_gus'])
        # def _dump_file(self, file, submission_gus, file_gus):

        if not os.path.isdir(settings.config.advanced.submissions_dir):
            log.msg("%s does not exist. Creating it." %
                    settings.config.advanced.submissions_dir)
            os.mkdir(settings.config.advanced.submissions_dir)

        the_submission_dir = settings.config.advanced.submissions_dir

        # this happen only at the first execution
        if not os.path.isdir(the_submission_dir):
            os.mkdir(the_submission_dir)

        filelocation = os.path.join(the_submission_dir, file_desc['file_gus'])

        print "Saving file \"%s\" of %d byte [%s] type, to %s" %\
              (file_desc['name'], file_desc['size'], file_desc['content_type'], filelocation )

        # *The file is complete*
        # because Cyclone cache them before pass to the handler.
        # This mean that need to be limited client and Cyclone side,
        # and we here can't track about incomplete file.
        with open(filelocation, 'w+') as fd:
            fdesc.setNonBlocking(fd.fileno())
            fdesc.writeToFD(fd.fileno(), client_file_desc['body'])

        return file_desc

    @transact
    def new_files(self, access_gus, request, is_tip):
        if is_tip:
            itip_desc = ReceiverTip(self.store).get_single(access_gus)
            context_gus = itip_desc['context_gus']
        else:
            submission_desc = Submission(self.store).get_single(access_gus)
            if submission_desc['finalize']:
                raise SubmissionConcluded
            context_gus = submission_desc['context_gus']

        result_list = []

        file_array, files = request.files.popitem()

        for single_file in files:

            start_time = time.time()

            result = self.dump_single_file(single_file, access_gus, context_gus)
            result['elapsed_time'] = time.time() - start_time
            result_list.append(result)

        self.returnData(result_list)
        self.returnCode(200)
        return self.prepareRetVals()


    @transact
    def download_file(self, file_gus):
        fileDict = File(self.store).get_content(file_gus)

        self.returnData(fileDict)
        self.returnCode(200)
        return self.prepareRetVals()

