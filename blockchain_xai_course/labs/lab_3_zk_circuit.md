# Lab 3 — Your First ZK Circuit

**Goal**: write, compile, and verify a Circom-based zk-SNARK that proves "I know `x` such that `x*x = 25`" without revealing `x`. Then deploy the verifier to Sepolia.

**Time**: ~4 hours.

**Prereqs**:
```
npm i -g circom snarkjs
```

You'll also need Node 18+, a funded Sepolia address (~0.05 ETH), and a wallet (Metamask or Foundry's `cast`).

---

## Step 1 — The circuit

`square.circom`:

```
pragma circom 2.1.4;

template Square() {
    signal input x;       // private witness
    signal input y;       // public input
    signal product;

    product <== x * x;
    y === product;
}

component main { public [y] } = Square();
```

Compile:
```
circom square.circom --r1cs --wasm --sym
```

## Step 2 — Trusted setup (Powers of Tau + Groth16)

```bash
snarkjs powersoftau new bn128 12 pot12_0000.ptau -v
snarkjs powersoftau contribute pot12_0000.ptau pot12_0001.ptau --name="me" -v
snarkjs powersoftau prepare phase2 pot12_0001.ptau pot12_final.ptau -v
snarkjs groth16 setup square.r1cs pot12_final.ptau square_0000.zkey
snarkjs zkey contribute square_0000.zkey square_final.zkey --name="me" -v
snarkjs zkey export verificationkey square_final.zkey verification_key.json
```

## Step 3 — Generate witness + proof

`input.json`:
```json
{ "x": 5, "y": 25 }
```

```bash
node square_js/generate_witness.js square_js/square.wasm input.json witness.wtns
snarkjs groth16 prove square_final.zkey witness.wtns proof.json public.json
snarkjs groth16 verify verification_key.json public.json proof.json
```

You should see `OK!`.

Now try with `{ "x": -5, "y": 25 }` (sign flips in the field). Still verifies — that's the zero-knowledge point: from `y=25`, the verifier can't tell whether `x=5` or `x=-5`.

## Step 4 — Solidity verifier

```bash
snarkjs zkey export solidityverifier square_final.zkey Verifier.sol
snarkjs zkey export soliditycalldata public.json proof.json
```

Copy the resulting calldata. Deploy `Verifier.sol` to Sepolia via Foundry:

```bash
forge create Verifier.sol:Groth16Verifier --rpc-url $SEPOLIA_RPC --private-key $PK
```

Call `verifyProof()` via `cast`:
```bash
cast call $VERIFIER "verifyProof(uint256[2],uint256[2][2],uint256[2],uint256[1])(bool)" \
  $PI_A_HEX $PI_B_HEX $PI_C_HEX $PUBLIC_INPUTS --rpc-url $SEPOLIA_RPC
```

Returns `true`.

## Step 5 — Reflect

In your journal:
- Why does this construction reveal `y` but not `x`?
- How would you extend it to prove "I know `(p, q)` such that `p*q = n` without revealing the factors"? (Hint: factoring is a one-way function — this is the kind of statement RSA-based ZK proofs use.)
- What does it cost in Sepolia gas to verify?

---

## Deliverable

- `square.circom`, `proof.json`, `public.json`, `Verifier.sol`.
- Sepolia tx hash of the successful `verifyProof()` call.
- 1-page journal entry.

## Stretch

1. Replace Groth16 with PLONK:
```bash
snarkjs plonk setup square.r1cs pot12_final.ptau square_plonk.zkey
snarkjs plonk prove square_plonk.zkey witness.wtns proof.json public.json
```
Compare proof sizes and verifier gas.

2. Build a Merkle-inclusion circuit using `circomlib`'s Poseidon hash. Prove that "I know a leaf and its path that produces this Merkle root" — the building block of Tornado Cash, zk identity, and rollups.
