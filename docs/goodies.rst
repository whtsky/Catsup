Goodies
===========

.. _preview-server:

Preview Server
----------------
Preview your blog **without build & deploy** ::

    catsup server
    catsup server -p 8000

Deploy Support
----------------
Help you deploy your blog via git or rsync ::

    catsup deploy # Deploy via default way
    catsup rsync # Deploy via rsync
    catsup git # Deploy via git

.. note:: Catsup has GitHub Pages support.It will create a `CNAME` file when deploy via git.

Webhook
---------
If you host your posts on GitHub or Bitbucket, catsup can generate your blog when you push to your repo.

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

Then when you push to GitHub, catsup will pull and generate your blog.

.. _Supervisor: http://pypi.python.org/pypi/supervisor/

Twitter Card
--------------
Catsup has a build-in Twitter Card support via ``meta`` marco.

Click here if you don't know what Twitter Card is : https://dev.twitter.com/docs/cards

All you need to do is go to https://dev.twitter.com/form/participate-twitter-cards and submit your blog.
Then wait for the magic works.