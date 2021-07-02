from __future__ import print_function
import requests
from io import BytesIO
import time 

addr = 'http://127.0.0.1:8080'
test_url = addr + '/predictions/densenet161'
start = time.time()
url = 'https://raw.githubusercontent.com/pytorch/serve/master/docs/images/kitten_small.jpg'

# prepare headers for http request
content_type = 'image/jpeg'
headers = {'content-type': content_type}

response = requests.get(url)
byte_img = BytesIO(response.content)

# send http request with image and receive response
response = requests.post(test_url, data=byte_img, headers=headers)

print(time.time()-start)
print(response.text)