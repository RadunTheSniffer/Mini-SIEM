import logging
import socket
import configparser
import psutil
import time
import ssl

def send_log(log_message, server_address, server_port):
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE  # Use only for local testing

    try:
        with socket.create_connection((server_address, server_port)) as sock:
            with context.wrap_socket(sock, server_hostname=server_address) as ssock:
                ssock.sendall(log_message.encode())
    except Exception as e:
        logging.error(f"Error sending log: {e}")

def main():
    config = configparser.ConfigParser()
    config.read('config.ini')

    server_address = config['Server']['address']
    server_port = int(config['Server']['port'])
    log_file = config['Logs']['system_log']

    while True:
        try:
            with open(log_file, 'r') as f:
                for line in f:
                    send_log(line.strip(), server_address, server_port)

            for proc in psutil.process_iter(['pid', 'name']):
                send_log(f"Process: {proc.info}", server_address, server_port)

        except Exception as e:
            logging.error(f"Error reading log file: {e}")

        time.sleep(5)

if __name__ == "__main__":
    main()
