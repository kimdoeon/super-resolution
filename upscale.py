from PIL import Image 
import os
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
import warnings


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

# 검사하는 코드 
def check_image(original_image_path,generated_image_path):
    '''
    input original image path and generated image path then check the generation complete right way
    also checking if generated image is all black or all white image 
    '''
    gened_image = Image.open(generated_image_path)
    pixel_data = list(gened_image.getdata())


    # all black image check 
    all_black = all(pixel == (0, 0, 0) for pixel in pixel_data)

    # all white image check 
    all_white = all(pixel == (255,255,255) for pixel in pixel_data)

    # file size check
    original_size_bytes = os.path.getsize(original_image_path)
    generated_size_bytes = os.path.getsize(generated_image_path)
    if original_size_bytes > generated_size_bytes:
        check_size = False
    else:
        check_size = True



    flag = not all_black and not all_white and check_size

    return flag


# upscale api calling 하는 함수 
def grpc_upscale_call(INPUT_PATH, OUT_PATH = './', key = None, set_width = 1024):
    '''
    calling gRPC stability upscale API 
    put input image path and output image path you want to save (ex : ./outputs)
    '''

    img = Image.open(INPUT_PATH)
    img_name = 'upscaled_' + INPUT_PATH.split('/')[-1]
    out_img_path = os.path.join(OUT_PATH,img_name)
    # -----------------------------gRPC stability ai code ------------------------
    # Set up our connection to the API.
    stability_api = client.StabilityInference(
        key=os.environ['STABILITY_KEY'], # API Key reference.
        upscale_engine="esrgan-v1-x2plus", # The name of the upscaling model we want to use.
                                        # Available Upscaling Engines: esrgan-v1-x2plus
        verbose=True, # Print debug messages.
    )
    answers = stability_api.upscale(
        init_image = img, # Pass our image to the API and call the upscaling process.
        width = set_width, # Optional parameter to specify the desired output width.
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
                out_img = Image.open(io.BytesIO(artifact.binary))
                if not os.path.exists(OUT_PATH):
                    os.mkdir(OUT_PATH)

                out_img.save(out_img_path) # Save our image to a local file.
    return out_img_path