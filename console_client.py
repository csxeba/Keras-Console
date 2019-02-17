import socket
import argparse


SUPPORTED_COMMANDS = ["end-training", "save-model", "exit-console"]
PROMPT = "[Keras-Console] > "
SEP = "<(O.o)>"


def pprint(*args, **kw):
    print("[Keras-Console] ", *args, **kw)


def initiate_connection(ip, port):
    connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    connection.connect((ip, port))
    return connection


def print_help():
    pprint("Supported commands:")
    for command in SUPPORTED_COMMANDS:
        pprint(command)


def read_command():
    command = input(PROMPT).lower().strip().replace(" ", "-").replace("_", "-")
    if command == "help":
        print_help()
    if command not in SUPPORTED_COMMANDS:
        pprint("Unsupported command!")
        print_help()
    return command


def send_command(connection, command):
    command += SEP
    binary = command.encode()
    connection.sendall(binary)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("ip", default="127.0.0.1")
    parser.add_argument("--port", "-p", default=7199)
    args = parser.parse_args()

    connection = initiate_connection(args.ip, int(args.port))

    while 1:
        command = read_command()
        if command == "exit-console":
            break
        send_command(connection, command)

    pprint("See you!")


if __name__ == '__main__':
    main()
