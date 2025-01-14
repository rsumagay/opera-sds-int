import subprocess
import boto3
import os
from google.cloud import storage
import shutil
import h5py
import time
from botocore import UNSIGNED
from botocore.client import Config
import multiprocessing as mp





def upload_blob(bucket_name, source_file_name, destination_blob_name):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name,timeout=None)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name,timeout=None)

def processCSLC(s3key,gcskey):
    filename = s3key.split('/')[-1]
    if os.path.exists(f'./temp_{filename}/'):
        shutil.rmtree(f'./temp_{filename}/')
    os.mkdir(f'./temp_{filename}/')

    #Download CSLC file
    #print('Downloading CSLC File')
    s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED))
    bucket = 'opera-int-rs-fwd' #'opera-pst-rs-pop1'
    filename = s3key.split('/')[-1]
    filepath = f'./temp_{filename}/'+filename
    s3.download_file(bucket, s3key, filepath)

    #Change compression to DEFLATE
    #print('Converting amplitude to COG')
    outfile = f'./temp_{filename}/cog.tif'
    f = h5py.File(filepath, 'r')
    pass_direction = f['identification']['orbit_pass_direction'][()]
    if pass_direction == b'Ascending':
        pass_d = 'A'
    elif pass_direction == b'Descending':
        pass_d = 'D'
    else:
        pass_d = 'N'
    cslc_h5_amp = f'DERIVED_SUBDATASET:AMPLITUDE:NETCDF:"{filepath}":/data/VV'
    gdal_cmd = f'gdal_translate -of COG -co COMPRESS=DEFLATE -co RESAMPLING=AVERAGE {cslc_h5_amp} {outfile}'
    subprocess.run(gdal_cmd,shell=True,stdout=subprocess.DEVNULL)

    #Upload to GCS bucket
    #print('Uploading to GCS Bucket')
    gcsbucket = "opera-bucket-cslc"
    gcskey = gcskey.split('.tif')[0] + f'_{pass_d}.tif'
    upload_blob(gcsbucket,outfile,gcskey)
    shutil.rmtree(f'temp_{filename}')

def run_rtc_transfer(keydict):
    try:
        start_time = time.time()
        s3key = keydict['s3key']
        gcskey = keydict['gcsKey']
        processCSLC(s3key,gcskey)
        print(f'[{time.time() - start_time}] Uploaded to: {gcskey}')
    except Exception as e: 
        print(f'Failed on {s3key}, error: {e}')

if __name__ == '__main__':
    os.environ["GCLOUD_PROJECT"] = "opera-one"
    s3_prefix = 'products/CSLC_S1/' #'products/int_fwd_r2/2023-05-04_globalrun_2021-04-11_to_2021-04-22/CSLC_S1/'
    gcs_prefix = 'products/2023-06-26_historcal_2021-04-01_to_2021-04-19/'
    s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED))
    paginator = s3.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket='opera-int-rs-fwd', Prefix=s3_prefix, Delimiter='/')
    keyList = []
    for page in pages:
        #pprint(page)
        for obj in page['CommonPrefixes']:
            path = obj.get('Prefix')
            fname = path.split('/')[-2]+'.h5'
            keyList.append(path+fname)
    print(f'{len(keyList)} s3 keys found')

    storage_client = storage.Client()
    blobs = storage_client.list_blobs("opera-bucket-cslc", prefix=gcs_prefix)
    gcsKeys = []
    for blob in blobs:
        gcsKeys.append(blob.name.split('.tif')[0][:-2]+'.tif')
    print(f'{len(gcsKeys)} existing gcs keys found')

    keyPairs = []
    for key in keyList:
        fname = key.split('/')[-1]
        gcsKey = gcs_prefix+fname.split('.h5')[0]+'.tif'
        if gcsKey not in gcsKeys:
            keydict = {'s3key':key,'gcsKey':gcsKey}
            keyPairs.append(keydict)
    print(f'{len(keyPairs)} key pairs identified')

    pool = mp.Pool(4)
    pool.map(run_rtc_transfer,keyPairs)
    pool.close()
