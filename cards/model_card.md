---
license: apache-2.0
base_model: Qwen/Qwen3-VL-8B-Instruct
library_name: peft
pipeline_tag: image-text-to-text
datasets:
- ahd03/vln-synthetic-scenes
- leggedrobotics/navitrace
tags:
- navigation
- vision-language-navigation
- navitrace
- lora
- synthetic-data
---

# Masar

Masar takes a first-person outdoor photo and an instruction such as *"Go to the bench on the
left"* and returns the path a person would walk, as a list of points in the image.

It is a LoRA adapter for [Qwen3-VL-8B-Instruct](https://huggingface.co/Qwen/Qwen3-VL-8B-Instruct),
trained only on synthetic images rendered in Blender
([VLN Synthetic Scenes](https://huggingface.co/datasets/ahd03/vln-synthetic-scenes)).

## Results on NaviTrace (Human embodiment)

Scores on the 500 Human scenarios of the NaviTrace validation split, using NaviTrace's scoring code.
0 is walking straight ahead and 100 is the expert path.

| Category | Qwen3-VL-8B before training | Masar |
|---|---:|---:|
| **Overall** | **{{before.Overall}}** | **{{after.Overall}}** |
| Dynamic Obstacle | {{before.Dynamic Obstacle}} | {{after.Dynamic Obstacle}} |
| Stationary Obstacle | {{before.Stationary Obstacle}} | {{after.Stationary Obstacle}} |
| Semantic Terrain | {{before.Semantic Terrain}} | {{after.Semantic Terrain}} |
| Geometric Terrain | {{before.Geometric Terrain}} | {{after.Geometric Terrain}} |
| Accessibility | {{before.Accessibility}} | {{after.Accessibility}} |
| Visibility | {{before.Visibility}} | {{after.Visibility}} |
| Social Norms | {{before.Social Norms}} | {{after.Social Norms}} |

For reference, Human-only means on the NaviTrace leaderboard are 75.5 for a human expert, 35.4 for
Gemini 2.5 Pro, 21.1 for GPT-5 and 19.3 for Qwen3-VL-235B. Those are measured on the hidden test
split. Masar is measured on the validation split and has not been submitted.

## How to use

```python
import importlib.util
import torch
from huggingface_hub import hf_hub_download
from PIL import Image
from peft import PeftModel
from transformers import AutoProcessor, Qwen3VLForConditionalGeneration

base = "Qwen/Qwen3-VL-8B-Instruct"
processor = AutoProcessor.from_pretrained(base)
model = Qwen3VLForConditionalGeneration.from_pretrained(base, torch_dtype=torch.bfloat16, device_map="cuda")
model = PeftModel.from_pretrained(model, "ahd03/masar").eval()

# NaviTrace's prompts, the same ones used in training
spec = importlib.util.spec_from_file_location("prompts", hf_hub_download("ahd03/masar", "prompts.py"))
prompts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prompts)

image = Image.open("photo.jpg").convert("RGB")
image.thumbnail((896, 896))
messages = prompts.messages(image, "Go to the bench on the left")

text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
inputs = processor(text=[text], images=[image], return_tensors="pt").to("cuda")
out = model.generate(**inputs, max_new_tokens=256, do_sample=False)
print(processor.batch_decode(out[:, inputs["input_ids"].shape[1]:], skip_special_tokens=True)[0])
# [[0.500, 0.950], [0.470, 0.880], ..., [0.310, 0.560]]   x, y from 0 to 1, origin top-left
```

## Training

| Setting | Value |
|---|---|
| Base model | Qwen3-VL-8B-Instruct, vision encoder frozen |
| Adapter | LoRA rank 16, alpha 32, dropout 0.05, on the language model's attention and MLP projections |
| Data | VLN Synthetic Scenes, train split ({{dataset.train}} samples) |
| Optimisation | 2 epochs, learning rate 1e-4 with cosine decay, batch 16, bf16, images at 896 px |
| Prompts | NaviTrace's system and user prompts |

## Limitations

- Human embodiment only.
- Trained on rendered scenes with simple people and static traffic. Social Norms is the weakest category.
- Single-image input, no memory of earlier frames.
