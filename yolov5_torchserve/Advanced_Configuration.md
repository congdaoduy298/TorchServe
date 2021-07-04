# Advanced Configuration

There are three ways to configure TorchServe. In order of priority, they are:

- Environment variables

- Command line arguments

- Configuration file

## 1. Environment variables.

You can change TorchServe behavior by setting the following environment variables:

- JAVA_HOME (Path of Java Library)

- PYTHONPATH (Path of Python Library).
This variable has a meaning like sys.path.append in Python. 
When adding PYTHONPATH to the terminal, we can import python script on this path. 

Example: /home/user/Desktop/yolov5/utils/letterbox.py
    For using python script in utils, we run this command on terminal:

```bash
export PYTHONPATH=$PYTHONPATH:/home/user/Desktop/yolov5
```
    $PYTHONPATH: list current paths of PYTHONPATH variable. 
    
We can append more path to PYTHONPATH (PYTHONPATH will be split by “:”).

```bash
export PYTHONPATH=$PYTHONPATH:/home/user/Desktop/tmp_folder
```
    
- TS_CONFIG_FILE ( Path to config file)
    
- LOG_LOCATION (Logging folder Path)
    
- METRICS_LOCATION (Metrics folder Path)

## 2.Command line parameters

Customize TorchServe behavior by using the following command line arguments when you call torchserve:

```
–ts-config : TorchServe loads the specified configuration file
–model-store : Model folder path
–models : Model name
–log-config : Overrides the default log4j.properties. This file contains where you want to save access_log, ts_log, ts_metrics, model_log, model_metrics file and what is the maximum size of the files, etc .
–foreground : Runs TorchServe in the foreground. 
```
Example: 
```bash
torchserve --start --ncs --model-store model_store --models my_model_name.mar -ts-config /home/user/TorchServe-REST/model_store/config.properties
```

### Must remember the priority of Environment variables is the most important.

## 3.Create config.properties file

TorchServe loads the configuration from the path specified. (Depend on the priority)

If there is a config.properties in the folder where you call torchserve, TorchServe loads the config.properties file from the current working directory.

If none of the config paths is specified, TorchServe loads a built-in configuration with default values.

## Important parameters: 

### 3.1 Configure REST API listening address and port:
- inference_address: Inference API binding address. Default: http://127.0.0.1:8080
- management_address: Management API binding address. Default: http://127.0.0.1:8081
- metrics_address: Metrics API binding address. Default: http://127.0.0.1:8082

### 3.2 Configure gRPC listening port:
- grpc_inference_port: Inference gRPC API binding port. Default: 7070
- grpc_management_port: management gRPC API binding port. Default: 7071 

##### Must change the listening address and port if it is already in use on the operating system.

### 3.3 Enable SSL:

1. Use a keystore. 

Generate a keystore with Java’s keytool.

```
keytool -genkey -keyalg RSA -alias ts -keystore keystore.p12 -storepass changeit -storetype PKCS12 -validity 3600 -keysize 2048 -dname "CN=www.MY_TS.com, OU=Cloud Service, O=model server, L=Palo Alto, ST=California, C=US"
```

Serve a model must provide a certificate and private key to enable SSL.

Configure the following properties in config.properties:
```
inference_address=https://127.0.0.1:8443
management_address=https://127.0.0.1:8444
metrics_address=https://127.0.0.1:8445
keystore=keystore.p12
keystore_pass=changeit
keystore_type=PKCS12  
```

To send a request to the listening address set verify = False

```
requests.post(url, data=data, headers=headers, verify=False)
```

2. Use private-key/certificate files; generate your self signed cert and key with OpenSSL:

```
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout mykey.key -out mycert.pem
````

Config following property in config.properties:
```
inference_address=https://127.0.0.1:8443
management_address=https://127.0.0.1:8444
metrics_address=https://127.0.0.1:8445
private_key_file=mykey.key
certificate_file=mycert.pem
```

### 3.4 Other properties:

```
number_of_gpu: Maximum number of GPUs that TorchServe can use for inference. Default: all available GPUs in system.

enable_metrics_api : Enable or disable metric apis i.e. it can be either true or false

enable_envvars_config: When this option is set to true, any parameters in *config.properties* can be defined by environment variables. Default: false.
```
Example: To change *default_response_timeout = 6* (though in *config.properties* is set 120). We set *enable_envvars_config=true* and set environment variable *TS_DEFAULT_RESPONSE_TIMEOUT = 6*.

Note: export environment variable for property as *TS_<PROPERTY_NAME>*.
eg: to set *inference_address* property run cmd or terminal

```bash
export TS_INFERENCE_ADDRESS="http://127.0.0.1:8082".
```

default_workers_per_model: Number of workers to create for each model that is loaded at startup time. Default: available CPUs/GPUs in system. (If it is set to 0, the number of workers is still the number of available CPUs/GPUs in the system).

job_queue_size: Number inference jobs that frontend will queue before backend can serve. Default: 100. (Number requests at a time is num_workers + job_queue_size).

default_response_timeout: Timeout, in seconds, maximum time for model’s backend workers process a request. Raise Error 500 if no response.

unregister_model_timeout : Timeout, in seconds, used when handling an unregister model request when cleaning a process before it is deemed unresponsive and an error response is sent. Default: 120 seconds.

model_store : Path of model store directory.

model_server_home : Torchserve home directory.

max_request_size : The maximum allowable request size that the Torchserve accepts, in bytes. Default: 6553500

max_response_size : The maximum allowable response size that the Torchserve sends, in bytes. Default: 6553500
```