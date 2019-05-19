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


def verify_byte(address, data):
    return (do_read(address) == data)


def write_file(args):
    initialize_serial(args.p, args.b)
    address = int(args.offset_address, 16)
    with open(args.file, 'rb') as f:
        f.seek(int(args.offset_file, 16), 1)
        byte = f.read(1)
        while(byte != b''):
            if(address % 64 == 0):
                print('Writing to address:' + str(hex(address)))
            do_write(address, int.from_bytes(byte, byteorder='little'))

            address += 1
            byte = f.read(1)
    print('File writing complete')


def verify_file(args):
    initialize_serial(args.p, args.b)
    address = int(args.offset_address, 16)
    with open(args.file, 'rb') as f:
        f.seek(int(args.offset_file, 16), 1)
        byte = f.read(1)
        while(byte != b''):
            if(address % 64 == 0):
                print('Verifying address: ' + str(hex(address)))
            while(not verify_byte(address, int.from_bytes(byte, byteorder='little'))):
                print('Byte at '+str(hex(address))+' not ' +
                      str(int.from_bytes(byte, 'little')) + ', retrying')
                do_write(address, int.from_bytes(byte, byteorder='little'))

            address += 1
            byte = f.read(1)
    print('File verification complete')


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

    parser_write_file = subparsers.add_parser('write_file')
    parser_write_file.add_argument('file', help='writes this file')
    parser_write_file.set_defaults(func=write_file)
    parser_write_file.add_argument(
        '-offset_address', help='starts writing to this sram address(default: 0x0000)', default='0x0000')
    parser_write_file.add_argument(
        '-offset_file', help='writes starting from this address from file(default:0x0000)', default='0x0000')

    parser_verify_file = subparsers.add_parser('verify_file')
    parser_verify_file.add_argument('file', help='verifies this file')
    parser_verify_file.add_argument(
        '-offset_address', help='starts verifying at this sram address(default: 0x0000)', default='0x0000')
    parser_verify_file.add_argument(
        '-offset_file', help='verifies starting from this address from file(default:0x0000)', default='0x0000')
    parser_verify_file.set_defaults(func=verify_file)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
