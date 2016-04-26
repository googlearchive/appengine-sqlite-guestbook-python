![status: inactive](https://img.shields.io/badge/status-inactive-red.svg)

**This repository is deprecated and no longer maintained.**

Copyright (C) 2010-2014 Google Inc.
## appengine-sqlite-guestbook-python

A guestbook sample for the App Engine VM Runtime, which uses the Python sqlite3 library.

## Project Setup, Installation, and Configuration

You can run this application only on the [App Engine VM Runtime][1].
Currently, the VM Runtime is part of the Early Access Program, and only the participants
are able to run this application.

## Deploying

1. Make sure that you are invited to the VM Runtime Trusted Tester
   Program, and [download the SDK](http://commondatastorage.googleapis.com/gae-vm-runtime-tt/vmruntime_sdks.html).
2. Update the `application` value of the `app.yaml` file from
   `your-app-id` to the app-id which is whitelisted for the VM Runtime
   Trusted Tester Program.
3. Run the following command:

        $ <sdk_directory>/appcfg.py -s preview.appengine.google.com update <project_directory>

## Contributing changes

* See CONTRIB.md

## Licensing

* See LICENSE

[1]: https://docs.google.com/document/d/1VH1oVarfKILAF_TfvETtPPE3TFzIuWqsa22PtkRkgJ4
