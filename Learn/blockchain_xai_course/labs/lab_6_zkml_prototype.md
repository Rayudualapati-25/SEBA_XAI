# Lab 6 — zkML Prototype with EZKL

**Goal**: prove (in zero-knowledge) that a small neural network's MNIST inference was performed correctly. Then commit the explanation hash on-chain.

**Time**: ~8 hours (most of it is one-time setup and proving wait).

**Prereqs**:
```
pip install torch torchvision ezkl onnx onnxruntime
```

EZKL must be installed natively:
```
curl https://raw.githubusercontent.com/zkonduit/ezkl/main/install_ezkl_cli.sh | bash
```

---

## Step 1 — Train a tiny MLP

```python
import torch, torch.nn as nn
from torchvision import datasets, transforms
from torch.utils.data import DataLoader

tx = transforms.Compose([transforms.ToTensor(), transforms.Lambda(lambda x: x.view(-1))])
tr = DataLoader(datasets.MNIST(".", train=True, download=True, transform=tx), batch_size=128, shuffle=True)

class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(784, 32)
        self.fc2 = nn.Linear(32, 10)
    def forward(self, x):
        return self.fc2(torch.relu(self.fc1(x)))

net = Net()
opt = torch.optim.Adam(net.parameters(), 1e-3)
loss_fn = nn.CrossEntropyLoss()

for epoch in range(2):
    for x, y in tr:
        opt.zero_grad()
        loss = loss_fn(net(x), y)
        loss.backward()
        opt.step()

torch.save(net.state_dict(), "net.pt")
```

## Step 2 — Export to ONNX

```python
sample = torch.randn(1, 784)
torch.onnx.export(net, sample, "net.onnx",
                  input_names=["input"], output_names=["output"],
                  dynamic_axes={"input": {0: "batch"}, "output": {0: "batch"}},
                  opset_version=13)
```

Verify with `onnxruntime`:
```python
import onnxruntime as ort
sess = ort.InferenceSession("net.onnx")
print(sess.run(None, {"input": sample.numpy()})[0])
```

## Step 3 — EZKL pipeline

Create `input.json` with one MNIST sample (flattened, normalized to [0,1]):

```python
import json
from torchvision import datasets
dset = datasets.MNIST(".", train=False, download=True, transform=transforms.ToTensor())
x, y = dset[0]
x_flat = x.view(-1).tolist()
json.dump({"input_data": [x_flat]}, open("input.json", "w"))
```

Then run EZKL:
```
ezkl gen-settings -M net.onnx -O settings.json
ezkl calibrate-settings -M net.onnx -D input.json -O settings.json --target=resources
ezkl compile-circuit -M net.onnx --compiled-circuit net.compiled -S settings.json
ezkl get-srs -S settings.json
ezkl setup -M net.compiled --vk-path vk.key --pk-path pk.key
ezkl gen-witness -D input.json -M net.compiled --witness witness.json
ezkl prove --witness witness.json -M net.compiled --pk-path pk.key --proof-path proof.json
ezkl verify --proof-path proof.json --vk-path vk.key -S settings.json
```

Last line should print `verified: true`.

## Step 4 — Measure

```bash
ls -lh proof.json     # proof size (KB)
time ezkl prove ...   # prover time
```

Typical for this tiny network: a few hundred KB proof, tens of seconds prover time on a laptop.

## Step 5 — On-chain verifier

Generate Solidity verifier:
```
ezkl create-evm-verifier -S settings.json --vk-path vk.key --sol-code-path Verifier.sol
```

Deploy with Foundry:
```
forge create Verifier.sol:Halo2Verifier --rpc-url $SEPOLIA_RPC --private-key $PK
```

Call `verifyProof()` with the proof bytes. Record the gas cost.

## Step 6 — Commit explanation hash

Compute SHAP for the same input off-chain:
```python
import shap, torch, numpy as np
background = torch.randn(50, 784)
explainer = shap.DeepExplainer(net, background)
phi = explainer.shap_values(torch.tensor(x_flat).unsqueeze(0))
```

Hash the explanation:
```python
import hashlib
phi_bytes = np.array(phi).tobytes()
explanation_hash = hashlib.sha256(phi_bytes).hexdigest()
```

Commit on Sepolia in a one-off contract:
```solidity
contract Registry {
    event Committed(bytes32 inputHash, bytes32 modelHash, bytes32 explanationHash);
    function commit(bytes32 i, bytes32 m, bytes32 e) external {
        emit Committed(i, m, e);
    }
}
```

Anyone can later verify (off-chain) that a published SHAP matches the committed hash.

## Step 7 — Reflect

In your journal:
- Time and gas costs at each step.
- What would change to scale to ResNet-50? (Hint: orders of magnitude more constraints.)
- What's the trust model? Who verifies what?
- What's missing for **provable** explanations (vs only provable inference)?

---

## Deliverable

- `net.pt`, `net.onnx`, `settings.json`, `proof.json`, `Verifier.sol`.
- Sepolia tx hash of the successful verification.
- Sepolia tx hash of the `Registry.commit()` call.
- 2-page write-up.

## Stretch

- Use **Risc Zero** instead of EZKL: write the inference as Rust + tract, generate STARK.
- Implement a tiny SHAP computation inside the zk circuit (very hard; this is open research).
- Benchmark proving time as you scale the MLP hidden dim from 32 → 128 → 512.
- Add input privacy: hide the MNIST image, prove only the *class*.
