from PIL import Image
import os
from dotenv import load_dotenv
from eeeee import UpscaleException
from upscale import UpscaleManager
load_dotenv()

# setting
user_folder_path = './sample'
img_name = 'human1.png'


# test can get image from path
def test_can_get_image_from_path():
    img = UpscaleManager(user_folder_path=user_folder_path).get_image_from_path(origin_img_name=img_name)

    assert isinstance(img, Image.Image)


# 시나리오 1 : test can generate upscale image from img
def test_can_gen_upscale_img():
    # given : 유효한 데이터 (정상 이미지 주소)
    # when : upscale 요청
    # then : 정상 응답 (업스케일 이미지 저장)
    img = UpscaleManager(user_folder_path=user_folder_path).get_image_from_path(origin_img_name=img_name)
    result_path = UpscaleManager(user_folder_path=user_folder_path).grpc_upscale_call(image=img, origin_img_name=img_name)

    assert os.path.exists(result_path)


no_token_key = os.environ.get("NO_TOKEN_KEY")


# 시나리오 2
def test_no_token_case():
    # given : 유효한 데이터 (정상 이미지 주소)
    # when : upscale 요청
    # then : 토큰이 없는 경우 Token error 발생
    img = UpscaleManager(user_folder_path=user_folder_path).get_image_from_path(origin_img_name=img_name)
    try:
        result_path = UpscaleManager(user_folder_path=user_folder_path).grpc_upscale_call(image=img, origin_img_name=img_name,api_key=no_token_key)
    except UpscaleException as e:
        assert e.code == 401 and e.message == "Failed to connect. Contact service administrator." and e.log == "Upscale API request error with non token. Please purchase tk"

# 시나리오 3
def test_wrong_image_path_case():
    # given : 없는 이미지 주소 (데이터 오류)
    # when : upscale 요청?? 그 전에 이미지 open할 때
    # then : image not found error
    try:
        img = UpscaleManager(user_folder_path=user_folder_path).get_image_from_path(origin_img_name='abstract123.png')
    except UpscaleException as e:
        assert e.code == 404 and e.message == 'Failed to upload image. try again.' and e.log == 'Wrong image path, Please check the input image path'


# 시나리오 4
# unnormal image
# Create a new black image
black_image = Image.new('RGB', (768, 768), (0, 0, 0))
black_image.save('./sample/black_image.png')


def test_black_image_given_case():
    # given : 검은색 화면 또는 흰색으로 채워진 이미지(잘못된 이미지)
    # when : upscale 요청
    # then : unormal image error 발생  -> 메시지 중요
    try:
        img = UpscaleManager(user_folder_path=user_folder_path).get_image_from_path(origin_img_name='black_image.png')
    except UpscaleException as e:
        assert e.code == 400 and e.message == 'Failed to upload image. Please take a painting again' and e.log == 'Requested image is entirely black or white.'


# 시나리오 5
wrong_key = 'skaka102id992j9j2'
emtpy_key = ''


def test_incorrect_api_key_case():
    # given : 잘못된 API key or 빈 API 키 + 정상 이미지 
    # when : stability client 연결 
    # then : Wrong API key error  -> log가 더 중요
    img = UpscaleManager(user_folder_path=user_folder_path).get_image_from_path(origin_img_name=img_name)
    try:
        result_path = UpscaleManager(user_folder_path=user_folder_path).grpc_upscale_call(image=img, origin_img_name=img_name, api_key=wrong_key)
    except UpscaleException as e:
        assert e.code == 400 and e.message == 'Failed to request. Contact service administrator.' and e.log == 'Wrong API key. Please check your API key'
