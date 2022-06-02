docker run -it \
--name container-local-api \
-v "$(pwd):/home/app" \
-p 4000:4000 \
-e PORT=4000 \
image-local-deepfood-model-api