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
from subprocess import check_output as run
from workflow import Workflow3 as Workflow, ICON_INFO
from workflow.util import set_config


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
        # py3
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

    # READ keychain pass and parse escaping characters
    keychain_name = "{}.keychain".format(os.getenv('keychain_name'))
    keychain_pass = re.escape((os.getenv('keychain_pass')))

    # args from alfred
    query = ""
    secret = ""
    otp_key = ""
    if len(wf.args) >= 1:
        try:
            query = int(wf.args[0].strip())
        except ValueError:
            pass


    # set env variables
    # set_config('keychain_name', $query)

    # Unlock Keychain (to be closed in time interval of 1 min)
    # py3
    # run(["security unlock-keychain -w {} -p {}".format(keychain_pass, keychain_name), shell=True)
    # py2
    run("security unlock-keychain -p {} {}".format(keychain_pass, keychain_name), shell=True)

    # Dump TOTP Services
    # py3
    #totp_services = sorted(filter(None, run(["security dump-keychain {} | grep 0x00000007 | awk -F= \'{{print $2}}\'".format(keychain_name)], stdout=PIPE, shell=True).stdout.decode('utf-8').replace("\"", "").split("\n")), key=str.lower)
    # py2
    totp_services = sorted(filter(None, run("security dump-keychain {} | grep 0x00000007 | awk -F= \'{{print $2}}\'".format(keychain_name), shell=True).replace("\"", "").split("\n")), key=str.lower)

    # Get Steam Secret if present
    # py3
    # steam_secret = list(filter(None, run(["security find-generic-password -j {} {} | grep icmt | awk -F= \'{{print $2}}\'".format("steamguard", keychain_name)], stdout=PIPE, shell=True).stdout.decode('utf-8').replace("\"", "").split("\n")))
    # Get Steam Account(s)
    # py3
    # steam_accounts = sorted(filter(None, run(["security dump-keychain {} | grep -B 8 {} | grep 0x00000007 | awk -F= \'{{print $2}}\'".format(keychain_name, "steamguard")], stdout=PIPE, shell=True).stdout.decode('utf-8').replace("\"", "").split("\n")), key=str.lower)
    # py2
    steam_accounts = sorted(filter(None, run("security dump-keychain {} | grep -B 8 {} | grep 0x00000007 | awk -F= \'{{print $2}}\'".format(keychain_name, "steamguard"), shell=True).replace("\"", "").split("\n")), key=str.lower)

    # Generate OTPs for all services
    for service in totp_services:
        # get key's secret from keychain
        secret = ''.join((filter(None, run("security find-generic-password -s {} -w {}".format(service, keychain_name), shell=True).split("\n"))))
        # if service is a steamguard, call steamguard code-gen method
        if not service in steam_accounts:
            # Standard TOTP Services
            otp_key = ''.join((filter(None, run("/usr/local/bin/oathtool --totp -b \"{}\"".format(secret), shell=True).split("\n"))))
            wf.add_item('{}'.format(service), otp_key, valid=True, arg=otp_key)
        else:
            # Non-Standard TOTP Services (╯°□°)╯︵ ┻━┻ STEAM
            otp_key = get_steamguard_code(secret)
            wf.add_item('{}'.format(service), otp_key, valid=True, arg=otp_key)

        # services_dict.update(dict(
        #     identifier=service,
        #     secret='key_secret',
        #     isSteam=False,
        # ))

    # # If `query` is `None` or an empty string, all items are returned
    # items = wf.filter(query, items)

    # # Show error if there are no results. Otherwise, Alfred will show
    # # its fallback searches (i.e. "Search Google for 'XYZ'")
    # if not items:
    #     wf.add_item('No matches', icon=ICON_WARNING)

    # # Generate list of results. If `items` is an empty list nothing happens
    # for item in items:
    #     wf.add_item(item['title'], ...)

    wf.send_feedback()
    # # Dump to JSON
    # services_json = json.loads(services_dict)

    # Add an item to Alfred feedback
    # wf.add_item(u'Item title', u'Item subtitle')

    # Send output to Alfred. You can only call this once.
    # Well, you *can* call it multiple times, but subsequent calls
    # are ignored (otherwise the JSON sent to Alfred would be invalid).
    # wf.send_feedback()

    # Lock Keychain when we're done!
    run("security lock-keychain {}".format(keychain_name), shell=True)


if __name__ == '__main__':
    # Create a global `Workflow` object
    workflow3 = Workflow(
        libraries=['./lib'], update_settings={
            'github_slug': 'iganeshk/alfred-totp',
            'frequency': 1, # every day
        },
        help_url='https://github.com/iganeshk/alfred-totp'
    )

    workflow3.magic_prefix = 'otp:'

    # Call your entry function via `Workflow.run()` to enable its helper
    # functions, like exception catching, ARGV normalization, magic
    # arguments etc.
    sys.exit(workflow3.run(main))