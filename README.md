# Serving a Pytorch model by using TorchServe

This Document For Debian Based Systems/ MacOS

For Windows follow the document from [torchserve](https://github.com/pytorch/serve#install-torchserve-and-torch-model-archiver)

## I. Installation
 1. Clone TorchServe repository
```shell
git clone https://github.com/pytorch/serve.git
```
 2. Install all dependencies:
 
    Note: For Conda, Python 3.8 is required to run Torchserve.

   - Change to *serve* directory
     
     ```bash
     cd serve
     ```       
    
   - For CPU

        ```bash
        python ./ts_scripts/install_dependencies.py
        ```
        
   - For GPU with Cuda 10.2. Options are `cu92`, `cu101`, `cu102`, `cu111`

       ```bash
       python ./ts_scripts/install_dependencies.py --cuda=cu102
       ```
 3. Install torchserve, torch-model-archiver and torch-workflow-archiver
   For Conda
   ```
   conda install torchserve torch-model-archiver torch-workflow-archiver -c pytorch
   ```
   
   For Pip
   ```
   pip install torchserve torch-model-archiver torch-workflow-archiver
   ```
### Install TorchServe for development at [here](https://github.com/pytorch/serve#install-torchserve-for-development)
 
## II. Serve a model
#### 1. Run an example from github
   ##### 1.1 Change to the parent directory of the *serve* directory
   
   ```bash
   cd ..
   ```
   ##### 1.2 Create a folder to store your models
   
   ```bash
   mkdir model_store
   ```
   ##### 1.3 Download a trained model
   
   ```bash
    wget https://download.pytorch.org/models/densenet161-8d451a50.pth
   ```
   ##### 1.4 Archive the model by using the model archiver.
   
   ```bash
    torch-model-archiver --model-name densenet161 --version 1.0 --model-file ./serve/examples/image_classifier/densenet_161/model.py --serialized-file densenet161-8d451a50.pth --export-path model_store --extra-files ./serve/examples/image_classifier/index_to_name.json --handler image_classifier

   ```
   [Here](https://github.com/pytorch/serve/blob/master/model-archiver/README.md) for more informations about arguments.
  
  ##### 1.5 Start TorchServe to serve the model
  ```bash
    torchserve --start --ncs --model-store model_store --models densenet161.mar
   ```
  ##### 1.6 Get predictions from a model
  
  1.6.1 Using GRPC APIs through python client
     
   - Install grpc python dependencies :
   
     ```bash
     pip install -U grpcio protobuf grpcio-tools
     ```
   - Generate inference client using proto files
   
     ```bash
     python -m grpc_tools.protoc --proto_path=frontend/server/src/main/resources/proto/ --python_out=ts_scripts --grpc_python_out=ts_scripts   
     frontend/server/src/main/resources/proto/inference.proto frontend/server/src/main/resources/proto/management.proto
     ```
   - Run inference using a sample client [gRPC python client](ts_scripts/torchserve_grpc_client.py)
   - 
     ```bash
     python ts_scripts/torchserve_grpc_client.py infer densenet161 examples/image_classifier/kitten.jpg
     ```
  1.6.2 Using REST APIs
  
   - Download an image to test the model server (you also can use your own data).
   
     ![kitten](https://github.com/pytorch/serve/blob/master/docs/images/kitten_small.jpg)
     
     ```bash
     curl -O https://raw.githubusercontent.com/pytorch/serve/master/docs/images/kitten_small.jpg
     ```
   - The first way, we can use terminal to get prediction:
   
     ```bash
     curl http://127.0.0.1:8080/predictions/densenet161 -T kitten_small.jpg
     ```
   
   - The other way, we implement a python script to get prediction:
   
     ```bash
     python send_request.py
     ```
   
