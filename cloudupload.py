import logging
import math
import time
import requests
import mimetypes
from datetime import datetime, date
from multiprocessing import Pool
import os
import json
import argparse
from filechunkio import FileChunkIO
from fileupload.client import uploadfile
import sys
from file_encrypt import encrypt_file
from Crypto import Random
from Crypto.PublicKey import RSA
from fileupload import config
import key_value_db as pickle


host = uploadfile()
random_generator = Random.new().read
key = RSA.generate(1024, random_generator)
public_key = 'QZNy\x13m4-\xcc\xae@\xe4\x01$\x95\x1f'

processeddb = os.path.dirname(os.path.realpath(__file__)) + '/' + config.get( 'pickle', 'pickledb')
db     = pickle.set_db(processeddb)
gfilename = ' ' 

uploadstat = {}
logger = logging.getLogger("File-Upload-Chunks")
parser = argparse.ArgumentParser(description="Transfer large files to in chinks to FTP",
        prog="File-Upload-Using-Chinks")
parser.add_argument("src", type=file, help="The file to transfer")
parser.add_argument("ContainerName", help="The name of the folder where this should reside")
parser.add_argument("-np", "--num-processes", help="Number of processors to use",
        type=int, default=2)
parser.add_argument("-s", "--split", help="Split size, in Mb", type=int, default=50)
parser.add_argument("-t", "--max-tries", help="Max allowed retries for http timeout", type=int, default=5)
parser.add_argument("-v", "--verbose", help="Be more verbose", default=False, action="store_true")
parser.add_argument("-q", "--quiet", help="Be less verbose (for use in cron jobs)", default=False, action="store_true")

def upload_part_from_file(fp, part_num, dest):
    fname = 'part'+ str(part_num)
    dest = dest + '/' + fname
    files = {'file': (fname, fp, 'application/octet-stream')}
    if host.execute('upload-file',dest, files):
        return 1
    else:
        return 0
        

def upload_part(part_num, fname, offset, bytes1, dest, flname, amount_of_retries=10):
    """
    Uploads a part with retries.
    """
    #print 'Now uploading', fname

    def _upload(src, offset, bytes1, part_num, dest, flname, retries_left=amount_of_retries):
        #print 'Started upload', src, offset, bytes1
        try:
            logging.info('Start uploading part #%s ...' % part_num)
            with FileChunkIO(src, 'r', offset=offset, bytes=bytes1) as fp:
                uploadstat[str(part_num)] = 0
                uploadstat[str(part_num)] = upload_part_from_file(fp, part_num, dest)
            #break
        except Exception as exc:
            print 'Exception', exc
            if retries_left:
                _upload(retries_left=retries_left - 1)
            else:
                logging.info('... Failed uploading part #%d' % exc)
                return 0
                
             
            

    _upload(fname, offset, bytes1,part_num, dest, flname,  amount_of_retries )
    return flname + '-' + str(part_num)

def calculate_number_of_chunks(filesize, split_size):
    split_size = split_size*1000000
    bytes_per_chunk = max(int(math.sqrt(5242880) * math.sqrt(split_size)),
        5242880)
    print 'The bytes per chubk is ', bytes_per_chunk
    print 'The number of chunks is ', int(math.ceil(filesize / float(bytes_per_chunk)))
    print 'The file size is' , filesize
    return bytes_per_chunk , int(math.ceil(filesize / float(bytes_per_chunk)))

def callback(x):
    filename, part_num = x.split('-')
    pickle.update_dict_item(db, filename, part_num, 1)
    logging.info('Successfully Uploaded part #%s ' % part_num)


def check_if_uploaded(flname, chunk_num):
    print 'Now checking', flname, 'And', chunk_num
    upload_ind = pickle.get_dict_item(db, flname,str(chunk_num))
    if upload_ind == 1:
        print 'returning false'
        return False
    else:
        print 'returning true'
        return True


def measure_time(starttime, source_size):
    t2 = time.time() - starttime
    s = source_size/1024./1024.
    logging.info("Finished uploading %0.2fM in %0.2fs (%0.2fMBps)" % (s, t2, s/t2))
    
        
def main(src, ContainerName, num_processes=2, split=50, verbose=False, quiet=False, max_tries=5):
    source_size = os.stat(src.name).st_size
    t1 = time.time()
    iv = Random.get_random_bytes(8)
    logger.info("Now starting file encryption. %s" % date.today())
    #fileret = encrypt_file(src.name, 50000, public_key, iv)
    fileret = '/Users/ssinha/Downloads/hindic.enc'
    logger.info("File encryption ended. It took %0.2fs" % (time.time() - t1))
    if verbose:
        logging.info("The encrypted file is %s)" % (fileret))
        
    dest = ContainerName + '/' + os.path.basename(fileret).split('.')[0]
    if source_size  < 5*1024*1024:
        
        src.seek(0)
        files = {'file': (os.path.basename(fileret) , fileret, 'application/octet-stream')}
        if host.execute('upload-file',dest,files):
            measure_time(t1, source_size)
        else:
            logging.info( 'File not loaded successfully, try again later')
        sys.exit(0)
        
    #Calculate the number of chunks and the bytes per chunk
    bytes_per_chunk, chunk_amount = calculate_number_of_chunks(source_size, split)
    if verbose:
        logging.info('The chunking size is %0.2f, and the number of chunks are, %.2f' % ( bytes_per_chunk, chunk_amount ))
    #import ipdb;ipdb.set_trace()
    part_num = 0
    #spawn the worker threads
    pool = Pool(processes=num_processes)
    #set the global file name
    flname = os.path.basename(src.name).split('.')[0]
    previous_attempt = 'N'
    get_previous_dict = pickle.get_dict(db, flname)
    if get_previous_dict is not None:
        previous_attempt = 'Y'
    else:
        #Make sure that the db exists. If not then create it. This is necessary for tracking file progress
        assert( pickle.set_dict_name(db,flname) is True)
    
 

    t2 = time.time()
    if host.execute('create-container', dest ):
        for i in range(chunk_amount):
            offset = i * bytes_per_chunk
            remaining_bytes = source_size - offset
            bytes1 = min([bytes_per_chunk, remaining_bytes])
            part_num = i + 1
            if previous_attempt == 'Y':
                if check_if_uploaded(flname , part_num):
                    print 'this part need to be loaded', part_num
                    pool.apply_async(upload_part, (part_num, fileret, offset, bytes1, dest, flname), callback=callback)
            else:
                pool.apply_async(upload_part, (part_num, fileret, offset, bytes1, dest, flname), callback=callback)

        pool.close()
        pool.join()
        for worker in pool._pool:
            assert not worker.is_alive()
        logger.info("File upload ended. It took %0.2fs" % (time.time() - t2))
        #Remove the pickleDB.No need to keep trck of the segments since all of them loaded successfully
        pickle.remove_dict(db, flname)
##        if len(uploadstat) > 1:
##            if 0 not in uploadstat :
##                #print 'File upload complete, Now starting file combine'
##                urlc = url + 'fileupld/' + 'combine/'
##                r = requests.post(urlc, data = {'filename': filenames, 'filesize': source_size })
##                m = json.loads(r.content)
##                if m.get('status', ' ') == 'Success':
##                    measure_time(t1, source_size)
##                    return 0
##            else:
##                print 'File upload is incomplete'
##                return 1

if __name__ == "__main__":
    fh = logging.FileHandler('oraclefile.log')
    logging.basicConfig(level=logging.INFO)
    args = parser.parse_args()
    arg_dict = vars(args)
    if arg_dict['quiet'] == True:
        logger.setLevel(logging.WARNING)
    if arg_dict['verbose'] == True:
        logger.setLevel(logging.DEBUG)
    logger.debug("CLI args: %s" % args)
    main(**arg_dict)
