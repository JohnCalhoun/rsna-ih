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

rec_file_all_train=tempfile.NamedTemporaryFile()
rec_file_all_test=tempfile.NamedTemporaryFile()
rec_file_any_train=tempfile.NamedTemporaryFile()
rec_file_any_test=tempfile.NamedTemporaryFile()

print("downloading csv file")
s3.download_file(
    src_bucket,
    "stage_1_train.csv",
    csv_file.name
)

print("parsing csv file")
df=load(csv_file.name)
csv_file.close()

record_all_train = recordio.MXRecordIO(rec_file_all_train.name, 'w')
record_all_test = recordio.MXRecordIO(rec_file_all_test.name, 'w')
record_any_train = recordio.MXRecordIO(rec_file_any_train.name, 'w')
record_any_test = recordio.MXRecordIO(rec_file_any_test.name, 'w')

for i,row in df.iterrows() :
    if i%count==index:
        data=io.BytesIO()
        print("Downloading "+row.ID)
        result=s3.download_fileobj(
            src_bucket,
            "stage_1_train_images/"+row.ID+".dcm",
            data
        )
        data.seek(0)
        print("processing dicom image")
        ds = pydicom.dcmread(data)
        img=band(ds).transpose()
        header=recordio.IRHeader(0,row.tolist()[1:],0,0)
        packed_s = recordio.pack_img(header, img,quality=95,img_fmt=".jpg")
       
        rec=choice([record_all_train,record_all_test],1,p=[.8,.2])[0]
        rec.write(packed_s)
        if(row[-1]):
            rec=choice([record_any_train,record_any_test],1,p=[.8,.2])[0]
            rec.write(packed_s)

record_all_train.close()
record_all_test.close()
record_any_train.close()
record_any_test.close()
print("uploading files")

s3.upload_file(rec_file_all_train.name,dst_bucket,"stage_1_rec/all/train/"+str(index)+".rec")
s3.upload_file(rec_file_all_test.name,dst_bucket,"stage_1_rec/all/test/"+str(index)+".rec")
s3.upload_file(rec_file_any_train.name,dst_bucket,"stage_1_rec/any/train/"+str(index)+".rec")
s3.upload_file(rec_file_any_test.name,dst_bucket,"stage_1_rec/any/test/"+str(index)+".rec")

rec_file_all_train.close()
rec_file_all_test.close()
rec_file_any_train.close()
rec_file_any_test.close()


