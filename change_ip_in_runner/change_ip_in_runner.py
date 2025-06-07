import docker
import toml
import pathlib
import re
import sys
#import schedule
import time


def get_ip_in_file() -> str:
    path_to_toml = pathlib.Path("./gitlab-runner-config/config.toml")
    config_file = toml.load(path_to_toml)
    extra_hosts: str = config_file["runners"][0]["docker"]["extra_hosts"][0]
    return extra_hosts


def change_ip_address_in_toml(ip_address: str):
    path_to_toml = pathlib.Path("./gitlab-runner-config/config.toml")
    config_file = toml.load(path_to_toml)
    extra_hosts: str = config_file["runners"][0]["docker"]["extra_hosts"][0]
    ip_addresss_to_replace = re.match(r".*:(\d+\.\d+\.\d+\.\d+)", extra_hosts)

    if ip_addresss_to_replace:
        print(ip_addresss_to_replace.group(1))
        extra_hosts = extra_hosts.replace(ip_addresss_to_replace.group(1), ip_address)

    print(extra_hosts)
    config_file["runners"][0]["docker"]["extra_hosts"][0] = extra_hosts

    print(config_file)
    with open(path_to_toml, "w") as file:
        toml.dump(config_file, file)


def get_container_ip(container_name, network_name="bridge") -> str | None:
    """
    Retrieves the IP address of a specific Docker container.

    :param container_name: Name or ID of the Docker container.
    :param network_name: The Docker network the container is connected to (default: "bridge").
    :return: IP address of the container or None if not found.
    """
    client = docker.DockerClient(base_url='unix:///var/run/docker.sock')

    try:
        container = client.containers.get(container_name)
        network = container.attrs["NetworkSettings"]["Networks"]
        for key, value in network.items():
            if network_name in key:
                print(network)
                network_name = key
                break

        ip_address = container.attrs["NetworkSettings"]["Networks"][network_name]["IPAddress"]
        return ip_address
    except docker.errors.NotFound:
        print(f"❌ Error: Container '{container_name}' not found.")
    except KeyError:
        print(f"❌ Error: Network '{network_name}' not found for container '{container_name}'.")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

    return None


def start_script():
    try:
        if ip := get_container_ip("gitlab", "gitlab_env_gitlab_net"):
            change_ip_address_in_toml(ip)
            print("Changed the ip address")
        else:
            print("Couldn't find proper network raising and exception function returend None")
            raise TypeError
    except Exception as e:
        print(f"There was and error /n {e}")


if __name__ == "__main__":
#    schedule.every(5).minutes.do(start_script)
#
    while True:
        container_ip = get_container_ip("gitlab", "gitlab_env_gitlab_net")
        ip_in_file = get_ip_in_file()
        if container_ip != ip_in_file:
            start_script()
        time.sleep(10)
    
