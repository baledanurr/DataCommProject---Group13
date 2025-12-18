import socket

HOST = "127.0.0.1"
PORT = 5000


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
        column_chars = [matrix[row][col] for row in range(8)]
        ones = sum(bin(ord(c)).count("1") for c in column_chars)
        col_parity += "0" if ones % 2 == 0 else "1"

    control_info = row_parity + col_parity
    return control_info

def crc16(data: str):
    poly = 0x1021
    reg = 0xFFFF

    for char in data:
        reg ^= (ord(char) << 8)
        for _ in range(8):
            if reg & 0x8000:
                reg = (reg << 1) ^ poly
            else:
                reg <<= 1
            reg &= 0xFFFF

    return format(reg, '04X')


def hamming_encode(text: str):
    encoded = ""
    for ch in text:
        b = format(ord(ch), "08b")

        d1 = int(b[0])
        d2 = int(b[1])
        d3 = int(b[2])
        d4 = int(b[3])

        # parity bits
        p1 = (d1 ^ d2 ^ d4) % 2
        p2 = (d1 ^ d3 ^ d4) % 2
        p4 = (d2 ^ d3 ^ d4) % 2

        encoded_block = f"{p1}{p2}{d1}{p4}{d2}{d3}{d4}"
        encoded += encoded_block

    return encoded

def build_packet(text: str, method: str) -> str:
    if method == "PARITY":
        control = calculate_parity(text)
    elif method == "2DPARITY":
        control = calculate_2d_parity(text)
    elif method == "CRC16":
        control = crc16(text)
    elif method == "HAMMING":
        control = hamming_encode(text)
    else:
        control = "0"

    return f"{text}|{method}|{control}"


def main():
    print("\n--- ERROR DETECTION METHOD MENU ---")
    print("1) Parity Bit")
    print("2) 2D Parity")
    print("3) CRC-16")
    print("4) Hamming Code")
    print("5) Internet Checksum (soon)")

    choice = input("Choose method (1-5): ")

    methods = {
        "1": "PARITY",
        "2": "2DPARITY",
        "3": "CRC16",
        "4": "HAMMING",
        "5": "CHECKSUM"
    }

    method = methods.get(choice, "PARITY")

    text = input("Write the text you will send: ")

    packet = build_packet(text, method)
    print("The package that will be sent:", packet)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(packet.encode("utf-8"))


if __name__ == "__main__":
    main()
