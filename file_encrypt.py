from Crypto.Cipher import DES3
import os


def encrypt_file(in_filename, chunk_size, key, iv):
    des3 = DES3.new(key, DES3.MODE_CFB, iv)
    fname = os.path.basename(in_filename)
    out_filename = os.path.dirname(in_filename) + '/' +  fname.split('.')[0] +  '.enc'
    try:
        with open(in_filename, 'r') as in_file:
            with open(out_filename, 'w') as out_file:
                while True:
                    chunk = in_file.read(chunk_size)
                    if len(chunk) == 0:
                        break
                    elif len(chunk) % 16 != 0:
                        chunk += ' ' * (16 - len(chunk) % 16)
                    out_file.write(des3.encrypt(chunk))
        return out_filename 
    except Exception as e:
        print 'File could not be encrypted', e
        return None
