import docker
import docker.errors
import time


def add_user_to_gitlab(container_name, network_name="bridge", user: str = "user", password: str = "123password") -> str | None:
    """
    Retrieves the IP address of a specific Docker container.

    :param container_name: Name or ID of the Docker container.
    :param network_name: The Docker network the container is connected to (default: "bridge").
    :return: IP address of the container or None if not found.
    """
    client = docker.DockerClient(base_url='unix:///var/run/docker.sock')
    try:
        container = client.containers.get(container_name)
        # Prepare the Ruby code as a single-line string for gitlab-rails runner
        ruby_code = f"""
begin
  u = Users::CreateService.new(nil, username: '{user}', email: '{user}@example.com', name: 'Test User', password: '{password}', password_confirmation: '{password}', organization_id: Organizations::Organization.first.id, skip_confirmation: true).execute;
  if u && u.success?
    puts "User created with ID: \#{{u.id}}"
  else
    puts "User creation failed: \#{{u.errors.full_messages.join(', ') rescue 'Unknown error'}}"
    exit 1
  end
rescue => e
  puts "Ruby error: \#{{e.message}}"
  exit 1
end
"""
        # Use gitlab-rails runner and pass the code with -e
        command = ["gitlab-rails", "runner", "-e", "production",ruby_code]
        exec_result = container.exec_run(command,
                                           stdout=True,
                                           stderr=True,
                                           tty=True)

        if exec_result.exit_code == 0:
            print("✅ User creation command executed successfully.")
            print(exec_result)
            print(f"Output: {exec_result.output.decode('utf-8').strip()}")
            return exec_result.output.decode('utf-8').strip()
        else:
            print("❌ Error: User creation command failed.")
            print(f"Error Output: {exec_result.output.decode('utf-8').strip()}")
            return None
    except docker.errors.NotFound:
        print(f"❌ Error: Container '{container_name}' not found.")
    except KeyError:
        print(f"❌ Error: Network '{network_name}' not found for container '{container_name}'.")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

    return None


def register_global_runner(container_name, network_name="bridge",):
    """Registers a global GitLab runner and returns the registration token."""
    client = docker.DockerClient(base_url='unix:///var/run/docker.sock')
    try:
        container = client.containers.get(container_name)

        ruby_code = """
begin
  runner = Runner.create!(
    token: SecureRandom.hex(16),
    description: 'Global Runner',
    executor: 'docker',
    run_untagged: true,
    access_level: :not_protected
  )
  puts "Runner token: \#{runner.token}"
rescue => e
  puts "Ruby error: \#{{e.message}}"
  exit 1
end
    """
        command = ["gitlab-rails", "runner", "-e", "production", ruby_code]
        output = container.exec_run(command,
                                           stdout=True,
                                           stderr=True,
                                           tty=True)

        if output and "Runner token:" in output:
            runner_token = output.split("Runner token: ")[1]
            print("✅ Global runner registered successfully.")
            return runner_token
        else:
            print("❌ Failed to register global runner.")
            return None

    except docker.errors.NotFound:
        print(f"❌ Error: Container '{container_name}' not found.")
    except KeyError:
        print(f"❌ Error: Network '{network_name}' not found for container '{container_name}'.")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

    return None


def start_script():
    print(add_user_to_gitlab("gitlab", "gitlab_gitlab_net", "usr"))
    print(register_global_runner("gitlab", "gitlab_gitlab_net"))
    print("started")


if __name__ == "__main__":
    print("script started")
    start_script()
