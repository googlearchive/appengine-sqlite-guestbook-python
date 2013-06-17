## appengine-sqlite-guestbook-python

Another guestbook sample with VM Runtime and Python sqlite3 library.

## Project Setup, Installation, and Configuration

You can run this application only on the [App Engine VM
Runtime][1]. Now the VM Runtime is under Trusted Tester Program, and
only the testers are able to run this application.

## Deploying

1. Make sure that you are invited to the VM Runtime Trusted Tester
   Program, and download the custom SDK.
2. Update the `application` value of the `app.yaml` file from
   `your-app-id` to the app-id which is whitelisted for the VM Runtime
   Trusted Tester Program.
3. Run the following command:
   $ /$CUSTOM_SDK_DIR/appcfg.py -R update <directory>

## Contributing changes

* See CONTRIB.md

## Licensing

* See LICENSE

[1]: https://docs.google.com/a/google.com/document/d/1VH1oVarfKILAF_TfvETtPPE3TFzIuWqsa22PtkRkgJ4/edit
