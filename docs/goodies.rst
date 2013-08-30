Goodies
===========

.. _preview-server:

Preview Server
----------------
Preview your site **without deploy** ::

    catsup server
    catsup server -p 8000

.. note:: Preview Server will build your site before running.
.. attention:: You should never usr Preview Server in a production environment.

.. _deploy:

Deploy Support
----------------
Help you deploy your site via git or rsync ::

    catsup deploy # Deploy via default way
    catsup rsync # Deploy via rsync
    catsup git # Deploy via git


Webhook
---------
If you host your posts on GitHub or Bitbucket, catsup can generate your site when you push to your repo.

You need to clone your repo and start a  webhook server ::

    git clone git://path/to/your/repo.git posts
    catsup webhook -p 12580

.. attention:: Catsup webhook is not a daemon process.That means you may need to use Supervisor_ to turn it into daemon.

Then configure webhook on GitHub or Bitbucket. Here we use GitHub as an example:

+ Go to the “admin” page for your project
+ Click “Service Hooks”
+ In the available service hooks, click “WebHook URLs“
+ Type your url [1]_
+ Click “Update Settings”

.. [1] If your server's ip is 1.2.3.4 , you can type ``http://1.2.3.4:12580/webhook``

Then when you push to GitHub, catsup will pull and generate your site.

.. _Supervisor: http://pypi.python.org/pypi/supervisor/
