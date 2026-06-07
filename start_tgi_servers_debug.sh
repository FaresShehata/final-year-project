#!/bin/bash

# Share cache directory
volume=./tmp/fastdata/hfcache/transformers/
# HF token
token=$(cat ${HOME}/.config/huggingface/token)

# StarCoder: 8192, GPUs 0,1
#port=8192
#model=bigcode/starcoder
#docker run -d -e HUGGING_FACE_HUB_TOKEN=$token --gpus '"device=0,1"' --shm-size 1g \
#    -p ${port}:80 -v $volume:/data ghcr.io/huggingface/text-generation-inference:latest \
#    --model-id $model --trust-remote-code --dtype bfloat16 --sharded true --num-shard 2 \
#    --max-total-tokens 8192 --max-input-length 8000 --max-batch-prefill-tokens 8000

# Code Llama: 8193, GPUs 2,3
INPUT_TOKEN=2000
port=8192
model=Qwen/Qwen2.5-Coder-1.5B

# Remove any stale container from a previous (possibly crashed) run so the
# named `docker run` below doesn't fail with "name already in use". We
# deliberately do NOT pass --rm: keeping the container around after it exits
# means `docker logs tgi-server` survives for post-mortem if TGI dies mid-run.
docker rm -f "${DOCKER_NAME:-tgi-server}" >/dev/null 2>&1 || true

# --cuda-memory-fraction 0.8: leave VRAM headroom. This GPU also drives the
# desktop, so TGI must not grab 100% of memory (the default) for its KV cache
# -- otherwise desktop VRAM growth mid-run triggers a CUDA OOM that kills the
# shard and takes the whole synthesis run down with it.
docker run --name="${DOCKER_NAME:-tgi-server}" --gpus all -e HUGGING_FACE_HUB_TOKEN=$token --shm-size 1g \
    -p ${port}:80 -v $volume:/data ghcr.io/huggingface/text-generation-inference:3.3.4 \
    --model-id $model --trust-remote-code --dtype bfloat16 --cuda-memory-fraction 0.8 \
    --max-total-tokens 8192 --max-input-length $INPUT_TOKEN --max-batch-prefill-tokens $INPUT_TOKEN
