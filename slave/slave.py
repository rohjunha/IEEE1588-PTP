import socket
import sys
import time

server_socket = None
ADDRESS = ''
PORT = 2468


def main():
    global server_socket
    try:
        print('Creating socket...')
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except socket.error as e:
        print('Error creating socket: ' + str(e) + '. Exitting...')
        server_socket.close()
        sys.exit(-1)

    try:
        print('Binding to socket... ' + str(ADDRESS) + ':' + str(PORT))
        server_socket.bind((ADDRESS, PORT))
    except socket.error as e:
        print('Error binding to socket: ' + str(e) + '. Exitting...')
        server_socket.close()
        sys.exit(-1)

    try:
        while True:
            print('\nReady to receive requests on port ' + str(PORT) + '...')
            data, addr = server_socket.recvfrom(4096)
            data = data.decode()
            print('Request from ' + addr[0])
            if 'sync' == data:
                server_socket.sendto('ready'.encode('utf-8'), addr)
                num_of_times, addr = server_socket.recvfrom(4096)
                server_socket.sendto('ready'.encode('utf-8'), addr)
                for i in range(int(num_of_times)):
                    sync_clock()
                print('Done!')
            else:
                server_socket.sendto('Hello World!'.encode('utf-8'), addr)
    except socket.error as e:
        print('Error while handling requests: ' + str(e))
        server_socket.close()
        sys.exit(-1)


def sync_clock():
    addr = sync_packet()
    delay_packet(addr)
    recv()


def sync_packet():
    t2, (t1, addr) = recv()
    send(t2, addr)
    return addr


def delay_packet(addr):
    recv()
    send(get_time(), addr)


def recv():
    try:
        request = server_socket.recvfrom(4096)
        t = get_time()
        return t, request
    except socket.error as e:
        print('Error while receiving request: ' + str(e))
        server_socket.close()
        sys.exit(-1)


def send(data, addr):
    try:
        server_socket.sendto(str(data).encode('utf-8'), addr)
    except socket.error as e:
        print('Error while sending request: ' + str(e))
        print('Tried to send: ' + data)
        server_socket.close()
        sys.exit(-1)


def get_time():
    return time.time()


if __name__ == '__main__':
    main()
