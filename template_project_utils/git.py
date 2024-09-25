# Copyright (C) 2023 twyleg
import pygit2
import logging

from pathlib import Path


def remove_remote(project_dir_path: Path, name: str) -> None:
    repo = pygit2.Repository(str(project_dir_path))
    remote_collection = pygit2.remotes.RemoteCollection(repo)

    logging.debug("Remotes:")
    for remote in repo.remotes:
        logging.debug("  %s=%s", remote.name, remote.url)

    try:
        logging.info("Removing remote '%s=%s'", name, repo.remotes[name].url)
        remote_collection.delete(name)
    except KeyError as e:
        logging.warning("Unable to remove remote '%s' due to non-existence", name)
