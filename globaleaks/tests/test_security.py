import binascii

import os
import scrypt

import shutil

from Crypto.Hash import SHA512
from twisted.trial import unittest

from globaleaks.tests import helpers
from globaleaks.security import get_salt, hash_password, check_password, change_password, SALT_LENGTH, \
                                directory_traversal_check, GLSecureTemporaryFile, GLSecureFile

from globaleaks.settings import GLSetting
from globaleaks.rest import errors


class TestPasswordManagement(unittest.TestCase):

    def test_pass_hash(self):
        dummy_password = r"focaccina"
        dummy_salt_input = "vecna@focaccina.net"

        sure_bin = scrypt.hash(dummy_password, get_salt(dummy_salt_input) )
        sure = binascii.b2a_hex(sure_bin)
        not_sure = hash_password(dummy_password, dummy_salt_input)
        self.assertEqual(sure, not_sure)

    def test_salt(self):
        dummy_string = "xxxxxx32312xxxxxx"

        sha = SHA512.new()
        sha.update(dummy_string)

        complete_hex = sha.hexdigest()
        self.assertEqual( complete_hex[:SALT_LENGTH],
                          get_salt(dummy_string)[:SALT_LENGTH] )

        new_dummy_string = "xxxxkkkk"

        sha_second = SHA512.new()
        sha_second.update(new_dummy_string)

        complete_hex = sha_second.hexdigest()
        self.assertEqual( complete_hex[:SALT_LENGTH],
                          get_salt(new_dummy_string)[:SALT_LENGTH] )

    def test_valid_password(self):
        dummy_password = dummy_salt_input = \
            "http://blog.transparency.org/wp-content/uploads/2010/05/A2_Whistelblower_poster.jpg"
        dummy_salt = get_salt(dummy_salt_input)

        hashed_once = binascii.b2a_hex(scrypt.hash(dummy_password, dummy_salt))
        hashed_twice = binascii.b2a_hex(scrypt.hash(dummy_password, dummy_salt))
        self.assertTrue(hashed_once, hashed_twice)

        self.assertTrue(check_password(dummy_password, hashed_once, dummy_salt_input))

    def test_change_password(self):
        dummy_salt_input = "xxxxxxxx"
        first_pass = helpers.VALID_PASSWORD1
        second_pass = helpers.VALID_PASSWORD2
        dummy_salt = get_salt(dummy_salt_input)

        # as first we hash a "first_password" like has to be:
        hashed1 = binascii.b2a_hex(scrypt.hash(str(first_pass), dummy_salt))

        # now emulate the change unsing the globaleaks.security module
        hashed2 = change_password(hashed1, first_pass, second_pass, dummy_salt_input)

        # verify that second stored pass is the same
        self.assertEqual(
            hashed2,
            binascii.b2a_hex(scrypt.hash(str(second_pass), dummy_salt) )
        )


class TestFilesystemAccess(unittest.TestCase):

    def test_directory_traversal_check_blocked(self):
        try:
            directory_traversal_check(GLSetting.static_path, "/etc/passwd")
            self.assertTrue(False)
        except errors.DirectoryTraversalError:
            self.assertTrue(True)
        except Exception as excep:
            print "Wrong exception: %s" % excep.log_message
            raise excep


    def test_directory_traversal_check_allowed(self):
        try: 
            valid_access = os.path.join(GLSetting.static_path, "antani.txt")
            directory_traversal_check(GLSetting.static_path, valid_access)
            self.assertTrue(True)
        except Exception as excep:
            print "Exception %s" % excep.log_message
            self.assertTrue(False)

class TestGLSecureFiles(helpers.TestGL):

    def test_temporary_file(self):
        a = GLSecureTemporaryFile('files/submission', 'ramdisk')
        filepath = a.filepath
        keypath = a.keypath
        antani = "0123456789" * 10000
        a.write(antani)
        self.assertTrue(antani == a.read())
        a.close()
        self.assertFalse(os.path.exists(filepath))
        self.assertFalse(os.path.exists(keypath))

    def test_temporary_file_avoid_delete(self):
        a = GLSecureTemporaryFile('files/submission', 'ramdisk')
        a.avoid_delete()
        filepath = a.filepath
        keypath = a.keypath
        antani = "0123456789" * 10000
        a.write(antani)
        a.close()
        self.assertTrue(os.path.exists(filepath))
        self.assertTrue(os.path.exists(keypath))
        b = GLSecureFile(filepath, keypath)
        self.assertTrue(antani == b.read())