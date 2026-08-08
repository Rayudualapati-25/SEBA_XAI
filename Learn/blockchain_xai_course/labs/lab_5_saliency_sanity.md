# Lab 5 — Saliency Methods + Sanity Checks

**Goal**: implement vanilla saliency, SmoothGrad, Integrated Gradients, and Grad-CAM on a pretrained ResNet-50. Then run Adebayo's sanity checks. Discover which methods are faithful and which are decorative.

**Time**: ~4 hours.

**Prereqs**:
```
pip install torch torchvision matplotlib pillow opencv-python
```

---

## Step 1 — Setup

```python
import torch, torchvision
from torchvision.models import resnet50, ResNet50_Weights
from PIL import Image
from torchvision import transforms
import numpy as np, matplotlib.pyplot as plt

weights = ResNet50_Weights.IMAGENET1K_V2
model = resnet50(weights=weights).eval()
preprocess = weights.transforms()

img = Image.open("cat.jpg").convert("RGB")
x = preprocess(img).unsqueeze(0)
logits = model(x)
pred = logits.argmax(1).item()
print("predicted:", weights.meta["categories"][pred])
```

(Any ImageNet-class image works.)

## Step 2 — Vanilla saliency

```python
def saliency(model, x, class_idx):
    x = x.clone().requires_grad_(True)
    out = model(x)
    out[0, class_idx].backward()
    return x.grad.abs().max(1)[0][0].numpy()  # H × W
```

## Step 3 — SmoothGrad

```python
def smoothgrad(model, x, class_idx, n=30, sigma=0.15):
    grads = []
    for _ in range(n):
        noise = torch.randn_like(x) * sigma
        x_noisy = (x + noise).clone().requires_grad_(True)
        out = model(x_noisy)
        out[0, class_idx].backward()
        grads.append(x_noisy.grad.abs().max(1)[0][0].numpy())
    return np.mean(grads, axis=0)
```

## Step 4 — Integrated Gradients

```python
def integrated_gradients(model, x, class_idx, steps=50, baseline=None):
    if baseline is None: baseline = torch.zeros_like(x)
    alphas = torch.linspace(0, 1, steps).view(-1, 1, 1, 1)
    interps = baseline + alphas * (x - baseline)  # steps × C × H × W
    interps.requires_grad_(True)
    out = model(interps)
    g = torch.autograd.grad(out[:, class_idx].sum(), interps)[0]  # steps × C × H × W
    avg = g.mean(0, keepdim=True)
    ig = (x - baseline) * avg
    return ig.abs().max(1)[0][0].numpy()
```

## Step 5 — Grad-CAM

```python
def grad_cam(model, x, class_idx, target_layer):
    features, grads = [], []
    def fhook(_m, _i, o): features.append(o)
    def bhook(_m, _gi, go): grads.append(go[0])
    fh = target_layer.register_forward_hook(fhook)
    bh = target_layer.register_full_backward_hook(bhook)

    out = model(x)
    model.zero_grad()
    out[0, class_idx].backward()
    fh.remove(); bh.remove()

    A = features[0][0]                  # C × h × w
    grad = grads[0][0]                  # C × h × w
    weights = grad.mean(dim=(1, 2))     # C
    cam = torch.relu((weights[:, None, None] * A).sum(0)).cpu().numpy()
    cam = cam / (cam.max() + 1e-9)
    return cam

# Target layer for ResNet-50: layer4
cam = grad_cam(model, x, pred, model.layer4[-1])
```

## Step 6 — Visualize all four

```python
maps = {
    "saliency": saliency(model, x, pred),
    "smoothgrad": smoothgrad(model, x, pred),
    "ig": integrated_gradients(model, x, pred),
    "gradcam": cam,
}
fig, axs = plt.subplots(1, 5, figsize=(20, 4))
axs[0].imshow(img); axs[0].set_title("input")
for ax, (name, m) in zip(axs[1:], maps.items()):
    ax.imshow(m, cmap="hot"); ax.set_title(name)
plt.savefig("saliency_compare.png")
```

## Step 7 — Adebayo sanity check: model randomization

```python
def randomize_top_layers(model, layers_to_randomize):
    """Re-initialize the named layers."""
    import copy
    m = copy.deepcopy(model)
    for n, p in m.named_parameters():
        if any(layer in n for layer in layers_to_randomize):
            torch.nn.init.normal_(p) if p.dim() > 1 else torch.nn.init.zeros_(p)
    return m.eval()

m_rand = randomize_top_layers(model, ["fc", "layer4"])

cam_rand = grad_cam(m_rand, x, pred, m_rand.layer4[-1])
ig_rand  = integrated_gradients(m_rand, x, pred)

# Plot side-by-side: original vs randomized
# A faithful method should produce very different maps.
```

Compute the **structural similarity (SSIM)** between the original and randomized maps:

```python
from skimage.metrics import structural_similarity as ssim
print("Grad-CAM SSIM:", ssim(maps["gradcam"], cam_rand, data_range=cam_rand.max()-cam_rand.min()))
print("IG SSIM:", ssim(maps["ig"], ig_rand, data_range=ig_rand.max()-ig_rand.min()))
```

Higher SSIM = less change = less faithful. (Adebayo et al. report Guided BP / Guided Grad-CAM as high-SSIM = failing.)

## Step 8 — Build the comparison table

| Method | Visual quality | SSIM (lower=better) | Notes |
|---|---|---|---|
| Vanilla saliency | noisy | low | passes |
| SmoothGrad | cleaner | low | passes |
| Integrated Gradients | cleanest | low | passes axiomatically |
| Grad-CAM | smooth, low-res | medium | passes class-discriminative test |

(Numbers will depend on your specific image.)

---

## Deliverable

- `saliency_methods.py` (~150 lines).
- `saliency_compare.png` and `saliency_sanity.png`.
- A markdown table summarizing visual quality, SSIM, and your judgment of faithfulness.

## Stretch

- Implement **Guided Backprop** and **Guided Grad-CAM**. Run the sanity check. Confirm they fail.
- Add a **data randomization** test: train a small CNN on permuted CIFAR-10 labels, compare saliency to the correctly-trained model.
- Use the `quantus` library to compute faithfulness, sensitivity, and stability metrics.
