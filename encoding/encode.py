import re
import socket

test_str = 'hello world!'
# Ascii representation of 'hello world!'
test_binstr = ''.join('''
01101000
01100101
01101100
01101100
01101111
00100000
01110111
01101111
01110010
01101100
01100100
00100001'''.split())
# Encoded ascii representation of 'hello world!'
test_encoded = ''.join('''
10010110011010010110100110011001
10010110011010011001011010010110
10010110011010010110011010011001
10010110011010010110011010011001
10010110011010010110011001100110
10011001011010011001100110011001
10010110011001101001011001100110
10010110011010010110011001100110
10010110011001101001100101101001
10010110011010010110011010011001
10010110011010011001011010011001
10011001011010011001100110010110'''.split())

def mencode_string_to_binstr(chars):
    # Convert the characters to integers
    bytes = map(ord, chars)
    # Encode the bytes, then join them together
    return ''.join(map(mencode_byte_to_binstr, bytes))

def mencode_byte_to_binstr(byte):
    # Convert the byte to an 8 character binary string representation
    binstr_in = "{0:08b}".format(byte&0xFF)
    # Convert 0's to 1001 and 1's to 0110
    return ''.join(['0110' if x=='1' else '1001' for x in binstr_in])

def mdecode_from_binstr(binstr):
    # Ensure a valid length input string
    assert len(binstr)%4 == 0, 'Improper length string'
    # Split into 4 character chunks
    ebits = re.findall('....',binstr)
    # Decode the bits and put them back into a single string
    decode_dict = {'0110':'1', '1001':'0'}
    return ''.join([decode_dict[x] for x in ebits])

def self_test():
    # Test single byte encoding
    bytes = map(ord, test_str)
    result = ''.join(map(mencode_byte_to_binstr, bytes))
    assert result == test_encoded, 'byte encode failure'
    # Test full string encoding
    result = mencode_string_to_binstr(test_str)
    assert result == test_encoded, 'string encode failure'
    # Test the decoding
    result = mdecode_from_binstr(test_encoded)
    assert result == test_binstr, 'decode failure'

# Lookup table of 256 32-bit values (unencoded byte -> 4 encoded bytes)
encode_lut = [int(mencode_byte_to_binstr(x),2) for x in range(256)]

if __name__ == "__main__":
    self_test()

    # Print the lut
    #print ['0x%08X'%x for x in encode_lut]

    #print '0x%08X'%encode_lut[ord('h')]
    #print '0x%08X'%socket.htonl(encode_lut[ord('h')])

    # Print the lut (big endian version)
    print ', '.join(['0x%08X'%socket.htonl(x) for x in encode_lut])
