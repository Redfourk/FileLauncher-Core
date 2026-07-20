import urllib.request
import json


def send_command(command_str, server_url="http://127.0.0.1:8080"):
    url = f"{server_url}/command"
    data = command_str.encode('utf-8')

    req = urllib.request.Request(url, data=data, method='POST')

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            print(f"Server replied: {result['result']}")
    except Exception as e:
        print(f"Failed to send command: {e}")


# Usage Examples:
if __name__ == "__main__":
    print("Testing command: delete old_file.txt")
    send_command("delete old_file.txt")

    print("Testing command: move data.txt backup.txt")
    send_command("move data.txt backup.txt")

    print("Testing command: version")
    send_command("version")