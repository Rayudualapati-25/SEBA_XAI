# Lab 1 — Build a Toy Blockchain in Python

**Goal**: implement, from scratch, the smallest blockchain that demonstrates hashing, signing, Merkle roots, and tamper detection.

**Time**: ~4 hours.

**Prereqs**: Python 3.10+, `hashlib`, `ecdsa` (`pip install ecdsa`).

---

## Step 1 — Wallet

```python
from ecdsa import SigningKey, SECP256k1
import hashlib, json

class Wallet:
    def __init__(self):
        self.sk = SigningKey.generate(curve=SECP256k1)
        self.vk = self.sk.get_verifying_key()
        self.pubkey = self.vk.to_string().hex()
        self.address = hashlib.sha256(self.pubkey.encode()).hexdigest()[:40]

    def sign(self, msg: bytes) -> bytes:
        return self.sk.sign(msg)

    def verify(self, msg: bytes, sig: bytes) -> bool:
        try:
            return self.vk.verify(sig, msg)
        except: return False
```

## Step 2 — Transaction

```python
class Transaction:
    def __init__(self, sender_pub, recipient_addr, amount, signature=None):
        self.sender_pub = sender_pub
        self.recipient_addr = recipient_addr
        self.amount = amount
        self.signature = signature

    def payload(self) -> bytes:
        return json.dumps({
            "from": self.sender_pub, "to": self.recipient_addr, "amt": self.amount
        }, sort_keys=True).encode()

    def is_valid(self) -> bool:
        from ecdsa import VerifyingKey
        vk = VerifyingKey.from_string(bytes.fromhex(self.sender_pub), curve=SECP256k1)
        try: return vk.verify(self.signature, self.payload())
        except: return False
```

## Step 3 — Merkle root

```python
def merkle_root(tx_hashes):
    if not tx_hashes: return b"\0" * 32
    layer = tx_hashes[:]
    while len(layer) > 1:
        if len(layer) % 2: layer.append(layer[-1])
        layer = [hashlib.sha256(layer[i] + layer[i+1]).digest()
                 for i in range(0, len(layer), 2)]
    return layer[0]
```

## Step 4 — Block

```python
import time
class Block:
    def __init__(self, prev_hash, txs, nonce=0):
        self.prev_hash = prev_hash
        self.txs = txs
        self.timestamp = int(time.time())
        self.nonce = nonce
        tx_hashes = [hashlib.sha256(tx.payload()).digest() for tx in txs]
        self.merkle = merkle_root(tx_hashes)

    def header(self) -> bytes:
        return self.prev_hash + self.merkle + self.timestamp.to_bytes(8, "big") + self.nonce.to_bytes(8, "big")

    def hash(self) -> bytes:
        return hashlib.sha256(self.header()).digest()
```

## Step 5 — Chain + verification

```python
class Chain:
    def __init__(self):
        self.blocks = [Block(b"\0"*32, [])]  # genesis

    def add(self, txs):
        prev = self.blocks[-1].hash()
        block = Block(prev, txs)
        self.blocks.append(block)

    def verify(self) -> bool:
        for i in range(1, len(self.blocks)):
            if self.blocks[i].prev_hash != self.blocks[i-1].hash():
                return False
            for tx in self.blocks[i].txs:
                if not tx.is_valid(): return False
        return True
```

## Step 6 — Tamper detection demo

```python
alice, bob = Wallet(), Wallet()
chain = Chain()
for i in range(5):
    tx = Transaction(alice.pubkey, bob.address, i)
    tx.signature = alice.sign(tx.payload())
    chain.add([tx])

assert chain.verify()
print("chain valid")

# tamper:
chain.blocks[2].txs[0].amount = 999
print("after tamper:", chain.verify())  # False
```

---

## Deliverable

- `toy_chain.py` — ~150 lines.
- A printed demo showing valid chain → tampering → invalid chain.
- A 1-paragraph reflection: which property does this demonstrate (integrity / authentication / tamper-evidence)?

## Stretch

- Add Proof-of-Work: block header must hash below a target.
- Add longest-chain rule for fork resolution.
- Add a tiny P2P layer with `asyncio`.
