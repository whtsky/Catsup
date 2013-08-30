Goodies
===========

.. _preview-server:

Preview Server
----------------
Preview your site without deploy ::

    catsup server
    catsup server -p 8000

Preview server will regenerate your site when :

+ Your source folder (``posts`` by default) changes (Like add a new post or modify one)
+ Your theme folder changes(Useful for writing themes for Catsup)
+ Catsup program changes(Useful for writing codes for Catsup)

.. note:: Catsup will ignore ``site.url`` and build your site into a temporary directory when running Preview Server.

.. _deploy:

Deploy Support
----------------
Help you deploy your site via git or rsync ::

    catsup deploy # Deploy via default way
    catsup rsync # Deploy via rsync
    catsup git # Deploy via git


Webhook
---------
If you host your site's source on GitHub or Bitbucket, Catsup can generate your site when you push to your repo.

You need to clone your repo and start webhook server ::

    git clone git://path/to/your/site.git
    cd site
    catsup webhook -p 12580

.. attention:: Catsup webhook is not a daemon process.That means you may need to use Supervisor_ to turn it into daemon.

Then configure webhook on GitHub or Bitbucket. Here we use GitHub as an example:

+ Go to the “admin” page for your project
+ Click “Service Hooks”
+ In the available service hooks, click “WebHook URLs“
+ Type your url [1]_
+ Click “Update Settings”

.. [1] If your server's ip is 1.2.3.4 , you can type ``http://1.2.3.4:12580/webhook``

Then when you push to GitHub, Catsup will pull and generate your site.

.. _Supervisor: http://pypi.python.org/pypi/supervisor/
