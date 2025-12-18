import socket
import random

HOST = "127.0.0.1"
PORT_FROM_CLIENT1 = 5000
HOST_TO_CLIENT2 = "127.0.0.1"
PORT_TO_CLIENT2 = 6000




def bit_flip(text: str) -> str:
    """Flips a character's LSB byte."""
    if not text:
        return text
    idx = random.randrange(len(text))
    flipped_char = chr(ord(text[idx]) ^ 1)      # LSB flip
    return text[:idx] + flipped_char + text[idx+1:]


def char_substitution(text: str) -> str:
    """Chooses a random character from text, puts a new letter from A-Z."""
    if not text:
        return text
    idx = random.randrange(len(text))
    random_char = chr(random.randint(65, 90))   # Random A–Z
    return text[:idx] + random_char + text[idx+1:]


def char_deletion(text: str) -> str:
    """Erases a random character from text."""
    if len(text) < 2:
        return text
    idx = random.randrange(len(text))
    return text[:idx] + text[idx+1:]


def char_insertion(text: str) -> str:
    """
    Adds a new character to text in a random location.
    Important:Does not erase anythig, just dislocates.
    """
    if not text:

        return chr(random.randint(97, 122))


    idx = random.randint(0, len(text))
    random_char = chr(random.randint(97, 122))

    return text[:idx] + random_char + text[idx:]


def char_swap(text: str) -> str:
    """Swaps two characters next to each other."""
    if len(text) < 2:
        return text
    idx = random.randrange(len(text) - 1)
    return text[:idx] + text[idx+1] + text[idx] + text[idx+2:]


def burst_error(text: str) -> str:
    """Distorts a block that has 3-8 characters with ASCII characters."""
    if len(text) < 4:
        return text
    start = random.randrange(len(text) - 3)
    length = random.randint(3, 8)
    end = min(start + length, len(text))
    corrupted = ''.join(chr(random.randint(33, 126)) for _ in range(end - start))
    return text[:start] + corrupted + text[end:]


def multiple_bit_flips(text: str) -> str:
    """Flips multiple bits of LSB bytes of random characters from the text."""
    if not text:
        return text
    flips = random.randint(2, 5)
    text_list = list(text)
    for _ in range(flips):
        idx = random.randrange(len(text_list))
        text_list[idx] = chr(ord(text_list[idx]) ^ 1)
    return "".join(text_list)



def apply_error(choice: str, text: str) -> str:
    """
    Calls the corresponding error function based on the menu selection (1–8).
    """
    if choice == "1":
        return bit_flip(text)
    elif choice == "2":
        return char_substitution(text)
    elif choice == "3":
        return char_deletion(text)
    elif choice == "4":
        return char_insertion(text)
    elif choice == "5":
        return char_swap(text)
    elif choice == "6":
        return burst_error(text)
    elif choice == "7":
        return multiple_bit_flips(text)
    elif choice == "8":
        return text   # No error
    else:
        return text




def main():
    print("\n--- ERROR INJECTION MENU ---")
    print("1) Bit Flip")
    print("2) Character Substitution")
    print("3) Character Deletion")
    print("4) Insert Random Character")
    print("5) Swap Adjacent Characters")
    print("6) Burst Error (3–8 chars)")
    print("7) Multiple Bit Flips")
    print("8) No Error (Forward Only)")
    error_choice = input("Choose error method (1-8): ").strip()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT_FROM_CLIENT1))
        server.listen()
        print("\nServer is open. Waiting for Client1...\n")

        while True:
            conn, addr = server.accept()
            with conn:
                data = conn.recv(4096).decode("utf-8")

                if not data:
                    continue

                print(f"Packet from Client1: {data}")

                try:
                    text, method, control = data.split("|")
                except ValueError:
                    print("❌ Packet format has errors!")
                    continue

                corrupted_text = apply_error(error_choice, text)
                new_packet = f"{corrupted_text}|{method}|{control}"

                print("💥 Corrupted Packet:", new_packet)
                print("➡ Sending to Client2...\n")

                # Forward to Client2
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as to_client2:
                    to_client2.connect((HOST_TO_CLIENT2, PORT_TO_CLIENT2))
                    to_client2.sendall(new_packet.encode("utf-8"))


if __name__ == "__main__":
    main()
