from sys import argv
import cv2
import numpy as np
import matplotlib.animation as animation
import matplotlib.pyplot as plt
from xml.dom import minidom

print(f"Loading PAGE file {argv[1]}")
src_img = f"{argv[2]}/{argv[1].split('/')[-1].replace('.xml','.jpg')}"
print(f"Image is {src_img}")


# Parse the XML file
xmldoc = minidom.parse(argv[1])

textlines = xmldoc.getElementsByTagName('TextLine')
lines = []
boxes = []
for textline in textlines:
	lines.append(textline.getElementsByTagName('Baseline')[0].getAttribute('points'))
	boxes.append(textline.getElementsByTagName("Coords")[0].getAttribute("points"))

def get_vertexes(box : str) -> tuple[tuple[int,int],tuple[int,int],tuple[int,int],tuple[int,int]] :

	pairs : list[str] = box.split()

	vertex_a : tuple[int,int] = None
	vertex_b : tuple[int,int] = None
	vertex_c : tuple[int,int] = None
	vertex_d : tuple[int,int] = None

	prev : tuple[int,int]  = None
	current : tuple[int,int]  = None

	for i, p in enumerate(pairs):
		x, y = map(int, p.split(','))
		current = (x,y)
		if i == 0 :
			vertex_a = (x,y)
			prev = current
			continue

		if i == (len(pairs) -1 ) :
			vertex_d = (x,y)
			continue
		#print(f"is {prev[0]} greater than {current[0]}?")
		if prev[0] > current[0] :
			vertex_b = prev
			vertex_c = current

		prev = current
	#endFor
	return (vertex_a,vertex_b,vertex_c,vertex_d)
#endDef


frames = []

img = cv2.imread(src_img)

# Check if the image was loaded correctly
if img is None:
	print(f"Error: Could not load image at {image_path}")
else:
	# Convert the image to BGR for OpenCV
	img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
	
	for i, box in enumerate(boxes):
		coords = []
		for coord_pair in box.split():
			x, y = map(int, coord_pair.split(','))
			coords.append((x,y))

		verts = get_vertexes(box)
		if None in verts:
			continue
		#print(box)
		#print(verts)
		VA=0
		VB=1
		VC=2
		VD=3

		new_frame = img.copy()

		color_bgr = (255,0,0)
		#cv2.line(img, verts[VA], verts[VB], tuple(map(int, color_bgr)), 1)
		cv2.line(new_frame, verts[VA], verts[VC], tuple(map(int, color_bgr)), 1)
		cv2.line(new_frame, verts[VB], verts[VD], tuple(map(int, color_bgr)), 1)
		#cv2.line(img, verts[VC], verts[VD], tuple(map(int, color_bgr)), 1)

		split_top = coords[:coords.index(verts[VC])]
		split_bottom = coords[coords.index(verts[VC]):]

		for j in range(len(split_top) - 1):
			cv2.line(new_frame, split_top[j], split_top[j + 1], tuple(map(int, color_bgr)), 1)
		for j in range(len(split_bottom) - 1):
			cv2.line(new_frame, split_bottom[j], split_bottom[j + 1], tuple(map(int, color_bgr)), 1)
		frames.append(new_frame)


# Assuming 'frames' is a list of images (NumPy arrays)
fig, ax = plt.subplots()
fig.set_size_inches(8,10.31)
im = ax.imshow(frames[0]) # display the first frame

def animate_func(i):
    im.set_array(frames[i])
    return [im]

anim = animation.FuncAnimation(
    fig, 
    animate_func, 
    frames = len(frames),
    interval = 100, # in ms
    blit = True
)

outfile = f"data/anims/{argv[1].split('/')[-1].replace('.xml','.gif')}"
print(outfile)

anim.save(outfile, writer='ffmpeg',fps=60)
