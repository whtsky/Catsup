import os
import datetime

from catsup.logger import logger
from catsup.utils import call


def git(config):
    logger.info("Deploying your blog via git")

    cwd = os.path.abspath(config.config.output)

    def _call(*args, **kwargs):
        return call(*args, cwd=cwd, **kwargs)

    if not os.path.exists(os.path.join(cwd, '.git')):
        _call('rm -rf *')
        # Hasn't setup git.
        _call('git init', silence=True)
        _call(['git', 'remote', 'add', 'origin', config.deploy.git.repo])
        if config.deploy.git.branch != 'master':
            _call('git branch -m %s' % config.deploy.git.branch, silence=True)
        _call(['git', 'pull', 'origin', config.deploy.git.branch])

    _call('git add .', silence=True)
    _call('git commit -m "Update at %s" % str(datetime.datetime.utcnow())',
          silence=True)
    _call(['git', 'push', 'origin', config.deploy.git.branch])


def rsync(config):
    logger.info("Deploying your blog via rsync")
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
    call(cmd)
