'''
Download and unpack data for model.
'''
import zipfile
from tqdm import tqdm
import urllib.request
from pathlib import Path
data_path = Path("data")
data_path.mkdir(exist_ok=True)


def download_url(url: str, filename: Path):
    '''
    Download data and show progress bar during downloading.

    Parameters
    ----------
    url: str
        URL for downloading.
    
    filename: Path
        Path to save downloaded file.
    '''
    tqdm_bar = tqdm(
        unit='B', 
        unit_scale=True, 
        unit_divisor=1024, 
        desc="Downloading data"
    )

    with tqdm_bar as progress_bar:
        def reporthook(block_num, block_size, total_size):
            if total_size > 0:
                progress_bar.total = total_size
                progress_bar.update(block_num * block_size - progress_bar.n)

        urllib.request.urlretrieve(url, filename, reporthook)


archive_path = data_path/'DocTramper.zip'
if not archive_path.exists():
    download_link = 'https://storage.googleapis.com/kaggle-data-sets/5147540/8603105/bundle/archive.zip?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=gcp-kaggle-com%40kaggle-161607.iam.gserviceaccount.com%2F20240919%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20240919T143955Z&X-Goog-Expires=259200&X-Goog-SignedHeaders=host&X-Goog-Signature=16464a44f5fbdf10a76faafdeb302b07053883bd78543935d4eec571c3f1e5ecd4dd88f0efdb30b85d2a7fb69deff7fbbfda7ba1f815ece2aee9b07485e62b9697d77ce9b26541554d1bdcd7a330646d04315a7527e3cbeb97a05e0c8debf5d96e28cc131457b0a04d20d4e7bfbd057db83f1da743730251f7c7438743ce261b843ade1f2f844ba9090ebd21a9c29841d9547cc491991a32483ea8548e41ae03ff84c9c2f8dcdaa309954f4553f61bd9b4613712e54803fb17acd25c6d7a6ecbf7e21d9d473adc6ac61a5ccf61c7dac010a3267ac1dca8213c06a6a6cf9aa0c03eb478c1589b85b3f6fad75a29a371c87ee29985986930fc0de62f7be883707c'
    download_url(url=download_link, filename=archive_path)

with zipfile.ZipFile(file=str(archive_path), mode='r') as archive:
    archive.extractall(path="data")