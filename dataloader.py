import six
import cv2
import lmdb
import torch
import jpegio
import tempfile
import numpy as np
import pickle

from pathlib import Path

import PIL
from PIL import Image

from torch.utils.data import Dataset
from albumentations.pytorch import ToTensorV2
import torchvision

from typing import Union, Tuple, Dict, Any

class DocTamperDataset(Dataset):
    '''
    A basic dataloader of the inference mode

    roots: path of the LMDB file
    minq : min random compression factor, choiced from (75, 80, 85, 90)
    max_readers : max_readers of the LMDB loader
    '''
    def __init__(self, roots, minq=75, max_nums = None, max_readers=64):
        self.envs = lmdb.open(roots,max_readers=max_readers,readonly=True,lock=False,readahead=False,meminit=False)
        with self.envs.begin(write=False) as txn:
            self.nSamples = int(txn.get('num-samples'.encode('utf-8')))

        if max_nums is None:
            self.max_nums=self.nSamples
        self.max_nums=min(max_nums,self.nSamples)

        self.minq = minq # Q
        with open('qt_table.pk','rb') as fpk:
            pks = pickle.load(fpk)
        self.pks = {}
        for k,v in pks.items():
            self.pks[k] = torch.LongTensor(v)
        with open('pks/'+roots+'_%d.pk'%minq,'rb') as f: # random compression factors with the same random seed
            self.record = pickle.load(f)
        self.totsr = ToTensorV2()
        self.toctsr =torchvision.transforms.Compose([torchvision.transforms.ToTensor(),torchvision.transforms.Normalize(mean=(0.485, 0.455, 0.406), std=(0.229, 0.224, 0.225))])

    def __len__(self):
        return self.max_nums

    def __getitem__(self, index):
        with self.envs.begin(write=False) as txn:
            img_key = 'image-%09d' % index
            imgbuf = txn.get(img_key.encode('utf-8'))
            buf = six.BytesIO()
            buf.write(imgbuf)
            buf.seek(0)
            im = Image.open(buf)
            lbl_key = 'label-%09d' % index
            lblbuf = txn.get(lbl_key.encode('utf-8'))
            mask = (cv2.imdecode(np.frombuffer(lblbuf,dtype=np.uint8),0)!=0).astype(np.uint8)
            record = self.record[index]
            choicei = len(record)-1
            q = int(record[-1])
            if True:
                use_qtb = self.pks[q]
                if choicei>1:
                    q2 = int(record[-3])
                    use_qtb2 = self.pks[q2]
                if choicei>0:
                    q1 = int(record[-2])
                    use_qtb1 = self.pks[q1]
            mask = self.totsr(image=mask.copy())['image']
            with tempfile.NamedTemporaryFile(delete=True) as tmp:
                im = im.convert("L")
                if True:
                    if choicei>1:
                        im.save(tmp,"JPEG",quality=q2)
                        im = Image.open(tmp)
                    if choicei>0:
                        im.save(tmp,"JPEG",quality=q1)
                        im = Image.open(tmp)
                    im.save(tmp,"JPEG",quality=q)
                jpg = jpegio.read(tmp.name)
                dct = jpg.coef_arrays[0].copy()
                im = im.convert('RGB')
            return {
                'image': self.toctsr(im),
                'label': mask.long(),
                'dct': np.clip(np.abs(dct),0,20),
                'qtb':use_qtb,
                'q':q
            }


class TamperDataset(Dataset):
    '''
    Dataset that works :).
    '''
    def __init__(
        self, 
        roots: Union[str, Path],
        mode: bool, 
        pickle_path: Union[str, Path], 
        minq: int=95,
        max_readers: int=64
    ) -> None:
        self.envs = lmdb.open(
            str(roots),
            max_readers=max_readers,
            readonly=True,
            lock=False,
            readahead=False,
            meminit=False
        )

        with self.envs.begin(write=False) as txn:
            self.nSamples = int(txn.get('num-samples'.encode('utf-8')))
        self.max_nums=self.nSamples

        self.minq = minq
        self.mode = mode

        with open('qt_table.pk','rb') as fpk:
            pks = pickle.load(fpk)
        self.pks = {}
        for k,v in pks.items():
            self.pks[k] = torch.LongTensor(v)
        
        with open(pickle_path,'rb') as f:
            self.record = pickle.load(f)

        self.totsr = ToTensorV2()
        self.toctsr =torchvision.transforms.Compose([
            torchvision.transforms.ToTensor(),
            torchvision.transforms.Normalize(
                mean=(0.485, 0.455, 0.406), 
                std=(0.229, 0.224, 0.225)
            )
        ])


    def __len__(self):
        return self.max_nums


    def read_image(self, files_code: str) -> Tuple[
        PIL.JpegImagePlugin.JpegImageFile,
        np.ndarray
    ]:
        '''
        Load image and it's mask from database.

        Parameters
        ----------
        files_code: str
            9 digit identifier for sample.
        
        Returns
        -------
        out: tuple[
            PIL.JpegImagePlugin.JpegImageFile,
            np.ndarray
        ]
        - Image.
        - Mask.
        '''
        with self.envs.begin(write=False) as txn:
            imgbuf = txn.get(f"image-{files_code}".encode('utf-8'))
            buf = six.BytesIO()
            buf.write(imgbuf)
            buf.seek(0)
            im = Image.open(buf)
            
            lbl_key = f"label-{files_code}"
            lblbuf = txn.get(lbl_key.encode('utf-8'))
            mask = (
                cv2.imdecode(
                    np.frombuffer(lblbuf,dtype=np.uint8), 0
                ) != 0
            ).astype(np.uint8)

        return im, mask


    def __getitem__(self, index: int) -> Dict[str, Any]:

        im, mask = self.read_image(files_code=('%09d'%index))

        record: Dict[int, np.ndarray] = self.record[index]

        choicei = len(record)-1
        q = int(record[-1])
        use_qtb = self.pks[q]

        with tempfile.NamedTemporaryFile(delete=True) as tmp:

            im = im.convert("L")

            quality = int(record[-3] if choicei > 1 else record[-2])
            im.save(tmp, "JPEG", quality=quality)

            im = Image.open(tmp)
            im.save(tmp, "JPEG", quality=q)

            jpg = jpegio.read(tmp.name)
            dct = jpg.coef_arrays[0].copy()
            im = im.convert('RGB')

        mask = self.totsr(image=mask.copy())['image']
        
        return {
            'image': self.toctsr(im),
            'label': mask.long(),
            'rgb': np.clip(np.abs(dct), 0, 20),
            'q': use_qtb,
            'i': q
        }
