#!/usr/bin/env python3
"""
Simplified Docker CLI wrapper for common operations.
"""

import argparse
import subprocess
import sys
import json
from pathlib import Path

def run_docker_cmd(args_list, capture_output=False):
    """Run a docker command."""
    cmd = ["docker"] + args_list
    if capture_output:
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout, result.stderr, result.returncode
    else:
        subprocess.run(cmd)

def cmd_ps(args):
    """List containers."""
    docker_args = ["ps"]
    if args.all or args.a:
        docker_args.append("-a")
    if args.format:
        docker_args.extend(["--format", args.format])
    else:
        docker_args.extend(["--format", "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"])
    run_docker_cmd(docker_args)

def cmd_run(args):
    """Run a container."""
    docker_args = ["run"]
    
    if args.detach or args.d:
        docker_args.append("-d")
    
    if args.interactive or args.i:
        docker_args.append("-i")
    
    if args.tty or args.t:
        docker_args.append("-t")
    
    if args.rm:
        docker_args.append("--rm")
    
    if args.name:
        docker_args.extend(["--name", args.name])
    
    for port in args.port or []:
        docker_args.extend(["-p", port])
    
    for env in args.env or []:
        docker_args.extend(["-e", env])
    
    for volume in args.volume or []:
        docker_args.extend(["-v", volume])
    
    docker_args.append(args.image)
    
    if args.command:
        docker_args.extend(args.command)
    
    run_docker_cmd(docker_args)

def cmd_stop(args):
    """Stop container(s)."""
    for container in args.containers:
        run_docker_cmd(["stop", container])

def cmd_start(args):
    """Start container(s)."""
    for container in args.containers:
        run_docker_cmd(["start", container])

def cmd_restart(args):
    """Restart container(s)."""
    for container in args.containers:
        run_docker_cmd(["restart", container])

def cmd_rm(args):
    """Remove container(s)."""
    docker_args = ["rm"]
    if args.force or args.f:
        docker_args.append("-f")
    docker_args.extend(args.containers)
    run_docker_cmd(docker_args)

def cmd_logs(args):
    """View container logs."""
    docker_args = ["logs"]
    if args.follow or args.f:
        docker_args.append("-f")
    if args.tail:
        docker_args.extend(["--tail", args.tail])
    else:
        docker_args.extend(["--tail", "100"])
    docker_args.append(args.container)
    run_docker_cmd(docker_args)

def cmd_exec(args):
    """Execute command in container."""
    docker_args = ["exec"]
    if args.interactive or args.i:
        docker_args.append("-i")
    if args.tty or args.t:
        docker_args.append("-t")
    docker_args.append(args.container)
    docker_args.extend(args.command)
    run_docker_cmd(docker_args)

def cmd_images(args):
    """List images."""
    docker_args = ["images"]
    if args.dangling or args.d:
        docker_args.append("--filter dangling=true")
    run_docker_cmd(docker_args)

def cmd_pull(args):
    """Pull image."""
    run_docker_cmd(["pull", args.image])

def cmd_rmi(args):
    """Remove image(s)."""
    run_docker_cmd(["rmi"] + args.images)

def cmd_build(args):
    """Build image."""
    docker_args = ["build"]
    for tag in args.tag or []:
        docker_args.extend(["-t", tag])
    docker_args.append(args.path)
    run_docker_cmd(docker_args)

def cmd_volumes(args):
    """List volumes."""
    run_docker_cmd(["volume", "ls"])

def cmd_volume_create(args):
    """Create volume."""
    run_docker_cmd(["volume", "create", args.name])

def cmd_volume_rm(args):
    """Remove volume(s)."""
    run_docker_cmd(["volume", "rm"] + args.volumes)

def cmd_volume_prune(args):
    """Prune unused volumes."""
    run_docker_cmd(["volume", "prune", "-f"])

def cmd_compose_up(args):
    """Compose up."""
    docker_args = ["compose", "up"]
    if args.detach or args.d:
        docker_args.append("-d")
    if args.build:
        docker_args.append("--build")
    run_docker_cmd(docker_args)

def cmd_compose_down(args):
    """Compose down."""
    docker_args = ["compose", "down"]
    if args.volumes or args.v:
        docker_args.append("-v")
    run_docker_cmd(docker_args)

def cmd_compose_logs(args):
    """Compose logs."""
    docker_args = ["compose", "logs"]
    if args.follow or args.f:
        docker_args.append("-f")
    if args.tail:
        docker_args.extend(["--tail", args.tail])
    if args.service:
        docker_args.append(args.service)
    run_docker_cmd(docker_args)

def cmd_compose_scale(args):
    """Compose scale."""
    run_docker_cmd(["compose", "scale", args.service])

def cmd_compose_config(args):
    """Compose validate config."""
    run_docker_cmd(["compose", "config"])

def cmd_cleanup(args):
    """Clean up unused resources."""
    if args.target == "all" or not args.target:
        print("Cleaning up all unused resources...")
        run_docker_cmd(["system", "prune", "-f"])
    elif args.target == "containers":
        run_docker_cmd(["container", "prune", "-f"])
    elif args.target == "images":
        run_docker_cmd(["image", "prune", "-f"])
    elif args.target == "volumes":
        run_docker_cmd(["volume", "prune", "-f"])
    elif args.target == "networks":
        run_docker_cmd(["network", "prune", "-f"])

def main():
    parser = argparse.ArgumentParser(description="Simplified Docker CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    # ps
    ps_parser = subparsers.add_parser("ps", help="List containers")
    ps_parser.add_argument("-a", "--all", action="store_true", help="Show all containers")
    ps_parser.add_argument("--format", help="Output format")
    
    # run
    run_parser = subparsers.add_parser("run", help="Run container")
    run_parser.add_argument("image", help="Image name")
    run_parser.add_argument("-d", "--detach", action="store_true", help="Run in background")
    run_parser.add_argument("-i", "--interactive", action="store_true", help="Interactive")
    run_parser.add_argument("-t", "--tty", action="store_true", help="Allocate TTY")
    run_parser.add_argument("--rm", action="store_true", help="Remove when stopped")
    run_parser.add_argument("--name", help="Container name")
    run_parser.add_argument("-p", "--port", action="append", help="Port mapping")
    run_parser.add_argument("-e", "--env", action="append", help="Environment variable")
    run_parser.add_argument("-v", "--volume", action="append", help="Volume mount")
    run_parser.add_argument("command", nargs="*", help="Command to run")
    
    # stop
    stop_parser = subparsers.add_parser("stop", help="Stop container(s)")
    stop_parser.add_argument("containers", nargs="+", help="Container name(s)")
    
    # start
    start_parser = subparsers.add_parser("start", help="Start container(s)")
    start_parser.add_argument("containers", nargs="+", help="Container name(s)")
    
    # restart
    restart_parser = subparsers.add_parser("restart", help="Restart container(s)")
    restart_parser.add_argument("containers", nargs="+", help="Container name(s)")
    
    # rm
    rm_parser = subparsers.add_parser("rm", help="Remove container(s)")
    rm_parser.add_argument("containers", nargs="+", help="Container name(s)")
    rm_parser.add_argument("-f", "--force", action="store_true", help="Force remove")
    
    # logs
    logs_parser = subparsers.add_parser("logs", help="View container logs")
    logs_parser.add_argument("container", help="Container name")
    logs_parser.add_argument("-f", "--follow", action="store_true", help="Follow logs")
    logs_parser.add_argument("--tail", help="Number of lines")
    
    # exec
    exec_parser = subparsers.add_parser("exec", help="Execute command in container")
    exec_parser.add_argument("container", help="Container name")
    exec_parser.add_argument("-i", "--interactive", action="store_true")
    exec_parser.add_argument("-t", "--tty", action="store_true")
    exec_parser.add_argument("command", nargs="+", help="Command to execute")
    
    # images
    images_parser = subparsers.add_parser("images", help="List images")
    images_parser.add_argument("-d", "--dangling", action="store_true", help="Show dangling only")
    
    # pull
    pull_parser = subparsers.add_parser("pull", help="Pull image")
    pull_parser.add_argument("image", help="Image name")
    
    # rmi
    rmi_parser = subparsers.add_parser("rmi", help="Remove image(s)")
    rmi_parser.add_argument("images", nargs="+", help="Image name(s)")
    
    # build
    build_parser = subparsers.add_parser("build", help="Build image")
    build_parser.add_argument("path", help="Build context path")
    build_parser.add_argument("-t", "--tag", action="append", help="Image tag")
    
    # volumes
    volumes_parser = subparsers.add_parser("volumes", help="List volumes")
    
    # volume create
    volume_create_parser = subparsers.add_parser("volume-create", help="Create volume")
    volume_create_parser.add_argument("name", help="Volume name")
    
    # volume rm
    volume_rm_parser = subparsers.add_parser("volume-rm", help="Remove volume(s)")
    volume_rm_parser.add_argument("volumes", nargs="+", help="Volume name(s)")
    
    # volume prune
    volume_prune_parser = subparsers.add_parser("volume-prune", help="Prune unused volumes")
    
    # compose up
    compose_up_parser = subparsers.add_parser("compose-up", help="Compose up")
    compose_up_parser.add_argument("-d", "--detach", action="store_true")
    compose_up_parser.add_argument("--build", action="store_true")
    
    # compose down
    compose_down_parser = subparsers.add_parser("compose-down", help="Compose down")
    compose_down_parser.add_argument("-v", "--volumes", action="store_true")
    
    # compose logs
    compose_logs_parser = subparsers.add_parser("compose-logs", help="Compose logs")
    compose_logs_parser.add_argument("service", nargs="?", help="Service name")
    compose_logs_parser.add_argument("-f", "--follow", action="store_true")
    compose_logs_parser.add_argument("--tail", help="Number of lines")
    
    # compose scale
    compose_scale_parser = subparsers.add_parser("compose-scale", help="Compose scale")
    compose_scale_parser.add_argument("service", help="Service=count (e.g., web=3)")
    
    # compose config
    compose_config_parser = subparsers.add_parser("compose-config", help="Compose validate")
    
    # cleanup
    cleanup_parser = subparsers.add_parser("cleanup", help="Clean up unused resources")
    cleanup_parser.add_argument("target", nargs="?", choices=["all", "containers", "images", "volumes", "networks"], help="What to clean")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    commands = {
        "ps": cmd_ps,
        "run": cmd_run,
        "stop": cmd_stop,
        "start": cmd_start,
        "restart": cmd_restart,
        "rm": cmd_rm,
        "logs": cmd_logs,
        "exec": cmd_exec,
        "images": cmd_images,
        "pull": cmd_pull,
        "rmi": cmd_rmi,
        "build": cmd_build,
        "volumes": cmd_volumes,
        "volume-create": cmd_volume_create,
        "volume-rm": cmd_volume_rm,
        "volume-prune": cmd_volume_prune,
        "compose-up": cmd_compose_up,
        "compose-down": cmd_compose_down,
        "compose-logs": cmd_compose_logs,
        "compose-scale": cmd_compose_scale,
        "compose-config": cmd_compose_config,
        "cleanup": cmd_cleanup,
    }
    
    if args.command in commands:
        commands[args.command](args)
    else:
        print(f"Unknown command: {args.command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
