#! /usr/bin/env python3

import pydicom
import numpy as np
from PIL import Image
from pydicom.data import get_testdata_files

def single_band(img,start,end,name):
    out=np.copy(img)
    out=(out-start)/(end-start)
    out[out>1]=0
    out[out<0]=0
    return out.reshape((1,512,512))

def band(ds):
    img=ds.pixel_array
    img=img * ds.RescaleSlope + ds.RescaleIntercept
    
    return np.concatenate((
        single_band(img,20,45,"tissue"),
        single_band(img,45,90,"blood"),
        single_band(img,100,1000,"bone")
    ))

if __name__ == "__main__":
    ds = pydicom.dcmread("./test/ID_test.dcm")
    out=band(ds)
    out=(out*256).astype(np.uint8)
    print(out.transpose().shape)
    im = Image.fromarray(out.transpose())
    im.save('./tmp/out.png')

