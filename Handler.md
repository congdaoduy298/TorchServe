# HANDLER

## I. AVAILABLE HANDLER

TorchServe supports the following handlers out of box:

- `image_classifier`
- `object_detector`
- `text_classifier`
- `image_segmenter`

### 1. image_classifier

* Description : Handles image classification models trained on the ImageNet dataset.
* Input : RGB image
* Output : Batch of top 5 predictions and their respective probability of the image

You can see this file [here](https://github.com/pytorch/serve/blob/master/ts/torch_handler/image_classifier.py)

### 2. image_segmenter

* Description : Handles image segmentation models trained on the ImageNet dataset.
* Input : RGB image
* Output : Output shape as [N, CL, H, W], N - batch size, CL - number of classes, H - height and W - width.

You can see this file [here](https://github.com/pytorch/serve/blob/master/ts/torch_handler/image_segmenter.py)

### 3. object_detector

* Description : Handles object detection models.
* Input : RGB image
* Output : Batch of lists of detected classes and bounding boxes respectively

Note : We recommend running `torchvision>0.6` otherwise the object_detector default handler will only run on the default GPU device


You can see this file [here](https://github.com/pytorch/serve/blob/master/ts/torch_handler/object_detector.py)

### 4. text_classifier

* Description : Handles models trained on the ImageNet dataset.
* Input : text file
* Output : Class of input text. (No batching supported)

You can see this file [here](https://github.com/pytorch/serve/blob/master/ts/torch_handler/text_classifier.py)


As you see `ImageClassifier`, `ImageSegmenter` ,and `ObjectDetector` inherits of `VisionHandler` class. The `VisionHandler` preprocess data is sent from client (binary format) and it decode data to PIL image and *image_processing* process will be applied. After that data will go through *inference* method of `Base_Handler` class (`VisionHandler` inherits it). Then data will pass *postprocess* method of one of the three beginning classes depend on what handler did you call.

`TextClassifier` also has that pipeline.

To read more from [TorchServe Github](https://github.com/pytorch/serve/blob/master/docs/default_handlers.md).

## II. CUSTOM HANDLER 

I am going to write a yolov5 custom handler.

Just like the `ImageClassifier`, `ImageSegmenter` ,and `ObjectDetector` classes. To write a image handler, `ModelHandler` inherits of `Base_Handler` class. We have to write `preprocess` method and `postprocess` method.  

Follow the flow of get predictions from yolov5 model. Try to read `detect.py` file to get the flow.

- At prediction stage, the yolov5 progress will follow these steps:
    
    ```python
        img0 = cv2.imread(path)  # BGR
        # Padded resize
        img = letterbox(img0, self.img_size, stride=self.stride)[0]
        # Convert
        img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB and HWC to CHW
        img = np.ascontiguousarray(img)
        img = torch.from_numpy(img).to(device)
        # half only supported on CUDA
        img = img.half() if half else img.float()  # uint8 to fp16/32
        img /= 255.0  # 0 - 255 to 0.0 - 1.0
        if img.ndimension() == 3:
            img = img.unsqueeze(0)
        pred = model(img)[0]
        pred = non_max_suppression(pred, conf_thres, iou_thres, classes, agnostic_nms, max_det=max_det)
    ```

(`LoadImages` class from `utils/datasets.py` and from file `detect.py`)

You can see how `letterbox` work [here](https://github.com/AlexeyAB/darknet/issues/232#issuecomment-336955485). But in this case `letterbox` only scale image to keep ratio and resize image by adding padding 0. 

- Example: image 1280x720 will be resized to 416x234. Not 416X416

So we can write preprocess method and postprocess base on these above steps.

In `preprocess` method (Take the input data and make it inference ready):
    
You can see, raw data is sent from client will pass to `preprocess`.

```python
def preprocess(self, data):
```

Do some preprocessing like these above steps of yolov5 prediction stage.

```python
# Get byte data.
# Key 'body' is by default.
byte_array = data[0]['body']
file_bytes = np.asarray(bytearray(byte_array), dtype=np.uint8)
# yolov5 preprocessing
img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
img = letterbox(img, self.img_size, stride=self.stride)[0] 
# Looks like the image of letterbox function here.
# https://github.com/AlexeyAB/darknet/issues/232#issuecomment-336955485
img = padding_image(img, self.img_size, self.img_size)
img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
img = np.ascontiguousarray(img)
input = torch.from_numpy(img)
input = input.float()
input /= 255.0  # 0 - 255 to 0.0 - 1.0
if input.ndimension() == 3:
    input = input.unsqueeze(0)

# Do this if you want to predict on a batch.
# inputs[i, :, :, :] = input
```

In `postprocess` method (Return inference result.):

After `preprocess`, data will pass to model by `inference` method that inherits from `BaseHandler`.

```python
def postprocess(self, inference_output):
```
Input of `postprocess` is the result of `inference`. That can be considered as step `pred = model(img)` in yolov5 prediction stage.

So we need to apply non-max suppression on the result. And convert the result of NMS to list.

```python
postprocess_output = inference_output
pred = non_max_suppression(postprocess_output[0], conf_thres=0.2)
pred = [p.tolist() for p in pred]
return [pred]
```

### NOTE: 

- A eager model of yolov5 you can pass any size of images. It helps the model is able to use `Multi-Scale Training` approach. And at prediction stage, we can pass any size of images that will keep the ratio of images. 

- However, after export to a script model that means we only can pass through the model with specific size. In my case, I use img_size = 640. Only an image 640 X 640 pixels can go through the model. 

You can read more about [custom handlers](https://github.com/pytorch/serve/blob/master/docs/default_handlers.md).








