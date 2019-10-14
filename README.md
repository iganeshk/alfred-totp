<h1 align="center">
  <a href="https://github.com/iganeshk/alfred-totp" title="Alfred TOTP Workflow">
    <img alt="Alfred TOTP" src="https://github.com/iganeshk/alfred-totp/raw/master/assets/alfred-totp.png" width="15%"/>
  </a>
  <br />
  Alfred TOTP Workflow
</h1>
<p align="center">
  Obtain one time passwords from alfred.
</p>

## Requirements

* [AlfredApp](https://www.alfredapp.com/) (Alfred 3 & 4 tested)
* [Brew](https://brew.sh/) package manager
* Python3 (SteamGuard OTP support)

## Installation

`$ brew install oauthtool`

## Obtaining your TOTP secrets
You could either export it from the existing applications you're using or generate a new secret from the website's user control panel.

For SteamGuard OTP, follow [this guide](https://github.com/SteamTimeIdler/stidler/wiki/Getting-your-'shared_secret'-code-for-use-with-Auto-Restarter-on-Mobile-Authentication) to obtain your secret key.

Then insert your totp secret codes into the macOS keychain `alfred-totp.keychain` like so:

```
$ security -i
> create-keychain alfred-totp.keychain
> set-keychain-settings alfred-totp.keychain
> add-generic-password -a alfred-totp -s "name of service" -w "totp secret" alfred-totp.keychain
> # repeat above command as needed, crtl-c to quit.
```

Now [download](https://github.com/iganeshk/alfred-totp/releases/latest) the latest workflow and install it.

## Usage

In alfred just type `otp` then start typing the name of your service. 

<img alt="alfred-totp-1" src="https://github.com/iganeshk/alfred-totp/raw/master/assets/alfred_totp_1.png" width="80%" />

The TOTP code will be pasted to the top most app by default and copied to the clipboard on option return.

<img alt="alfred-totp-2" src="https://github.com/iganeshk/alfred-totp/raw/master/assets/alfred_totp_2.png" width="80%" />


If you would like to display all the service's passwords at once, configure the object (script filter) of alfred-totp's workflow as below

<img alt="alfred-totp-2" src="https://github.com/iganeshk/alfred-totp/raw/master/assets/alfred_totp_3_list_setting.png" width="80%" />

<img alt="alfred-totp-2" src="https://github.com/iganeshk/alfred-totp/raw/master/assets/alfred_totp_4_list_all.png" width="80%" />

* Note: Icons reflected in the results are located at workflow's icon directory and follow service name as entered in the keychain.

## Thanks

Thanks to [waynehoover](https://github.com/waynehoover/) and [aria.ia](https://www.aria.ai/blog/posts/storing-secrets-with-keychain.html) for the code on how to list items from macOS keychain.
