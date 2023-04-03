import io
import logging
import socket
import subprocess
import time
from random import randint
from typing import Any, Dict, List, Optional, Union

import docker

logger = logging.getLogger(__name__)


def _run_command(command: List[str], input: Optional[str] = None):
    with subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=False,
        bufsize=1,
    ) as p:
        if input:
            p.stdin.write(input.encode())
        p.stdin.close()
        out = io.TextIOWrapper(p.stdout, newline="", errors="replace")
        for line in out:
            logger.info(line)

    return p.returncode


class ContainerRun(object):
    """A class represent a container run in local."""

    CONTAINER_STATUS_RUNNING = "running"
    CONTAINER_STATUS_EXITED = "exited"
    CONTAINER_STATUS_PAUSED = "paused"

    def __init__(self, container: docker.models.containers.Container, port: int):
        """Initialize a container run.

        Args:
            container: A docker container object.
            port (int): The port container is exposing.

        """
        self.container = container
        self.port = port

    def is_running(self):
        """Return True if container is running, otherwise False."""
        return self.container.status == self.CONTAINER_STATUS_RUNNING

    def is_terminated(self):
        """Return True if container is terminated, otherwise False."""
        return self.container.status in [
            self.CONTAINER_STATUS_EXITED,
            self.CONTAINER_STATUS_PAUSED,
        ]

    def is_succeeded(self):
        """Return True if container is succeeded, otherwise False."""
        return (
            self.container.status == "exited"
            and self.container.attrs["State"]["ExitCode"] == 0
        )

    def wait_for_ready(self, interval=1):
        """Wait until container is ready.

        If a port is specified, wait until server is ready.

        """
        while True:
            self.container.reload()
            if self.is_running():
                break
            elif self.is_terminated():
                raise RuntimeError(
                    "Container is terminated: id={} status={}".format(
                        self.container.id, self.container.status
                    )
                )
            time.sleep(interval)

        if self.port:
            self._wait_for_serving(interval=interval)

    def _wait_for_serving(self, timeout=20, interval=1):
        start_time = time.time()
        while True:
            try:
                s = socket.create_connection(("127.0.0.1", self.port))
                s.close()
                return
            except socket.error as e:
                elapse = time.time() - start_time
                if elapse > timeout:
                    raise RuntimeError(
                        "Wait for container serving timeout, connection error: %s", e
                    )
                time.sleep(interval)
                continue

    def stop(self):
        self.container.reload()
        if self.is_running():
            self.container.stop()

    def start(self):
        self.container.reload()
        if not self.is_running():
            self.container.start()

    def delete(self):
        if self.is_running():
            self.container.stop()
        self.container.remove()

    def watch(self):
        """Watch container log and wait for container to exit."""
        log_iter = self.container.logs(
            stream=True,
            follow=True,
        )
        for log in log_iter:
            logger.info(log)
        self.container.reload()
        exit_code = self.container.attrs["State"]["ExitCode"]
        if exit_code != 0:
            raise RuntimeError(
                "Container run exited failed: exit_code={}".format(exit_code)
            )


def run_container(
    image_uri: str,
    container_name: str = None,
    port: int = None,
    environment_variables: Dict[str, str] = None,
    command: Union[List[str], str] = None,
    entry_point: Union[List[str], str] = None,
    volumes: Union[Dict[str, Any], List[str]] = None,
) -> ContainerRun:
    """Run a container in local.

    Args:
        image_uri (str):  A docker image uri.
        container_name (str): Name of the container.
        port (int): The port to expose.
        environment_variables (Dict[str, str]): Environment variables to set in the
            container.
        command (Union[List[str], str]): Command to run the container.
        entry_point (Union[List[str], str]): Entry point to run the container.
        volumes (Union[Dict[str, Any], List[str]]): Volumes to mount in the container.

    Returns:
        ContainerRun: A ContainerRun object.

    """
    client = docker.from_env()
    # use a random host port.
    host_port = randint(49152, 65535)
    container = client.containers.run(
        name=container_name,
        entrypoint=entry_point,
        image=image_uri,
        command=command,
        environment=environment_variables,
        ports={port: host_port} if port else None,
        volumes=volumes,
        detach=True,
    )
    container_run = ContainerRun(
        container=container,
        port=host_port,
    )
    return container_run
