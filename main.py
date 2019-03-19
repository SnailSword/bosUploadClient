#!/usr/bin/env python
#coding=utf-8



import os
import bos_sample_conf 
from baidubce import exception
from baidubce.services import bos
from baidubce.services.bos import canned_acl
from baidubce.services.bos.bos_client import BosClient
import re
import ConfigParser

config = ConfigParser.RawConfigParser()
config.read('config.cfg')

class Bd_Bos_Upload:
    def __init__(self,bucket_name,file_name,download,withRoot,upload_class=1):
        self.bos_client = BosClient(bos_sample_conf.config)
        self.bucket_name = bucket_name
        self.file_name = file_name
        self.user_headers = {'Content-Disposition': 'attachement; filename=' + file_name}
        self.download = download
        self.withRoot = withRoot
        if upload_class == 1:
            self._part_upload()
        if upload_class == 0:
            self._small_upload()
    
    
    
    #small file upload
    def _small_upload(self):
        data = open(self.file_name, 'rb')
        print('Start upload file: ', self.file_name)
        if self.download:
            user_headers = self.user_headers
        else:
            user_headers = None
        if self.withRoot:
            file_path = self.file_name
        else:
            file_path = _pickPath(self.file_name)
        print(self.bucket_name, file_path, self.file_name)
        self.bos_client.put_object_from_file(self.bucket_name, file_path, self.file_name, user_headers=user_headers)
        print('Upload Successfully!')

    #part upload , file size > 5GB  
    def _part_upload(self):
        upload_id = self.bos_client.initiate_multipart_upload(self.bucket_name, self.file_name).upload_id
        left_size = os.path.getsize(self.file_name)

        offset = 0

        part_number = 1
        part_list = []
        print('Start upload file: ',self.file_name)
        while left_size > 0:

            part_size = 5 * 1024 * 1024
            if left_size < part_size:
                part_size = left_size

            response = self.bos_client.upload_part_from_file(
                self.bucket_name, self.file_name, upload_id, part_number, part_size, self.file_name, offset)


            left_size -= part_size
            offset += part_size
            part_list.append({
                "partNumber": part_number,
                "eTag": response.metadata.etag
            })
            print('Upload Successfully: Part',part_number)
            part_number += 1


        self.bos_client.complete_multipart_upload(self.bucket_name, self.object_key, upload_id, part_list)
        print('Upload Successfully!')

def _pickPath(path):
    pattern = re.compile(r'\/.*')
    match = pattern.search(path)
    if match:
        res = match.group()
        return res[1:];

bucketName = config.get('BosFile', 'bucket')
download = config.getboolean('BosFile', 'download')
withRoot = config.getboolean('BosFile', 'withRoot')
def _folder_uploader(rootDir):
    for lists in os.listdir(rootDir):
        path = os.path.join(rootDir, lists)

        if os.path.isdir(path):
            _folder_uploader(path)
        else:
            Bd_Bos_Upload(bucketName, path, download, withRoot, 0)

if __name__ == "__main__":
    floderName = config.get('BosFile', 'folder')
    withRoot = config.getboolean('BosFile', 'withRoot')
    _folder_uploader(floderName)