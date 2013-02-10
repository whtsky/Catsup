import os
import sys
import datetime
import logging

from catsup.options import g, config
from catsup.utils import call, check_git, check_rsync


def git():
    if not check_git():
        logging.error("Catsup can't find git.Please install git first.")
        sys.exit(1)
    logging.info("Deploying your blog via git")

    cwd = os.path.abspath(config.config.output)
    def _call(*args, **kwargs):
        return call(*args, cwd=cwd, **kwargs)

    if not os.path.exists(os.path.join(cwd, '.git')):
        _call('rm -rf *')
        # Hasn't setup git.
        _call('git init', silence=True)
        _call(['git', 'remote', 'add', 'origin', config.deploy.git.repo],
            silence=False)
        if config.deploy.git.branch != 'master':
            _call('git branch -m %s' % config.deploy.git.branch, silence=True)
        _call(['git', 'pull', 'origin', config.deploy.git.branch])

        logging.info("Rebuild your blog..")
        import catsup.build
        catsup.build.build()

    # GitHub custom domain support
    with open(os.path.join(cwd, 'CNAME'), 'w') as f:
        domain = config.site.url.split('//')[-1].rstrip('/')
        f.write(domain)

    _call('git add .', silence=True)
    _call(['git', 'commit',
       '-m',"Update at %s" % str(datetime.datetime.utcnow())],
        silence=True)
    _call(['git', 'push', 'origin', config.deploy.git.branch])



def rsync():
    if not check_rsync():
        logging.error("Catsup can't find rsync.Please install rsync first.")
        sys.exit(1)
    logging.info("Deploying your blog via rsync")
    if config.deploy.rsync.delete:
        args = "--delete"
    else:
        args = ""
    cmd = "rsync -avze 'ssh -p {ssh_port}' {args}" \
          " {deploy_dir}/ {ssh_user}@{ssh_host}:{document_root}".format(
        ssh_port=config.deploy.rsync.ssh_port,
        args=args,
        deploy_dir=config.config.output,
        ssh_user=config.deploy.rsync.ssh_user,
        ssh_host=config.deploy.rsync.ssh_host,
        document_root=config.deploy.rsync.document_root
    )
    os.system(cmd)
