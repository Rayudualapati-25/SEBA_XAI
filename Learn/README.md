# Learn

Study material and reference documentation. **Nothing here is part of the
SEBA-XAI research project** — no code, results, or text from this folder appears
in the paper.

| Folder | What it is | Size |
|---|---|---|
| `solidity-practice/` | Solidity/Ethereum learning track: Hardhat plus practice contracts (HelloWorld, Counter, Calculator, Ownable, PiggyBank, Voting, SimpleToken, SimpleStorage). Was `seba_fabric_workspace/sol/` | 467 MB |
| `blockchain_xai_course/` | Course notes, syllabus and generated PDFs for the blockchain and XAI course | 10 MB |
| `fabric-docs/` | Offline copy of the Hyperledger Fabric release-2.5 documentation, ~120 pages. Handy for grepping, re-downloadable | 37 MB |

Most of the 515 MB is `node_modules` inside `solidity-practice/`, which is
reinstallable with `npm install`.

## Why Solidity is here and not in the project

The research system is **Hyperledger Fabric**, whose smart contracts (chaincode)
are JavaScript. Fabric has no EVM, so Solidity cannot run in it. The Solidity
work is separate coursework and shares no code with the paper.

## What did NOT move, and must not

`seba_fabric_workspace/fabric-samples/` looks like downloadable reference
material, but it is a **live dependency** of the running network:

- `fabric-samples/bin/` holds the `peer`, `orderer`, `configtxgen`, `osnadmin`
  and `fabric-ca-client` binaries that every script puts on `PATH`
- `fabric-samples/config/` is **bind-mounted into all five peer containers**

Moving it breaks the running network and every script. It stays where it is.

## References updated when these folders moved

- `scripts/create_all_in_one_pdf.py` — 41 course paths now point at `Learn/blockchain_xai_course/`
- `seba_fabric_workspace/SETUP.md` — the offline-docs paths now point at `../Learn/fabric-docs/`
