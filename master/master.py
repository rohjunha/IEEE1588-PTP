import socket
import sys
import time

server_socket = None
# ADDRESS = '10.0.0.19'
# ADDRESS = '192.168.137.2'
ADDRESS = '127.0.0.1'
PORT = 2468
NUM_OF_TIMES = 1000

OFFSETS = []
DELAYS = []


def main():
    try:
        global server_socket
        print('Creating socket...')
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    except socket.error as e:
        print('Error creating socket: {}'.format(e))
        server_socket.close()
        sys.exit(-1)

    try:
        print('Connecting to socket... {}:{}'.format(ADDRESS, PORT))
        server_socket.connect((ADDRESS, PORT))
    except socket.error as e:
        print('Error connecting to socket: {}'.format(e))
        server_socket.close()
        sys.exit(-1)

    sync_clock()


def sync_clock():
    print('Syncing time with {}:{}'.format(ADDRESS, PORT))
    send('sync')
    t, resp = recv()
    send(str(NUM_OF_TIMES))

    t, resp = recv()
    resp = resp.decode()

    if resp == 'ready':
        time.sleep(1)  # to allow for server to get ready
        for i in range(NUM_OF_TIMES):
            ms_diff = sync_packet()
            sm_diff = delay_packet()

            offset = (ms_diff - sm_diff) / 2
            delay = (ms_diff + sm_diff) / 2

            OFFSETS.append(offset)
            DELAYS.append(delay)

            send('next')

        print('avg offset: {}'.format(sum(OFFSETS) * 1e9 / len(OFFSETS)))
        print('avg delay : {}'.format(sum(DELAYS) * 1e9 / len(DELAYS)))
        print('min offset: {}'.format(min(OFFSETS) * 1e9 / len(OFFSETS)))
        print('max offset: {}'.format(max(OFFSETS) * 1e9 / len(OFFSETS)))
    else:
        print('Error syncing times, received: {}'.format(resp))


def sync_packet():
    t1 = send('sync_packet')
    t, t2 = recv()
    return float(t2) - float(t1)


def delay_packet():
    send('delay_packet')
    t4, t3 = recv()
    return float(t4) - float(t3)


def recv():
    try:
        msg = server_socket.recv(4096)
        t = get_time()
        return t, msg
    except socket.error as e:
        print('Error while receiving request: {}'.format(e))
        server_socket.close()
        sys.exit(-1)


def send(data):
    try:
        server_socket.sendall(str(data).encode('utf-8'))
        t = get_time()
        return t
    except socket.error as e:
        print('Error while sending request: {}'.format(e))
        print('Tried to send: {}'.format(data))
        server_socket.close()
        sys.exit(-1)


def get_time():
    return time.time()


if __name__ == '__main__':
    main()
