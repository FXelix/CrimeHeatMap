from PIL import Image, ImageDraw, ImageFont

def add_filename(image_name):
	im = Image.open(f'png_images/{image_name}.png')
	draw = ImageDraw.Draw(im)
	font = ImageFont.truetype('abel-regular.ttf',30)
	draw.text((256,480),f'{image_name}',(0,0,0),font=font)
	im.save(f'png_images/dated/ ({image_name}).png')


for year in range(2001,2017):
	for month in range(1,13):
		image_name = f'{year} - {month}'
		add_filename(image_name)
