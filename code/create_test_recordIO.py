#! /usr/bin/env python3

from util.load_csv import parse as load
from util.band import band as band
import pydicom
import os
import boto3
s3 = boto3.client('s3')
import io
import mxnet.recordio as recordio
import tempfile
from numpy.random import choice

src_bucket=os.environ.get("SRC_BUCKET","jmc-rsna-ih")
dst_bucket=os.environ.get("DST_BUCKET","jmc-rsna-ih")
count=int(os.environ.get("JOB_ARRAY_COUNT",2))
index=int(os.environ.get("AWS_BATCH_JOB_ARRAY_INDEX",0))

csv_file=tempfile.NamedTemporaryFile()
rec_file=tempfile.NamedTemporaryFile()

print("downloading csv file")
s3.download_file(
    src_bucket,
    "stage_1_sample_submission.csv",
    csv_file.name
)

print("parsing csv file")
df=load(csv_file.name)
csv_file.close()

record=recordio.MXRecordIO(rec_file.name, 'w')

for i,row in df.iterrows() :
    if i%count==index:
        data=io.BytesIO()
        print("Downloading "+row.ID)
        result=s3.download_fileobj(
            src_bucket,
            "stage_1_test_images/"+row.ID+".dcm",
            data
        )
        data.seek(0)
        print("processing dicom image")
        ds = pydicom.dcmread(data)
        img=band(ds).transpose()
        header=recordio.IRHeader(0,list(map(ord,list(row.ID))),0,0)
        packed_s = recordio.pack_img(header, img,quality=95,img_fmt=".jpg")
        record.write(packed_s)
        
record.close()
print("uploading files")

s3.upload_file(rec_file.name,dst_bucket,"stage_1_rec/test/"+str(index)+".rec")

rec_file.close()
