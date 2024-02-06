'''
gRPC 방식 stability API 호출 코드 

esrgan-v1-x2plus 엔진으로 사용시 0.2토큰 ($0.002)

가능한 파라미터 
init_image= 
width= and height= parameters are accepted.

only width= OR height=  가능  (width 와 height 둘 다 동시에 설정 X )

If no width= or height= parameter is provided, 
    the image will be upscaled to 2x or 4x its dimensions by default depending on the engine in use.
'''

import os
import io
import warnings
from PIL import Image
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
from dotenv import load_dotenv

# 환경변수 설정
load_dotenv()
os.environ['STABILITY_HOST'] = os.environ.get('STABILITY_HOST')
os.environ['STABILITY_KEY'] = os.environ.get('STABILITY_KEY')

#데이터 준비
# Import our local image to use as a reference for our upscaled image.
# The 'img' variable below is set to a local file for upscaling, however if you are already running a generation call and have an image artifact available, you can pass that image artifact to the upscale function instead.
img = Image.open('./sample/landscape0.png')


def test_upscale():
        
    # Set up our connection to the API.
    stability_api = client.StabilityInference(
        key=os.environ['STABILITY_KEY'], # API Key reference.
        upscale_engine="esrgan-v1-x2plus", # The name of the upscaling model we want to use.
                                        # Available Upscaling Engines: esrgan-v1-x2plus
        verbose=True, # Print debug messages.
    )



    answers = stability_api.upscale(
        init_image=img, # Pass our image to the API and call the upscaling process.
        # width=1024, # Optional parameter to specify the desired output width.
    )

    # Set up our warning to print to the console if the adult content classifier is tripped.
    # If adult content classifier is not tripped, save our image.

    for resp in answers:
        for artifact in resp.artifacts:
            if artifact.finish_reason == generation.FILTER: # 자체 필터 걸렸다는 워닝 출력 
                warnings.warn(
                    "Your request activated the API's safety filters and could not be processed."
                    "Please submit a different image and try again.")
            if artifact.type == generation.ARTIFACT_IMAGE: # 아티펙트 타입이 이미지이면 이미지 열어서 원하는 path에 save
                big_img = Image.open(io.BytesIO(artifact.binary))
                big_img.save("imageupscaled" + ".png") # Save our image to a local file.