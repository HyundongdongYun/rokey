def generate_hairstyle_image(input_image_path, prompt, output_path="output.jpg"):
    from diffusers import StableDiffusionPipeline
    import torch
    import PIL.Image

    pipe = StableDiffusionPipeline.from_pretrained(
        "CompVis/stable-diffusion-v1-4", torch_dtype=torch.float16
    ).to("cuda")

    # input_image를 참조 프롬프트로 사용해야 하면 IP-Adapter 통합 필요

    image = pipe(prompt=prompt).images[0]
    image.save(output_path)
    return output_path

