from PIL import Image
import os
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
import warnings
from io import BytesIO
from eeeee import UpscaleException
from error_code import UpscaleErrorCode
import grpc
from dotenv import load_dotenv
load_dotenv()

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

# ------------------
user_folder_path = './sample'  # self


def get_image_from_path(origin_img_name: str):
    """
    Get image for Upscale
    Param:
        - origin_img_name : 원본 이미지 이름(example.png)
    Return:
        - Pillow Image 객체
    """
    # get image from path
    origin_img_path = os.path.abspath(os.path.join(user_folder_path, origin_img_name))
    if os.path.exists(origin_img_path):
        image = Image.open(origin_img_path).convert("RGB")
        if all(pixel == (0, 0, 0) for pixel in list(image.getdata())) or all(pixel == (255, 255, 255) for pixel in list(image.getdata())):
            raise UpscaleException(**UpscaleErrorCode.WrongImageError.value)
    else:
        raise UpscaleException(**UpscaleErrorCode.FileNotFoundError.value)

    return image


api_key = os.environ.get('STABILITY_KEY')
width = 1024


def grpc_upscale_call(image: Image, origin_img_name: str, api_key=api_key):
    """
    Get generated upscaled image from stability ai grpc
    Params:
        - image : 사용할 이미지 개체
        - origin_img_name: 저장할 img 이름
    Return:
        - origin_img_path: 저장한 img 경로
    Description:
        - image should be pillow Image
    """
    origin_img_path = os.path.abspath(os.path.join(user_folder_path, origin_img_name))

    stability_api = client.StabilityInference(
        key=api_key,  # API Key reference.
        upscale_engine="esrgan-v1-x2plus",  # The name of upscaling model
        verbose=True,  # Print debug messages.
    )

    answers = stability_api.upscale(
        init_image=image,  # Pass image to API and call the upscaling process.
        width=width,  # Optional parameter to specify the desired output width.
    )
    # If adult content classifier is not tripped, save our image.
    try:
        for resp in answers:
            for artifact in resp.artifacts:
                if artifact.finish_reason == generation.FILTER:  # 자체 필터 걸렸다는 워닝 출력
                    warnings.warn(
                        "Your request activated the API's safety filters and could not be processed."
                        "Please submit a different image and try again.")
                if artifact.type == generation.ARTIFACT_IMAGE:  # 아티펙트 타입이 이미지이면 이미지 열어서 원하는 path에 save
                    out_img = Image.open(BytesIO(artifact.binary))
                    if not os.path.exists(user_folder_path):
                        os.mkdir(user_folder_path)

                    out_img.save(origin_img_path)  # Save our image to a local file.
    except grpc.RpcError as e:
        if e.code().value[0] == 8:
            raise UpscaleException(**UpscaleErrorCode.NonTokenError.value, error=e)
        elif e.code().value[0] == 16:
            raise UpscaleException(**UpscaleErrorCode.WrongApiKeyError.value, error=e)
        else:
            raise UpscaleException(**UpscaleErrorCode.APIError.value, error=e)
    return origin_img_path
