import zlib

def compress():
    with open('after.sl2', 'rb') as f:
        data = f.read()

    compressed_data = zlib.compress(data, 9)

    with open('output.bin', 'wb') as f:
        f.write(compressed_data)

def decompress():
    with open('output.bin', 'rb') as f:
        data = f.read()

    decompressed_data = zlib.decompress(data)

    with open('converted.sl2', 'wb') as f:
        f.write(decompressed_data)

decompress()