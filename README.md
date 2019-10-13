# Alfred TOTP

Alfred 2-factor authentication workflow

## Requirements

* AlfredApp
* Brew package manager

## Installation

`$ brew install oauthtool`

Then insert your totp codes into the macOS keychain `alfred-totp.keychain` like so:

```
$ security -i
> create-keychain alfred-totp.keychain
> set-keychain-settings alfred-totp.keychain
> add-generic-password -a alfred-totp -s "Name of service" -w "TOTP CODE" alfred-totp.keychain
> # repeat above command as needed, crtl-c to quit.
```

Now [download](https://github.com/waynehoover/atotp/releases) and install the workflow.

## Usage

In alfred just type `otp` then start typing the name of your service. 

<img alt="alfred-totp-1" src="https://github.com/iganeshk/alfred-totp/raw/master/assets/alfred_totp_1.png" width="80%" />

The TOTP code will be pasted to the top most app by default and copied to the clipboard on option return.

<img alt="alfred-totp-2" src="https://github.com/iganeshk/alfred-totp/raw/master/assets/alfred_totp_2.png" width="80%" />


If you would like to display all the service's passwords at once, configure the object (script filter) of alfred-totp's workflow as below

<img alt="alfred-totp-2" src="https://github.com/iganeshk/alfred-totp/raw/master/assets/alfred_totp_3_list_setting.png" width="80%" />

<img alt="alfred-totp-2" src="https://github.com/iganeshk/alfred-totp/raw/master/assets/alfred_totp_4_list_all.png" width="80%" />

## Finding your totp codes
On most websites you can login and see your totp code in the 2-factor setting page.

## Thanks

Thanks to [aria.ia](https://www.aria.ai/blog/posts/storing-secrets-with-keychain.html) for the code on how to list items from macOS keychain.
