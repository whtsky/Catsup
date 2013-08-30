import os
import datetime

from catsup.logger import logger
from catsup.utils import call


def git(config):
    logger.info("Deploying your site via git")

    cwd = os.path.abspath(config.config.output)

    def _call(*args, **kwargs):
        return call(*args, cwd=cwd, **kwargs)

    dot_git_path = os.path.join(cwd, '.git')

    if os.path.exists(dot_git_path) and \
            _call('git remote -v | grep %s' % config.deploy.git.repo) == 0:
        if os.path.exists(dot_git_path):
            import shutil
            shutil.rmtree(dot_git_path)
        _call('git init', silence=True)
        _call('git remote add origin %s' % config.deploy.git.repo)
        if config.deploy.git.branch != 'master':
            _call('git branch -m %s' % config.deploy.git.branch, silence=True)
        _call('git pull origin %s' % config.deploy.git.branch)
        _call('rm -rf *')

        from catsup.generator import Generator

        generator = Generator(config.path)
        generator.generate()

    _call('git add .', silence=True)
    _call('git commit -m "Update at %s"' % str(datetime.datetime.utcnow()),
          silence=True)
    _call('git push origin %s' % config.deploy.git.branch)


def rsync(config):
    logger.info("Deploying your site via rsync")
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
