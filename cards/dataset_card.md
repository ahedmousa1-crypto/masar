# VLN Synthetic Scenes

{{dataset.total}} synthetic first-person outdoor images with ground-truth walking paths for the Human
embodiment, in the format of [NaviTrace](https://huggingface.co/datasets/leggedrobotics/navitrace).
The scenes are built procedurally in Blender (streets, an old town, a campus). Each path is computed
from the 3D scene by a route planner.

![A sample with its path drawn](https://huggingface.co/datasets/ahd03/vln-synthetic-scenes/resolve/main/assets/sample.jpg)

The model trained on this data is [ahd03/masar](https://huggingface.co/ahd03/masar). The code is
at https://github.com/ahedmousa1-crypto/masar.

## Load it

```python
from datasets import load_dataset
ds = load_dataset("ahd03/vln-synthetic-scenes")
```

## Contents

| Split | Samples |
|---|---:|
| Train | {{dataset.train}} |
| Test | {{dataset.test}} |

- **Tasks.** {{dataset.goal}} Goal tasks ("Walk to the bike rack ahead") and {{dataset.directions}} Directions tasks ("Go
  straight for about 10 metres, then bear left").
- **Paths.** 6 to 15 pixel points per path, starting at the bottom centre of the image. A goal
  reached by both stairs and a ramp lists both paths.
- **Lighting.** Day 55%, overcast 15%, dusk 15%, night 10%, moonlight 5%.
- **Test split.** Whole areas of each scene are held out, so no test view is near a training view.

## Fields

Same columns as NaviTrace, `sample_id`, `task`, `embodiments`, `image` (1365 x 1024),
`segmentation_mask`, `ground_truth`, `category`, `context` and `metadata`.

- `segmentation_mask` is a grayscale PNG of 74 class ids. The id-to-name map is in the repository
  (`blender/worldlib/classes.py`).
- Only `ground_truth["Human"]` is filled. Traces are pixel `[x, y]` with a top-left origin.
- `synthetic` (JSON) holds the camera pose, lighting, target object and the path in 3D.

## Limitations

- Rendered images. Geometry is simple and people are simple figures.
- Scenes are static. People, cars and animals do not move.
- Human embodiment only.

## License and credits

CC BY 4.0. Built with Blender. Animal meshes from Quaternius (CC0). Skies and textures from Poly
Haven (CC0). Format, prompts and categories follow NaviTrace (Windecker et al., 2025, arXiv 2510.26909).
