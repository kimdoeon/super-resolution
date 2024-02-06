from PIL import Image 
import os
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
import warnings
from io import BytesIO
import grpc
import pytest
from dotenv import load_dotenv
from eeeee import *
from error_code import UpscaleErrorCode
from upscale import get_image_from_path, grpc_upscale_call
load_dotenv()

#normal key
key = os.environ.get('STABILITY_KEY')
host = os.environ.get('STABILITY_HOST')

#unormal key
wrong_key = 'skaka102id992j9j2'
emtpy_key = ''
no_token_key = os.environ.get("NO_TOKEN_KEY")

# normal image 
IN_PATH = './sample/abstract0.png'
OUT_BASE = './outputs'
img_name = 'rescaled' + IN_PATH.split('/')[-1]
OUT_PATH = os.path.join(OUT_BASE, img_name)
img = Image.open(IN_PATH)


# test can get image from path
def test_can_get_image_from_path():
    img = get_image_from_path('abstract1.png')

    assert isinstance(img, Image.Image)


# 시나리오 1 : test can generate upscale image from img
def test_can_gen_upscale_img():
    # given : 유효한 데이터 (정상 이미지 주소)
    # when : upscale 요청
    # then : 정상 응답 (업스케일 이미지 저장)
    img = get_image_from_path('abstract1.png')
    result_path = grpc_upscale_call(image=img, origin_img_name='upscaled.png')

    assert os.path.exists(result_path)



# 시나리오 2 
def test_no_token_case():
    # given : 유효한 데이터 (정상 이미지 주소) 
    # when : upscale 요청
    # then : 토큰이 없는 경우 Token error 발생
    # -----------------------------gRPC stability ai code ------------------------
    # Set up our connection to the API.
    stability_api = client.StabilityInference(
        key = no_token_key, # API Key reference.
        upscale_engine="esrgan-v1-x2plus", # The name of the upscaling model we want to use.
                                        # Available Upscaling Engines: esrgan-v1-x2plus
        verbose=True, # Print debug messages.
    )
    answers = stability_api.upscale(
        init_image = img, # Pass our image to the API and call the upscaling process.
        width = 1024, # Optional parameter to specify the desired output width.
    )
    # Set up our warning to print to the console if the adult content classifier is tripped.
    # If adult content classifier is not tripped, save our image.
    with pytest.raises(UpscaleException):
        try:
            for resp in answers:
                for artifact in resp.artifacts:
                    if artifact.finish_reason == generation.FILTER: # 자체 필터 걸렸다는 워닝 출력 
                        warnings.warn(
                            "Your request activated the API's safety filters and could not be processed."
                            "Please submit a different image and try again.")
                    if artifact.type == generation.ARTIFACT_IMAGE: # 아티펙트 타입이 이미지이면 이미지 열어서 원하는 path에 save
                        out_img = Image.open(BytesIO(artifact.binary))
                        if not os.path.exists(OUT_BASE):
                            os.mkdir(OUT_BASE)

                        out_img.save(OUT_PATH) # Save our image to a local file.
        except grpc.RpcError as e:
            raise UpscaleException(**UpscaleErrorCode.NonTokenError.value)
    

# 시나리오 3 
Wrong_image_path = './sample/no_image.png'
def test_wrong_image_path_case():
    # given : 없는 이미지 주소 (데이터 오류)
    # when : upscale 요청?? 그 전에 이미지 open할 때
    # then : image not found error 발생 -> 사용자보다 로그가 중요할 듯 (리사이즈 크롭한 이미지가 들어와야하니까)

    with pytest.raises(UpscaleException):
        try:
            img = Image.open(Wrong_image_path)
        except FileNotFoundError as e:
            raise UpscaleException(**UpscaleErrorCode.FileNotFoundError.value)

# 시나리오 4
# unnormal image
# Create a new black image
black_image = Image.new('RGB', (768, 768), (0, 0, 0))
def test_black_image_given_case():
    # given : 검은색 화면 또는 흰색으로 채워진 이미지(잘못된 이미지)
    # when : upscale 요청
    # then : unormal image error 발생  -> 메시지 중요
    with pytest.raises(UpscaleException):
        if all(pixel == (0, 0, 0) for pixel in list(black_image.getdata())) or all(pixel == (255, 255, 255) for pixel in list(black_image.getdata())):
            raise UpscaleException(**UpscaleErrorCode.WrongImageError.value)

# 시나리오 5

def test_incorrect_api_key_case():
    # given : 잘못된 API key or 빈 API 키 + 정상 이미지 
    # when : stability client 연결 
    # then : Wrong API key error  -> log가 더 중요

    # -----------------------------gRPC stability ai code ------------------------
    # Set up our connection to the API.
    stability_api = client.StabilityInference(
        key = wrong_key, # API Key reference.
        upscale_engine="esrgan-v1-x2plus", # The name of the upscaling model we want to use.
                                        # Available Upscaling Engines: esrgan-v1-x2plus
        verbose=True, # Print debug messages.
    )
    answers = stability_api.upscale(
        init_image = img, # Pass our image to the API and call the upscaling process.
        width = 1024, # Optional parameter to specify the desired output width.
    )
    # Set up our warning to print to the console if the adult content classifier is tripped.
    # If adult content classifier is not tripped, save our image.
    with pytest.raises(UpscaleException):
        try:
            for resp in answers:
                for artifact in resp.artifacts:
                    if artifact.finish_reason == generation.FILTER: # 자체 필터 걸렸다는 워닝 출력 
                        warnings.warn(
                            "Your request activated the API's safety filters and could not be processed."
                            "Please submit a different image and try again.")
                    if artifact.type == generation.ARTIFACT_IMAGE: # 아티펙트 타입이 이미지이면 이미지 열어서 원하는 path에 save
                        out_img = Image.open(BytesIO(artifact.binary))
                        if not os.path.exists(OUT_BASE):
                            os.mkdir(OUT_BASE)

                        out_img.save(OUT_PATH) # Save our image to a local file.
        except grpc.RpcError as e:
            raise UpscaleException(**UpscaleErrorCode.WrongApiKeyError.value)
    
# 시나리오6 

# Create a new black image
black_image = Image.new('RGB', (768, 768), (0, 0, 0))
black_image.save(OUT_BASE + '/black_output.png')
def test_black_image_given_case():
    # given : 잘못된 output 이미지 결과 (온통 검은 화면)
    # when : output 이미지 저장할 때, 
    # then : unormal output error ? 
    out_image = Image.open(OUT_BASE + '/black_output.png')
    with pytest.raises(UpscaleException):
        if all(pixel == (0, 0, 0) for pixel in list(out_image.getdata())) or all(pixel == (255, 255, 255) for pixel in list(out_image.getdata())):
            raise UpscaleException(**UpscaleErrorCode.WrongImageOutError.value)
