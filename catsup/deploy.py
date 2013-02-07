import os
import sys
import logging

from catsup.options import g, config
from catsup.utils import check_git, check_rsync


def git():
    if not check_git():
        logging.error("Catsup can't find git.Please install git first.")
        sys.exit(1)
    pass



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
