import socket

HOST = "127.0.0.1"
PORT = 6000

def calculate_parity(text: str) -> str:
    total_ones = 0
    for char in text:
        total_ones += bin(ord(char)).count("1")
    return "0" if total_ones % 2 == 0 else "1"


def calculate_2d_parity(text: str):
    padded = text.ljust(64, "#")
    matrix = [padded[i:i + 8] for i in range(0, 64, 8)]

    row_parity = ""
    col_parity = ""

    for row in matrix:
        ones = sum(bin(ord(c)).count("1") for c in row)
        row_parity += "0" if ones % 2 == 0 else "1"

    for col in range(8):
        chars = [matrix[row][col] for row in range(8)]
        ones = sum(bin(ord(c)).count("1") for c in chars)
        col_parity += "0" if ones % 2 == 0 else "1"

    return row_parity + col_parity


def crc16(text: str):
    poly = 0x1021
    reg = 0xFFFF

    for char in text:
        reg ^= (ord(char) << 8)
        for _ in range(8):
            if reg & 0x8000:
                reg = (reg << 1) ^ poly
            else:
                reg <<= 1
            reg &= 0xFFFF

    return format(reg, "04X")



def hamming_check(encoded: str):

    if len(encoded) % 7 != 0:
        return "CORRUPTED"

    blocks = [encoded[i:i+7] for i in range(0, len(encoded), 7)]

    error_found = False

    for block in blocks:
        p1 = int(block[0])
        p2 = int(block[1])
        d1 = int(block[2])
        p4 = int(block[3])
        d2 = int(block[4])
        d3 = int(block[5])
        d4 = int(block[6])

        c1 = (d1 ^ d2 ^ d4) % 2
        c2 = (d1 ^ d3 ^ d4) % 2
        c4 = (d2 ^ d3 ^ d4) % 2

        if c1 != p1 or c2 != p2 or c4 != p4:
            error_found = True

    return "CORRUPTED" if error_found else "OK"



def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen()
        print("Client2 is Ready. Waiting for packet from Server...\n")

        while True:
            conn, addr = server.accept()
            with conn:
                packet = conn.recv(4096).decode("utf-8")
                if not packet:
                    continue

                print(f"The packet coming from Server: {packet}")

                try:
                    incoming_data, method, incoming_control = packet.split("|")
                except:
                    print("The packet format is damaged!\n")
                    continue


                if method == "PARITY":
                    computed = calculate_parity(incoming_data)

                elif method == "2DPARITY":
                    computed = calculate_2d_parity(incoming_data)

                elif method == "CRC16":
                    computed = crc16(incoming_data)

                elif method == "HAMMING":
                    result = hamming_check(incoming_control)
                    computed = incoming_control
                    status = "DATA CORRUPTED" if result == "CORRUPTED" else "DATA CORRECT"

                else:
                    computed = "0"

                if method != "HAMMING":
                    if computed == incoming_control:
                        status = "DATA CORRECT"
                    else:
                        status = "DATA CORRUPTED"

                print("Received Data:        ", incoming_data)
                print("Method:               ", method)
                print("Sent Check Bits:      ", incoming_control)
                print("Computed Check Bits:  ", computed)
                print("Status:               ", status)
                print("-" * 40)


if __name__ == "__main__":
    main()
