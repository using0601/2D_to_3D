# Dataset
所需dataset：連續照片、相機內外部參數(`.yml`)  
dataset放置：放在`dataset/`  
dataset格式：
```
dataset
|---{dataset name}
    |---images
    |   |---{camera 1}
    |   |   |---000000.jpg
    |   |   |---000001.jpg
    |   |   |---...
    |   |---{camera 2}
    |   |   |---000000.jpg
    |   |   |---000001.jpg
    |   |   |---...
    |   |---...
    |---mask
    |   |---{camera 1}
    |   |   |---000000.png
    |   |   |---000001.png
    |   |   |---...
    |   |---{camera 2}
    |   |   |---000000.png
    |   |   |---000001.png
    |   |   |---...
    |   |---...
    |---extri.yml
    |---intri.yml
```
`mask`資料夾下的圖檔，位元深度需為1  
相機參數格式：請參考 https://chingswy.github.io/easymocap-public-doc/database/1_camera.html

## 範例dataset
浙江大學MoCap dataset  
https://chingswy.github.io/Dataset-Demo/  
需要向浙江大學取得download link  
`mask`採用的是`mask_cihp`資料夾下的檔案，且需要事先將超過1的值調整為1。

## 自動校準相機參數

若沒有相機參數（或是不信任相機參數），也可以用COLMAP估出，方法如以下步驟：
1. 參考 https://colmap.github.io/install.html 安裝COLMAP，建議安裝支援CUDA的版本
2. `python extract.py --skip_pcd {dataset name} {time step}`  
=> 產生第`time step`個時間點，透明背景的圖片，直接放在`dataset/{dataset name}/images/`資料夾下面
3. 將`dataset/{dataset name}/images/`中的圖片移至`dataset/{dataset name}/input/`資料夾（複製一份亦可）
4. `python gaussian-splatting/convert.py -s dataset/{dataset name}`  
如果COLMAP沒有在系統路徑上，可以`--colmap_executable {path to colmap}`指定COLMAP執行檔路徑（其中在Windows上需將路徑指向`.bat`檔）。更多細節可參考`gaussian-splatting/README.md`。
5. 將`dataset/{dataset name}/sparse/0/`中的`cameras.bin`、`images.bin`放入`dataset/{dataset name}/colmap_cam`
6. `python generate_pointcloud/gen_colmap_cam/gen_colmap.py {dataset name}`  
=> 估出之相機參數(`.yml`)已放入`dataset/{dataset name}/`  
（若用COLMAP估，則相機名稱必須是`Camera_B1`, `Camera_B2`...）

# 環境設置

## EasyMoCap

```shell
conda create -n easymocap python=3.9 -y
conda activate easymocap
wget -c https://download.pytorch.org/whl/cu111/torch-1.9.1%2Bcu111-cp39-cp39-linux_x86_64.whl
wget -c https://download.pytorch.org/whl/cu111/torchvision-0.10.1%2Bcu111-cp39-cp39-linux_x86_64.whl
python3 -m pip install ./torch-1.9.1+cu111-cp39-cp39-linux_x86_64.whl
python3 -m pip install ./torchvision-0.10.1+cu111-cp39-cp39-linux_x86_64.whl
python -m pip install -r requirements.txt
# install pyrender if you have a screen
python3 -m pip install pyrender
python setup.py develop
python3 -m pip install open3d
```
Prepare SMPL model:  
請參考 https://chingswy.github.io/easymocap-public-doc/install/install.html#prepare-smpl-models

## Gaussian Splatting

硬體要求：
* 支援CUDA的顯示卡，建議compute capability至少7.0（但已知6.0也跑得動）

軟體要求：
* Python >= 3.9
* Anaconda （建議，以下建置步驟使用）
* C++ Compiler for PyTorch extensions (we used Visual Studio 2022 for Windows)
* CUDA SDK 11 for PyTorch extensions, install after Visual Studio (we used 12.1, known issues with 11.6)
* C++編譯器與CUDA SDK須相容

建置步驟：（根據系統設定，可能需要root或系統管理員權限）
```shell
SET DISTUTILS_USE_SDK=1 # Windows only
conda env create --file environment.yml
conda activate gaussian_splatting
```
注意`environment.yml`與原repo的版本不一樣。如有其它版本需求，可以微調此檔案，但不保證對較低軟體版本的相容性。

# 執行步驟

1. `emc --data generate_pointcloud/config/datasets/mvimage.yml --exp generate_pointcloud/config/mv1p/detect_triangulate_fitSMPL.yml --root dataset/{dataset name} --subs_vis {camera name} --out output/{dataset name}`
2. `python3 generate_pointcloud/apps/postprocess/write_vertices.py generate_pointcloud/output/{dataset name}/smpl generate_pointcloud/output/{dataset name}/vertices --cfg_model generate_pointcloud/config/model/smpl.yml --mode vertices`
3. `python generate_pointcloud/json2ply.py {dataset name}`  
=> pointcloud already in `generate_pointcloud/pcd/{dataset name}`
4. `python extract.py [--skip_image] {dataset name} {time step}`  
若已產生透明背景的圖片，且時間點亦相同，則可使用`--skip_image`跳過此動作。
5. 若未有COLMAP相機參數檔案（`dataset/{dataset name}/sparse/0/cameras.bin`及`dataset/{dataset name}/sparse/0/images.bin`）：  
`python gaussian-splatting/camera_yml2colmap.py {dataset name}`
6. `cd gaussian-splatting`  
`python train.py -s ../dataset/{dataset name} -m {model path} [--eval] [--iterations ITERATIONS]`  
`python render.py -m {model path} [--skip_train] [--skip_test]`  
`--eval`參數模仿MipNeRF360，將所有視角切分成訓練視角（預設約7/8）及驗證視角（預設約1/8），如果需要其它分割模式（例如報告中將範例資料集唯一過度曝光的視角用作驗證），則可能需要直接修改`gaussian-splatting/scene/dataset_readers.py`。更多可調整的參數請直接參考`gaussian-splatting/README.md`。
