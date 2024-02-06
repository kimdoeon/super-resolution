from PIL import Image 
import os
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
import warnings
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

#normal key 
key = os.environ.get('STABILITY_KEY')
host = os.environ.get('STABILITY_HOST')

#unormal key
wrong_key = 'skaka102id992j9j2'
emtpy_key = ''

# normal image 
IN_PATH = './sample/landscape1.jpg'
OUT_BASE = './outputs'
img_name = 'rescaled' + IN_PATH.split('/')[-1]
OUT_PATH = os.path.join(OUT_BASE,img_name)
img = Image.open(IN_PATH)


# unnormal image
# Create a new black image with dimensions 1024x1024
black_image = Image.new('RGB', (768, 768), (0, 0, 0))

# 시나리오 1 : 
# given : 유효한 데이터 (정상 이미지 주소)
# when : upscale 요청
# then : 정상 응답 (업스케일 이미지 저장)
def test_normal_case():
    # -----------------------------gRPC stability ai code ------------------------
    # Set up our connection to the API.
    stability_api = client.StabilityInference(
        key = key, # API Key reference.
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

    assert os.path.exists(OUT_PATH)



# 시나리오 2 
# given : 유효한 데이터 (정상 이미지 주소) 
# when : upscale 요청
# then : 토큰이 없는 경우 Token error 발생
    

# 시나리오 3 
# given : 없는 이미지 주소 (데이터 오류)
# when : upscale 요청?? 그 전에 이미지 open할 때
# then : image not found error 발생 -> 사용자보다 로그가 중요할 듯 (리사이즈 크롭한 이미지가 들어와야하니까)

# 시나리오 4
# given : 검은색 화면 또는 흰색으로 채워진 이미지(잘못된 이미지)
# when : upscale 요청
# then : unormal image error 발생  -> 메시지 중요

# 시나리오 5
# given : 잘못된 API key or 빈 API 키 + 정상 이미지 
# when : stability client 연결 
# then : Wrong API key error  -> log가 더 중요
    
# 시나리오6 
# given : 잘못된 output 이미지 결과 (온통 검은 화면)
# when : output 이미지 저장할 때, 
# then : unormal output error ? 