import serial
import argparse


def initialize_serial(port, baud_rate):
    global arduino
    arduino = serial.Serial(port, baud_rate)

    while(arduino.read() != b'\xFF'):
        print("Initialization byte does not equal 0xFF")
    print("Communication established with arduino")


def read_byte(args):
    initialize_serial(args.p, args.b)
    address = int(args.address, 16)  # converts hex to int

    print(do_read(address))


def do_read(address):
    arduino.write(b'r\n')
    arduino.write((str(address)+'\n').encode('ascii'))
    return int(arduino.readline())


def write_byte(args):
    initialize_serial(args.p, args.b)
    address = int(args.address, 16)  # converts hex to int
    do_write(address, int(args.data))
    print("Write complete")


def do_write(address, data):
    arduino.write(b'w\n')
    arduino.write((str(address)+'\n'+str(data)+'\n').encode('ascii'))
    arduino.readline()


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    parser.add_argument('-b', default=115200, type=int,
                        help='serial baud rate (default:115200)')
    parser.add_argument('-p', default="/dev/ttyUSB0",
                        help='serial port (default: /dev/ttyUSB0)')

    parser_read_byte = subparsers.add_parser('read_byte')
    parser_read_byte.add_argument(
        'address', help='reads a byte at this hex address')
    parser_read_byte.set_defaults(func=read_byte)

    parser_write_byte = subparsers.add_parser('write_byte')
    parser_write_byte.add_argument(
        'address', help='writes to this hex address')
    parser_write_byte.add_argument('data', help='writes this integer')
    parser_write_byte.set_defaults(func=write_byte)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
