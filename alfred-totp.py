#!/usr/bin/env/ python
# coding=utf-8
'''
-----
Alfred 2-Factor Authenticator Workflow
Generate two-factor authentication tokens using Alfred.
-----
To-Do:
# Implement Queries : add a new keychain, services and delete.
# Fuzzy Filter Queries
# 
'''
import sys
import hmac
import base64
import hashlib
import time
import re
import os
import argparse
from subprocess import check_output as run
from workflow import Workflow3 as Workflow, ICON_INFO, ICON_ERROR, ICON_WARNING, ICON_COLOR
from workflow.util import set_config
log = None

def main(wf):
    """
    The Workflow3 instance will be passed to the function
    you call from `Workflow3.run`.
    Not super useful, as the `wf` object created in
    the `if __name__ ...` clause below is global...

    Your imports go here if you want to catch import errors, which
    is not a bad idea, or if the modules/packages are in a directory
    added via `Workflow3(libraries=...)`
    """

    # Get args from Workflow3, already in normalized Unicode.
    # This is also necessary for "magic" arguments to work.

    def get_steamguard_code(secret):
        """
        Generate Steamguard code from secret
        """
        steam_decode_chars = ['2', '3', '4', '5', '6', '7', '8', '9',
                              'B', 'C', 'D', 'F', 'G', 'H', 'J', 'K',
                              'M', 'N', 'P', 'Q', 'R', 'T', 'V', 'W',
                              'X', 'Y']
        # py3 ready
        """
        byte_time = bytes.fromhex(('%016x' % int(time.time() // 30)))
        auth = hmac.new(base64.b64decode(secret), byte_time, hashlib.sha1)
        digest = auth.digest()
        start = digest[19] & 0xF
        code = digest[start:start + 4]
        auth_code_raw = int(codecs.encode(code, 'hex'), 16) & 0x7FFFFFFF

        auth_code = []
        for _ in range(5):
            auth_code.append(steam_decode_chars[int(auth_code_raw % len(steam_decode_chars))])
            auth_code_raw /= len(steam_decode_chars)

        return ''.join(auth_code)
        """
        # py2
        auth_code = []
        hex_time = ('%016x' % (time.time() // 30))
        byte_time = hex_time.decode('hex')

        digest = hmac.new(base64.b64decode(secret), byte_time, hashlib.sha1).digest()
        begin = ord(digest[19:20]) & 0xF
        auth_code_raw = int((digest[begin:begin + 4]).encode('hex'), 16) & 0x7fffffff

        for _ in range(5):
            auth_code.append(steam_decode_chars[auth_code_raw % len(steam_decode_chars)])
            auth_code_raw /= len(steam_decode_chars)

        return ''.join(auth_code)

    def workflow_keychain_setup(query, otp_query):
        try:
            # no keychain setup, prompt user for setup
            # this method needs work
            if not query:
                wf.add_item(
                    title="2FA Keychain has'nt been setup yet!",
                    subtitle="Hit Enter/Tab to continue...",
                    autocomplete="setup ",
                    icon=ICON_WARNING,
                    valid=False,
                    )
            if str(query[0]) == "setup" and len(query) <= 3:
                # setup mode
                wf.add_item(
                    title="Enter keychain name (without .keychain) and password",
                    subtitle="Example: alfred-totp $ecur3P@ssw0rd (press enter)",
                    icon=ICON_INFO,
                    uid="keyNamePass",
                    autocomplete="{} done".format(otp_query),
                    valid=False,
                    )
            if str(args.query[0]) == "setup" and str(query[3]) == "done":
                wf.add_item(
                    title="Keychain has been configured!",
                    subtitle="Now trigger the workflow again",
                    uid="keyNamePass",
                    icon=ICON_COLOR,
                    valid=True,
                    )
                # set env variables
                set_config('keychain_name', query[1])
                set_config('keychain_pass', query[2])
        except:
            pass

    # ---------------------------------------------------
    # Workflow Begins
    # ---------------------------------------------------
    # READ keychain pass and parse escaping characters
    keychain_name = "{}.keychain".format(os.getenv('keychain_name'))
    keychain_pass = re.escape(os.getenv('keychain_pass'))

    # Arguments from alfred
    _reserved_words = ['add', 'update', 'remove', 'setup']
    parser = argparse.ArgumentParser()
    parser.add_argument('query', nargs='*', default=None)
    args = parser.parse_args(wf.args)
    otp_query = ' '.join(args.query)

    # Workflow Variables
    otp_key = ""

    if not (os.getenv('keychain_name') and os.getenv('keychain_pass')):
        workflow_keychain_setup(args.query, otp_query)
    else:
        # Unlock Keychain
        # py3 ready
        # run(["security unlock-keychain -w {} -p {}".format(keychain_pass, keychain_name), shell=True)
        # py2
        # implement: call setup again if keychain fails to open
        run("security unlock-keychain -p {} {}".format(keychain_pass, keychain_name), shell=True)
        log.debug("keychain: unlocked")

        # Dump TOTP Services
        # py3 ready
        # totp_services = sorted(filter(None, run(["security dump-keychain {} | grep 0x00000007 | awk -F= \'{{print $2}}\'".format(keychain_name)], stdout=PIPE, shell=True).stdout.decode('utf-8').replace("\"", "").split("\n")), key=str.lower)
        # py2
        # note: grabbing "Service" attribute from keychain dump since 0x00000007 does not reflect changes made to keychain
        temp_dict = sorted(filter(None, run("security dump-keychain {} | grep -e svce -e icmt | awk -F= \'{{print $2}}\'| paste -d \":\" - -".format(keychain_name), shell=True).replace("\"", "").split("\n")))
        # reverse the order of mapped dictionary comment:service -> service:comment
        services_dict = dict((y, x) for x, y in dict(map(lambda s: s.split(':'), temp_dict)).iteritems())

        # Generate OTPs for all services
        for service in services_dict:
            # get key's secret from keychain
            if not services_dict[service].startswith("steam"):
                # Standard TOTP Services
                otp_key = ''.join((filter(None, run("/usr/local/bin/oathtool --totp -b \"{}\"".format(
                    ''.join((filter(None, run("security find-generic-password -s {} -w {}".format(service, keychain_name), shell=True).split("\n"))))
                    ), shell=True).split("\n"))))
            else:
                # Non-Standard TOTP Services (╯°□°)╯︵ ┻━┻ STEAM
                otp_key = get_steamguard_code(
                    ''.join((filter(None, run("security find-generic-password -s {} -w {}".format(service, keychain_name), shell=True).split("\n"))))
                    )
            # add service-type, otp_key to the service dictionary
            services_dict[service] = [services_dict[service], otp_key]

        # Lock Keychain when we're done!
        run("security lock-keychain {}".format(keychain_name), shell=True)
        log.debug("keychain: locked")

    # If `query` is `None` or an empty string, all items are returned
    try:
        if not args.query:
            # else display all the services
            for service in services_dict.keys():
                if services_dict[service][0] != "<NULL>" and os.path.isfile("./icons/{}.png".format(services_dict[service][0])):
                    wf.add_item(
                        '{}'.format(service),
                        services_dict[service][1],
                        valid=True, arg=otp_key,
                        icon="./icons/{}.png".format(services_dict[service][0])
                    )
                else:
                    wf.add_item(
                        '{}'.format(service),
                        services_dict[service][1],
                        valid=True, arg=otp_key
                    )
        else:
            items = wf.filter(str(args.query[0]), services_dict.keys())
            for service in items:
                # implement: missing service icon
                wf.add_item(
                    '{}'.format(service),
                    services_dict[service][1],
                    valid=True, arg=services_dict[service][1],
                    icon="./icons/{}.png".format(services_dict[service][0])
                )
    except:
        pass

    wf.send_feedback()


if __name__ == '__main__':
    # Create a global `Workflow` object
    workflow3 = Workflow(
        libraries=['./lib'], update_settings={
            'github_slug': 'iganeshk/alfred-totp',
            'frequency': 1, # every day
        },
        help_url='https://github.com/iganeshk/alfred-totp'
    )
    log = workflow3.logger
    # workflow3.magic_prefix = 'otp:'

    # Call your entry function via `Workflow.run()` to enable its helper
    # functions, like exception catching, ARGV normalization, magic
    # arguments etc.
    sys.exit(workflow3.run(main))
