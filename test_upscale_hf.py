'''
Test code for super-resolution 
we test two super resolution ways : 
    1. using Hugging Face model  : stability - the text-guided x4 superresolution model.
    2. Stability AI API 
'''
import requests
from PIL import Image
from io import BytesIO
from diffusers import StableDiffusionUpscalePipeline
import torch

# load model and scheduler
model_id = "stabilityai/stable-diffusion-x4-upscaler"
pipeline = StableDiffusionUpscalePipeline.from_pretrained(
    model_id, variant='fp16', torch_dtype=torch.float16
)

# for mac M1 M2 
pipeline = pipeline.to("mps")
pipeline.enable_attention_slicing()

# for Nvidia GPU 
# pipeline = pipeline.to("cuda")

# let's download an  image
url = "https://huggingface.co/datasets/hf-internal-testing/diffusers-images/resolve/main/sd2-upscale/low_res_cat.png"
response = requests.get(url)
low_res_img = Image.open(BytesIO(response.content)).convert("RGB")
low_res_img = low_res_img.resize((128, 128))
prompt = "a white cat"

upscaled_image = pipeline(prompt=prompt, image=low_res_img).images[0]
upscaled_image.save("upsampled_cat_red.png")