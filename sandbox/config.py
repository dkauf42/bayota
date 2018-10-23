import os

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(PROJECT_DIR, 'output/')


# Check if running on AWS
import requests
inaws = False
s3 = None
_S3BUCKET = ''
try:
    resp = requests.get('http://169.254.169.254', timeout=0.001)
    print('AWS url response: %s' % resp)
    if 'ami' in resp:
        print('In AWS')
        inaws = True
    else:
        raise ConnectionError

    import s3fs
    s3 = s3fs.core.S3FileSystem(anon=False)
    _S3BUCKET = 's3://modeling-data.chesapeakebay.net/'
except:
    print('Not In AWS')
