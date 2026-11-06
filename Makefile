.PHONY: all stills video clean
all:
	./generate.sh
stills:
	blender --background --python source/blender/01_code_to_form.py
	blender --background --python source/blender/02_recursive_courtyard.py
	blender --background --python source/blender/03_aframe_monument.py
video:
	blender --background --python source/blender/04_assemble_video.py
	ffmpeg -y -framerate 12 -i output/videos/frames_assemble/frame_%04d.png \
	  -c:v libx264 -pix_fmt yuv420p -crf 18 -movflags +faststart \
	  output/videos/04-code-assemble.mp4
clean:
	rm -rf output/images/* output/videos/* output/previews/*

score:
	./pipeline/score_assemble.sh

v2:
	blender --background --python source/blender/01_code_to_form_v2.py
	blender --background --python source/blender/02_recursive_courtyard_v2.py
	blender --background --python source/blender/03_aframe_monument_v2.py
	blender --background --python source/blender/05_courtyard_grow.py
	./pipeline/score_courtyard_grow.sh

final:
	./pipeline/generate_final.sh

score-final:
	./pipeline/score_final.sh
