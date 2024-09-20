# DocTamper

This is the official repository of the paper Towards Robust Tampered Text Detection in Document Image: New dataset and New Solution. [paper](https://openaccess.thecvf.com/content/CVPR2023/papers/Qu_Towards_Robust_Tampered_Text_Detection_in_Document_Image_New_Dataset_CVPR_2023_paper.pdf).


To install requirements use:

```
python3.8 -m venv venv
pip3 install segmentation_models_pytorch==0.2.1
pip3 install -r requirements.txt -U
```

`segmentation_models_pytorch` is now being installed separately due to a requirements conflict in the original repository. However, you can still install `segmentation_models_pytorch` independently from the main `requirements`. We're actively working to fix this issue.

**Note**: We're using the CUDA 12.4 PyTorch distribution. If you're using a different version, specify the appropriate `--extra-index-url` for your setup.

## Dataset

The DocTamper dataset is now avaliable at [BaiduDrive](https://pan.baidu.com/s/1nEEnq1ZWIem7wnkQ1YdTNw?pwd=od9k) and [Kaggle](https://www.kaggle.com/datasets/dinmkeljiame/doctamper/data).

Use script `data.py` for downloading and unpacking data.

---

The official implementation of the paper  Towards Robust Tampered Text Detection in Document Image: New Dataset and New Solution is in the "models" directory.

I delay the release of training codes as forced by my supervisor and the cooperative enterprise who bought them. My training pipline for DocTamper dataset and the IoU metric heavily brought from a famous project in this area, the results of  the paper can be easily re-produced with [it](https://github.com/DLLXW/data-science-competition/blob/main/tianchi/ImageForgeryLocationChallenge/utils/deeplearning_qyl.py), you just need to adjust the loss functions and the learing rate decay curve. I also used its [augmentation pipline](https://github.com/DLLXW/data-science-competition/blob/main/tianchi/ImageForgeryLocationChallenge/dataset/RSCDataset.py) except for (RandomBrightnessContrast, ShiftScaleRotate, CoarseDropout).


Open Source Scheme: <br>
1、Inference models and codes: June, 2023. <br>
2、Training codes: TBD. <br>
3、Data synthesis code: Within 2024. <br>

---

Any question about this work please contact 202221012612@mail.scut.edu.cn.

---

If you find this work useful in your research, please consider citing:
```
@inproceedings{qu2023towards,
  title={Towards Robust Tampered Text Detection in Document Image: New Dataset and New Solution},
  author={Qu, Chenfan and Liu, Chongyu and Liu, Yuliang and Chen, Xinhong and Peng, Dezhi and Guo, Fengjun and Jin, Lianwen},
  booktitle={Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition},
  pages={5937--5946},
  year={2023}
}
```
