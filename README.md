WonderPush Python library
=========================

Find the full WonderPush services documentation at:
http://www.wonderpush.com/docs/.



Introduction
------------

This project contains Python libraries for interacting with the WonderPush services.
It helps you performing calls to the APIs. This contrasts with the SDKs, which are targetted at being integrated within your apps and handle interactions with the users.


### APIs

WonderPush comes as two APIs, one aimed at the user devices, and the other optional one aimed at your servers and tools.
The former is simply called the REST API, whereas the latter is called the Management API.

This tool helps you performing calls to both.

#### Management API Reference

All references for the WonderPush Management API are available on the WonderPush documentation pages:
https://wonderpush-management-api.readme.io/v1/docs.

#### API Reference

All references for the WonderPush API are available on the WonderPush documentation pages:
http://www.wonderpush.com/docs/reference/api/v1.



Command-line tool
-----------------


### Dependencies

The command-line tool requires the following dependencies:

* argparse

    To install it, try one of the following, depending on your system:
    * Use python >= 2.7 or >= 3.2.
    * `sudo apt-get install python-argparse`
    * `sudo easy_install argparse`
    * `sudo pip install argparse`
    * Or install it manually: https://pypi.python.org/pypi/argparse

* requests

    To install it, try one of the following, depending on your system:
    * `sudo apt-get install python-requests`
    * `sudo pip requests`
    * `sudo easy_install requests`
    * Or install it manually: http://docs.python-requests.org/en/latest/user/install/#get-the-code

* pygments

    To install it, try one of the following, depending on your system:
    * `sudo apt-get install python-pygments`
    * `sudo easy_install Pygments`
    * Or install it manually: http://pygments.org/docs/installation/


### Usage

To get help, simply enter:
```
./rest.py --help
```

Note: The shorter `-h` does not show the help as it is the short for `--host`.

You should get the following output:
```
usage: rest.py [--help] [-p PROFILE] [-h HOST] [-v] [-q] [--no-ssl-verify]
               [--no-format] [--no-highlight] [--style STYLE] [-c CLIENT_ID]
               [-s CLIENT_SECRET] [-a ACCESS_TOKEN] [-i SID]
               [method] path [header:value [header:value ...]]
               [param=value [param=value ...]]

REST client for the WonderPush platform.

positional arguments:
  method                The HTTP method to use: GET, POST, PUT, DELETE
                        (default: GET)
  path                  The path to query. Eg.: /v1/players/me
  header:value          Additional headers.
  param=value           Additional query parameters. Eg.: lang=en

optional arguments:
  --help                show this help message and exit
  -p PROFILE, --profile PROFILE
                        Profile to use (default: default)
  -h HOST, --host HOST  Host to contact (default: api.wonderpush.com)
  -v, --verbose         Controls verbosity level
  -q, --quiet           Mute, except for exceptional errors
  --no-ssl-verify       Disable verification of SSL certificate
  --no-format           Disable formatting the output
  --no-highlight        Disable highlighting the output
  --style STYLE         Pygments style to use while highlighting (default:
                        default)
  -c CLIENT_ID, --client-id CLIENT_ID
                        Your client id
  -s CLIENT_SECRET, --client-secret CLIENT_SECRET
                        Your client secret
  -a ACCESS_TOKEN, --access-token ACCESS_TOKEN
                        The OAuth access token to use
  -i SID, --sid SID     The session id to use

You can create a configuration file in "~/.wonderpush/" or
"%APPDATA%\wonderpush" named "rest.conf" to define default arguments
and profiles.

The file structure is as follows:
    {
      "arguments": [],    # default arguments, always prepended to your
                          # command line
      "profiles": {
        "default": {      # default profile
          "arguments": [] # arguments to prepend after the default arguments
        },
        ...               # you can define your own profiles
      }
    }

Available styles are:
  - monokai
  - manni
  - rrt
  - perldoc
  - borland
  - colorful
  - default
  - murphy
  - vs
  - trac
  - tango
  - fruity
  - autumn
  - bw
  - emacs
  - vim
  - pastie
  - friendly
  - native
```


### Generalities

Every call to the Management API needs the application access token, given using the `-a`/`--access-token`.
You can find it in your dashboard under the _Settings / Configuration_ page, on the _Management API_ tab.

Every call to the REST API needs both an access token and a client secret,
given using the `-a`/`--access-token` and `-s`/`--client-secret` arguments respectively.

The only exception to the above is the call to get a client access token,
which needs both the client id and client secret of your application,
given using the `-c`/`--client-id` and `-s`/`--client-secret` arguments respectively.

Specifying an access token or a client id when it is not required by the REST end-point you're calling
merely adds it as an extraneous argument.
Although harmless, this should be avoided.

The client secret is required to calculate the signature of requests to the REST API,
whereas the client id identifies the application for which an access token is to be created,
and the access token in itself is attached to your application already.


### Access tokens

The [Management REST API](http://www.wonderpush.com/docs/reference/management-api/v1) requires either `staff` or `application` access tokens.
You can find them under your profile or your application's profile respectively.
The `staff` access token is subject to the rights you have been granted, whereas the `application` access token holds all rights.

The [REST API ](http://www.wonderpush.com/docs/reference/api/v1) requires `installation` access tokens,
you can create one by calling the `POST /v1/authentication/accessTokens deviceId=YOUR_DEVICE_ID devicePlatform=PLATFORM_HANDLED_BY_YOUR_APP` end-point.


### Configuration

As described in the above help message, you can create profiles or inject default arguments,
to avoid mentioning client secrets and access tokens for each and every call.

Here is a good start for your `~/.wonderpush/rest.conf`:
```json
{
  "arguments": [ "--style=native" ],
  "profiles": {
    "default": {
      "arguments": [  ]
    },

    "my_app": {
      "arguments": [ "-a", "YOUR_APPLICATION_ACCESS_TOKEN" ]
    },

    "my_test_device": {
      "arguments": [ "-s", "YOUR_CLIENT_SECRET", "-a", "THE_ACCESS_TOKEN_YOU_CREATED" ]
    }
  }
}
```

You can get your application client id and client secret [in your dashboard](https://dashboard.wonderpush.com/),
under _Settings / Configuration_ in the left menu, listed in the block entitled _Application credentials_.


### [Management API] Send your first notification

Simply call:
```shell
./rest.py -a YOUR_APPLICATION_ACCESS_TOKEN POST /v1/management/deliveries targetSegmentIds=@ALL notification='{"alert":{"text":"Hello, API!"}}'
```

You should get an answer like this one:
```json
{"success":true}
```

And all your installations will receive a notification.


### [REST API] Create your first installation access token

Simply call:
```shell
./rest.py -c YOUR_CLIENT_ID -s YOUR_CLIENT_SECRET POST /v1/authentication/accessToken deviceId=FAKE_TEST_DEVICE_ID_1 devicePlatform=Android
```

You should get an answer like this one:
```json
{
    "_serverTook": 67, 
    "_serverTime": 1421761259767, 
    "token": "dbW8ZraJYdBHZMRflgMnBOBogNWeFR5GgAwzvkKYmQPtiH2Nwla5III7TAHrH9f2ETR3M4dQBorjXH44hos7kb", 
    "clientId": "a0741443ad9a35758032216dab09c0934da7d984", 
    "expiresAt": 0, 
    "updateDate": 1421761260323, 
    "scope": "installation", 
    "creationDate": 1421761260323, 
    "data": {
        "installationId": "7aa7b3ec0db5664d335f5559b4821ddf13b48e89", 
        "applicationId": "0192gefjs6v82kc0", 
        "sid": "bec86771ab0c915ecb2dfc1468ca78203af6b31e4a31e1283b62a64f4b6dc2fb"
    }, 
    "id": "dbW8ZraJYdBHZMRflgMnBOBogNWeFR5GgAwzvkKYmQPtiH2Nwla5III7TAHrH9f2ETR3M4dQBorjXH44hos7kb"
}
```

If you get the following error instead:
```json
{
    "error": {
        "status": 400, 
        "message": "The platform is not supported", 
        "code": "12019"
    }
}
```
you should change the `devicePlatform=Android` argument by one of the platform you checked in your application profile.
For instance if your application targets iOS only, you must use `devicePlatform=iOS`.
