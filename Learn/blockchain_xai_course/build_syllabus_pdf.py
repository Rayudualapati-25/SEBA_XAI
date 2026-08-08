"""
Generate SRM University-AP style course syllabus PDFs for:
  - Blockchain Technologies
  - Explainable Artificial Intelligence

Format matches FINAL_NLP_Syllabus.pdf layout:
  - University header / address
  - Course info table (Code, Category, L-T-P-C, etc.)
  - Course Objectives (CLRs) — numbered
  - Course Outcomes (CLOs) — table with Bloom's Level
  - Course Articulation Matrix (CLO -> PLO)
  - Course Utilization Plan - Theory (Units x topics x hours)
  - Course Utilization Plan - In-Class Projects
  - Recommended Resources / Other Resources
  - Learning Assessment table
"""
from __future__ import annotations
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT


ROOT = Path(__file__).resolve().parent

# ---------- shared styles ----------
styles = getSampleStyleSheet()
H_UNIV = ParagraphStyle("HUniv", parent=styles["Normal"], fontName="Times-Bold",
                        fontSize=12, alignment=TA_CENTER, spaceAfter=0)
H_ADDR = ParagraphStyle("HAddr", parent=styles["Normal"], fontName="Times-Roman",
                        fontSize=10, alignment=TA_CENTER, spaceAfter=2)
H_TITLE = ParagraphStyle("HTitle", parent=styles["Normal"], fontName="Times-Bold",
                         fontSize=11.5, alignment=TA_CENTER, spaceAfter=4, spaceBefore=6)
H_SECTION = ParagraphStyle("HSec", parent=styles["Normal"], fontName="Times-Bold",
                           fontSize=10.5, alignment=TA_LEFT, spaceAfter=4, spaceBefore=8)
P_BODY = ParagraphStyle("PBody", parent=styles["Normal"], fontName="Times-Roman",
                        fontSize=10, leading=12.5, alignment=TA_LEFT, spaceAfter=2)
P_TBL = ParagraphStyle("PTbl", parent=styles["Normal"], fontName="Times-Roman",
                       fontSize=9, leading=11, alignment=TA_LEFT)
P_TBL_C = ParagraphStyle("PTblC", parent=P_TBL, alignment=TA_CENTER)
P_TBL_B = ParagraphStyle("PTblB", parent=P_TBL, fontName="Times-Bold")
P_TBL_BC = ParagraphStyle("PTblBC", parent=P_TBL_B, alignment=TA_CENTER)
P_OBJ = ParagraphStyle("PObj", parent=P_BODY, leftIndent=10)


def header_block():
    return [
        Paragraph("SRM University – AP, Andhra Pradesh", H_UNIV),
        Paragraph("Neeru Konda, Mangalagiri Mandal", H_ADDR),
        Paragraph("Guntur District, Mangalagiri, Andhra Pradesh 522240", H_ADDR),
        Spacer(1, 6),
    ]


def course_info_table(name: str, code: str) -> Table:
    title = Paragraph(f"<b>Name of the Course: {name}</b>", H_TITLE)
    data = [
        ["Course Code", code, "Course Category",
         Paragraph("Core<br/>Elective<br/>(CW)", P_TBL_BC),
         "L-T-P-C", "3", "0", "0", "3"],
        ["Pre-Requisite\nCourse(s)", "", "Co-Requisite\nCourse(s)", "", "Progressive\nCourse(s)", "", "", "", ""],
        ["Course\nOffering\nDepartment", "CSE", "Professional /\nLicensing\nStandards", "", "", "", "", "", ""],
    ]
    t = Table(data, colWidths=[2.4*cm, 1.8*cm, 2.6*cm, 2.0*cm, 2.2*cm,
                                0.7*cm, 0.7*cm, 0.7*cm, 0.7*cm])
    style = TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.6, colors.black),
        ("FONT", (0, 0), (-1, -1), "Times-Roman", 9.5),
        ("FONT", (1, 0), (1, 0), "Times-Bold", 9.5),
        ("FONT", (1, 2), (1, 2), "Times-Bold", 9.5),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (5, 0), (-1, 0), "CENTER"),
        ("SPAN", (3, 1), (3, 1)),  # placeholder
    ])
    t.setStyle(style)
    return [title, t]


def objectives_block(objectives: list[str]) -> list:
    out = [Paragraph("<b>Course Objectives / Course Learning Rationales (CLRs)</b>", H_SECTION)]
    for i, obj in enumerate(objectives, 1):
        out.append(Paragraph(f"<b>Objective {i}.</b> {obj}", P_OBJ))
    return out


def outcomes_table(outcomes: list[tuple[str, int, int, int]]) -> list:
    """outcomes: list of (description, bloom_level, proficiency_pct, attainment_pct)"""
    header = [
        "",
        Paragraph("<b>At the end of the course the learner will be able to</b>", P_TBL_BC),
        Paragraph("<b>Bloom's Level</b>", P_TBL_BC),
        Paragraph("<b>Expected Proficiency Percentage</b>", P_TBL_BC),
        Paragraph("<b>Expected Attainment Percentage</b>", P_TBL_BC),
    ]
    rows = [header]
    for i, (desc, bl, prof, attn) in enumerate(outcomes, 1):
        rows.append([
            Paragraph(f"<b>Outcome {i}</b>", P_TBL_BC),
            Paragraph(desc, P_TBL),
            Paragraph(str(bl), P_TBL_C),
            Paragraph(f"{prof}%", P_TBL_C),
            Paragraph(f"{attn}%", P_TBL_C),
        ])
    t = Table(rows, colWidths=[1.6*cm, 7.4*cm, 1.6*cm, 2.6*cm, 2.6*cm])
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.6, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef2f6")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    return [Paragraph("<b>Course Outcomes / Course Learning Outcomes (CLOs)</b>", H_SECTION), t]


def articulation_matrix(matrix_rows: list[list[str]]) -> list:
    """
    matrix_rows: 5 rows (Outcome 1..4, Course Average).
                 Each row is 12 cells of strings (PLO1..PLO11 omitted columns 7-9
                 because the NLP PDF leaves Ethics/Comm/Lifelong blank).
    """
    plo_headers_top = [
        "Engineering Knowledge",
        "Design / Development of Solutions",
        "Conduct Investigations of Complex Problems",
        "Conduct Investigations of Complex Problems",
        "Modern Tool Usage",
        "The Engineer and Society",
        "Environment and Sustainability",
        "Ethics",
        "Individual and Team Work",
        "Communication",
        "Life-long Learning",
        "PSO 1", "PSO 2", "PSO 3",
    ]
    header_top = [Paragraph(f"<b>{h}</b>", ParagraphStyle("rot", parent=P_TBL_BC, fontSize=7, leading=8)) for h in plo_headers_top]
    rows = [
        [Paragraph("<b>CLOs</b>", P_TBL_BC)] + header_top
    ]
    for label, cells in matrix_rows:
        label_para = label if isinstance(label, Paragraph) else Paragraph(label, P_TBL_BC)
        row = [label_para] + [Paragraph(c if c else "", P_TBL_C) for c in cells]
        rows.append(row)
    col_w = [1.4*cm] + [0.9*cm]*14
    t = Table(rows, colWidths=col_w, repeatRows=1)
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef2f6")),
        ("FONT", (0, 0), (-1, -1), "Times-Roman", 7),
    ]))
    return [Paragraph("<b>Course Articulation Matrix (CLO) to Program Learning Outcomes (PLO)</b>",
                      H_SECTION), t]


def utilization_table(units: list[dict]) -> list:
    """
    units: list of dicts:
       { 'name': 'Unit 1', 'hours': 9, 'rows': [(topic, hrs, clos, refs), ...] }
    """
    header = [
        Paragraph("<b>Unit No.</b>", P_TBL_BC),
        Paragraph("<b>Unit Name</b>", P_TBL_BC),
        Paragraph("<b>Required Contact Hours</b>", P_TBL_BC),
        Paragraph("<b>CLOs Addressed</b>", P_TBL_BC),
        Paragraph("<b>References Used</b>", P_TBL_BC),
    ]
    rows = [header]
    total = 0
    for u in units:
        # unit header row
        rows.append([
            Paragraph(f"<b>{u['name']}</b>", P_TBL_BC),
            Paragraph("", P_TBL),
            Paragraph(f"<b>{u['hours']}</b>", P_TBL_BC),
            Paragraph("", P_TBL),
            Paragraph("", P_TBL),
        ])
        total += u["hours"]
        for topic, hrs, clos, refs in u["rows"]:
            rows.append([
                Paragraph("", P_TBL),
                Paragraph(topic, P_TBL),
                Paragraph(str(hrs), P_TBL_C),
                Paragraph(clos, P_TBL_C),
                Paragraph(refs, P_TBL_C),
            ])
    rows.append([
        Paragraph("", P_TBL),
        Paragraph("<b>Total Contact Hours</b>", P_TBL_BC),
        Paragraph(f"<b>{total}</b>", P_TBL_BC),
        Paragraph("", P_TBL),
        Paragraph("", P_TBL),
    ])
    col_w = [1.6*cm, 9.2*cm, 2.0*cm, 2.0*cm, 2.0*cm]
    t = Table(rows, colWidths=col_w, repeatRows=1)
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef2f6")),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return [Paragraph("<b>Course Utilization Plan - Theory</b>", H_SECTION), t]


def experiments_table(experiments: list[tuple[str, str, str]]) -> list:
    header = [
        Paragraph("<b>Exp No.</b>", P_TBL_BC),
        Paragraph("<b>Experiment Name</b>", P_TBL_BC),
        Paragraph("<b>CLOs Addressed</b>", P_TBL_BC),
        Paragraph("<b>References Used</b>", P_TBL_BC),
    ]
    rows = [header]
    for i, (name, clos, refs) in enumerate(experiments, 1):
        rows.append([
            Paragraph(str(i), P_TBL_C),
            Paragraph(name, P_TBL),
            Paragraph(clos, P_TBL_C),
            Paragraph(refs, P_TBL_C),
        ])
    col_w = [1.4*cm, 11.0*cm, 2.0*cm, 2.4*cm]
    t = Table(rows, colWidths=col_w, repeatRows=1)
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef2f6")),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    return [Paragraph("<b>Course Utilization Plan – Suggested In-Class Projects</b>", H_SECTION), t]


def resources_block(recommended: list[str], other: list[str]) -> list:
    out = []
    rec_lines = "<br/>".join(f"{i+1}. {r}" for i, r in enumerate(recommended))
    other_lines = "<br/>".join(f"{i+1}. {r}" for i, r in enumerate(other))
    t = Table(
        [[Paragraph(f"<b>Recommended Resources</b><br/>{rec_lines}", P_TBL)]],
        colWidths=[16.8*cm])
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.6, colors.black),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    out.append(t)
    t2 = Table(
        [[Paragraph(f"<b>Other Resources</b><br/>{other_lines}", P_TBL)]],
        colWidths=[16.8*cm])
    t2.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.6, colors.black),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    out.append(t2)
    return out


def assessment_table() -> list:
    rows = [
        [
            Paragraph("<b>Bloom's Level of Cognitive Task</b>", P_TBL_BC),
            Paragraph("<b>Continuous Learning Assessments (50%)</b>", P_TBL_BC), "", "", "", "", "", "", "",
            Paragraph("<b>End Semester Exam (50%)</b>", P_TBL_BC), "",
        ],
        [
            "", Paragraph("<b>CLA-1 (10%)</b>", P_TBL_BC), "",
            Paragraph("<b>Mid-1 (15%)</b>", P_TBL_BC), "",
            Paragraph("<b>CLA-2 (10%)</b>", P_TBL_BC), "",
            Paragraph("<b>Mid-2 (15%)</b>", P_TBL_BC), "", "", "",
        ],
        [
            "",
            Paragraph("<b>Th</b>", P_TBL_BC), Paragraph("<b>Prac</b>", P_TBL_BC),
            Paragraph("<b>Th</b>", P_TBL_BC), Paragraph("<b>Prac</b>", P_TBL_BC),
            Paragraph("<b>Th</b>", P_TBL_BC), Paragraph("<b>Prac</b>", P_TBL_BC),
            Paragraph("<b>Th</b>", P_TBL_BC), Paragraph("<b>Prac</b>", P_TBL_BC),
            Paragraph("<b>Th</b>", P_TBL_BC), Paragraph("<b>Prac</b>", P_TBL_BC),
        ],
        ["Level 1\nRemember / Understand", "70%", "", "65%", "", "40%", "", "50%", "", "40%", ""],
        ["Level 2\nApply / Analyse",        "30%", "", "35%", "", "40%", "", "50%", "", "60%", ""],
        ["Level 3\nEvaluate / Create",      "",    "", "",    "", "20%", "", "",    "", "",    ""],
        [Paragraph("<b>Total</b>", P_TBL_BC),
         Paragraph("<b>100%</b>", P_TBL_BC), "",
         Paragraph("<b>100%</b>", P_TBL_BC), "",
         Paragraph("<b>100%</b>", P_TBL_BC), "",
         Paragraph("<b>100%</b>", P_TBL_BC), "",
         Paragraph("<b>100%</b>", P_TBL_BC), ""],
    ]
    col_w = [3.0*cm] + [1.38*cm]*10
    t = Table(rows, colWidths=col_w)
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("BACKGROUND", (0, 0), (-1, 2), colors.HexColor("#eef2f6")),
        ("SPAN", (1, 0), (8, 0)),
        ("SPAN", (9, 0), (10, 0)),
        ("SPAN", (1, 1), (2, 1)),
        ("SPAN", (3, 1), (4, 1)),
        ("SPAN", (5, 1), (6, 1)),
        ("SPAN", (7, 1), (8, 1)),
        ("SPAN", (9, 1), (10, 1)),
        ("FONT", (0, 0), (-1, -1), "Times-Roman", 8.5),
    ]))
    return [Paragraph("<b>Learning Assessment</b>", H_SECTION), t]


# ----------------------------------------------------------------------------
# CONTENT — BLOCKCHAIN
# ----------------------------------------------------------------------------
BLOCKCHAIN = dict(
    name="Blockchain Technologies",
    code="AML 571",
    objectives=[
        "Learn the cryptographic and distributed-systems foundations of blockchain technology and understand the architecture of public ledgers.",
        "To introduce the fundamentals of consensus algorithms, smart contracts, and the Ethereum Virtual Machine execution model.",
        "To discuss various issues including scalability, privacy, security, and governance that make blockchain a hard engineering problem.",
        "To discuss well-known applications of blockchain such as DeFi, Zero-Knowledge Proofs, Rollups, and On-Chain Machine Learning.",
    ],
    outcomes=[
        ("Recall the fundamental concepts of cryptographic primitives and distributed consensus.", 1, 70, 68),
        ("Demonstrate algorithms for blockchain consensus, digital signatures, and Merkle structures.", 2, 70, 65),
        ("Develop smart contracts and Layer-2 systems for decentralized financial applications.", 3, 70, 60),
        ("Implement systems using Zero-Knowledge Proofs and analyze DeFi/security incident postmortems.", 4, 70, 65),
    ],
    matrix=[
        ("Outcome 1", ["2","3","3","","2","","","","","","","3","2",""]),
        ("Outcome 2", ["2","3","3","","2","","","","","","","2","2",""]),
        ("Outcome 3", ["2","3","2","","2","","","","","","","2","2",""]),
        ("Outcome 4", ["3","3","3","","2","","","","","","","2","3",""]),
        (Paragraph("<b>Course Average</b>", P_TBL_BC),
         ["2","3","3","","2","","","","","","","2","2",""]),
    ],
    units=[
        {
            "name": "Unit 1",
            "hours": 9,
            "rows": [
                ("Introduction and Overview: What is Blockchain; Why decentralization is hard: Byzantine faults, double-spend; Applications of Blockchain.", 2, "1", "1,2"),
                ("Cryptographic Foundations: Hash functions (SHA-256, Keccak), pre-image / collision resistance, puzzle-friendliness.", 2, "1", "1,3"),
                ("Merkle Trees and Patricia Tries; Inclusion proofs; Verkle trees and KZG polynomial commitments.", 2, "1", "1,3"),
                ("Digital Signatures: ECDSA, EdDSA, Schnorr (BIP-340), BLS aggregate signatures.", 2, "1", "1,3"),
                ("Distributed systems: CAP / FLP impossibility, Byzantine Generals Problem, the 3f+1 bound.", 1, "1,2", "1,2"),
            ],
        },
        {
            "name": "Unit 2",
            "hours": 8,
            "rows": [
                ("Bitcoin Deep Dive: UTXO model, Bitcoin Script, Proof-of-Work, difficulty adjustment, longest-chain rule.", 2, "1,2", "1,4"),
                ("Bitcoin economics: block reward halving, fees, selfish mining (Eyal & Sirer), 51% attack.", 1, "1,2", "1,4"),
                ("Ethereum & Smart Contracts: Account model, EVM, gas mechanics, Solidity language fundamentals.", 2, "1,2,3", "1,5"),
                ("ERC standards (ERC-20, ERC-721, ERC-4337); Account abstraction; client diversity.", 2, "2,3", "5,6"),
                ("Lightning Network and payment channels; Off-chain state.", 1, "2,3", "1,6"),
            ],
        },
        {
            "name": "Unit 3",
            "hours": 7,
            "rows": [
                ("Consensus Algorithms — Proof of Work variants; Energy and centralization tradeoffs.", 1, "1,2", "1,7"),
                ("Proof of Stake families: Casper FFG + LMD-GHOST (Ethereum), Tendermint / CometBFT, Ouroboros (Cardano).", 2, "1,2", "7,8"),
                ("PBFT and HotStuff: 3-phase voting, linear view change, pipelined finality.", 2, "1,2", "7"),
                ("Algorand BA*, Avalanche Snowball, Solana PoH; DAG protocols (Narwhal, Bullshark).", 1, "1,2", "7,8"),
                ("Slashing conditions, nothing-at-stake problem, long-range attacks, weak subjectivity.", 1, "2,3", "7,8"),
            ],
        },
        {
            "name": "Unit 4",
            "hours": 9,
            "rows": [
                ("Scalability and the Trilemma; Sharding; Vertical vs Horizontal scaling.", 2, "2,3", "5,6"),
                ("Layer 2: Optimistic Rollups (Arbitrum, Optimism) and fraud proof bisection.", 2, "3", "5,6,9"),
                ("ZK Rollups (zkSync, StarkNet, Polygon zkEVM); zkEVM equivalence levels (Type 1–4).", 2, "3,4", "5,6,9"),
                ("Data Availability: EIP-4844 proto-danksharding, blob transactions, Celestia, EigenDA.", 1, "3,4", "5,6"),
                ("Zero-Knowledge Proofs: SNARK vs STARK, Groth16, PLONK, Halo2; Circom toolchain.", 2, "3,4", "9,10"),
            ],
        },
        {
            "name": "Unit 5",
            "hours": 12,
            "rows": [
                ("Decentralized Finance: Stablecoins (USDC, DAI, FRAX), CDPs, algorithmic failure (Terra/UST).", 2, "3,4", "5,6"),
                ("Automated Market Makers: Uniswap v2 (xy=k), Curve StableSwap, Uniswap v3 concentrated liquidity.", 2, "3,4", "5,6"),
                ("Lending markets (Aave, Compound, Morpho); Flash loans; Oracle manipulation.", 2, "3,4", "5,6"),
                ("MEV: arbitrage, sandwich attacks, MEV-Boost, Proposer-Builder Separation (PBS).", 1, "3,4", "5,6"),
                ("Security: Reentrancy, integer overflow, access control; DAO hack, Wormhole, Ronin, Curve postmortems.", 2, "4", "5,6,11"),
                ("Governance and Tokenomics: DAOs, on-chain voting, veToken model, restaking (EigenLayer).", 2, "4", "5,6"),
                ("Research Frontiers: zkML, ZKVMs (RISC Zero, SP1), folding schemes (Nova, HyperNova), modular blockchains.", 1, "4", "9,10,12"),
            ],
        },
    ],
    experiments=[
        ("Build a toy blockchain in Python with hash chain and tamper detection.", "1,2", "1,3"),
        ("Implement ECDSA wallet, transaction signing and signature verification.", "1,2", "1,3"),
        ("Construct Merkle tree and verify inclusion proofs for a block of transactions.", "1,2", "1,3"),
        ("Send a Bitcoin testnet transaction and decode raw transaction bytes.", "1,2", "1,4"),
        ("Develop and deploy an ERC-20 token contract using Foundry / Solidity.", "2,3", "5,6"),
        ("Reproduce a reentrancy attack on a vulnerable contract; apply checks-effects-interactions fix.", "3,4", "5,6,11"),
        ("Write invariant tests in Foundry; integrate Slither static analysis.", "3,4", "5,6,11"),
        ("Build a Proof-of-Work vs Proof-of-Stake simulator and benchmark finality latency.", "2,3", "7,8"),
        ("Inspect an Optimistic Rollup batch on Etherscan; compute calldata gas savings.", "3,4", "5,6"),
        ("Write a ZK circuit in Circom proving knowledge of `x` with `x*x=25`; deploy verifier.", "3,4", "9,10"),
        ("Analyze EIP-4844 blob transactions; compute cost-per-byte savings over calldata.", "3,4", "5,6"),
        ("Implement a Uniswap-v2-style AMM and compute impermanent loss for price moves.", "3,4", "5,6"),
        ("Simulate a flash loan arbitrage across two DEX pools using a mainnet fork.", "4",   "5,6"),
        ("Implement a DAO voting contract with token-weighted and conviction voting.", "3,4", "5,6"),
        ("Build a zkML inference proof for a small MLP using EZKL; verify on Sepolia.", "4",   "9,10,12"),
    ],
    recommended=[
        "Narayanan, A., Bonneau, J., Felten, E., Miller, A., Goldfeder, S. (2016). Bitcoin and Cryptocurrency Technologies. Princeton University Press.",
        "Antonopoulos, A. M. (2017). Mastering Bitcoin: Programming the Open Blockchain (2nd ed). O'Reilly.",
        "Boneh, D., Shoup, V. (2023). A Graduate Course in Applied Cryptography (online).",
        "Antonopoulos, A. M., Wood, G. (2018). Mastering Ethereum: Building Smart Contracts and DApps. O'Reilly.",
        "Werner, S. et al. (2022). SoK: Decentralized Finance (DeFi). ACM AFT.",
        "https://ethereum.org/en/developers/docs/  (Ethereum developer documentation)",
        "Yin, M. et al. (2019). HotStuff: BFT Consensus with Linearity and Responsiveness. ACM PODC.",
        "Kiayias, A. et al. (2017). Ouroboros: A Provably Secure Proof-of-Stake Protocol. CRYPTO.",
        "Ben-Sasson, E. et al. (2018). Scalable, transparent, and post-quantum secure computational integrity (STARK).",
        "Gabizon, A., Williamson, Z., Ciobotaru, O. (2019). PLONK: Permutations over Lagrange-bases.",
        "Atzei, N., Bartoletti, M., Cimoli, T. (2017). A Survey of Attacks on Ethereum Smart Contracts. POST.",
        "https://web.stanford.edu/class/cs251/  (Stanford CS251 — Cryptocurrencies and Blockchain Technologies)",
    ],
    other=[
        "https://bitcoin.org/bitcoin.pdf  (Satoshi Nakamoto, 2008)",
        "https://vitalik.eth.limo/  (Vitalik Buterin's research notes)",
        "https://ethresear.ch/  (Ethereum Research Forum)",
        "https://github.com/foundry-rs/foundry  (Foundry development toolkit)",
        "https://zk-learning.org/  (ZK MOOC — Stanford / Berkeley)",
        "https://learn.cyfrin.io/  (Cyfrin Updraft — Smart Contract Developer track)",
    ],
)


# ----------------------------------------------------------------------------
# CONTENT — XAI
# ----------------------------------------------------------------------------
XAI = dict(
    name="Explainable Artificial Intelligence",
    code="AML 572",
    objectives=[
        "Learn the foundations of Explainable AI and understand various interpretability frameworks including intrinsic and post-hoc methods.",
        "To introduce the algorithmic foundations of feature attribution, counterfactual reasoning, and concept-based explanation.",
        "To discuss issues that make explanation a hard task — faithfulness, disagreement, robustness, and adversarial vulnerability.",
        "To discuss well-known applications of XAI in medicine, finance, law, NLP, and the frontier of mechanistic interpretability.",
    ],
    outcomes=[
        ("Recall the fundamental concepts of interpretability, explainability, and transparency.", 1, 70, 68),
        ("Demonstrate algorithms for feature attribution, saliency analysis, and counterfactual generation.", 2, 70, 65),
        ("Develop systems for concept-based reasoning and global explanation of black-box models.", 3, 70, 60),
        ("Implement and evaluate mechanistic interpretability methods on transformer-based language models.", 4, 70, 65),
    ],
    matrix=[
        ("Outcome 1", ["2","3","3","","2","","","","","","","3","2",""]),
        ("Outcome 2", ["2","3","3","","2","","","","","","","2","2",""]),
        ("Outcome 3", ["2","3","2","","2","","","","","","","2","2",""]),
        ("Outcome 4", ["3","3","3","","2","","","","","","","2","3",""]),
        (Paragraph("<b>Course Average</b>", P_TBL_BC),
         ["2","3","3","","2","","","","","","","2","2",""]),
    ],
    units=[
        {
            "name": "Unit 1",
            "hours": 9,
            "rows": [
                ("Introduction and Overview: What is XAI; Why explanation is difficult: faithfulness vs plausibility; Regulatory drivers (GDPR, EU AI Act).", 2, "1", "1,2"),
                ("Definitions: Interpretability, Explainability, Transparency, Simulatability, Decomposability (Lipton's taxonomy).", 2, "1", "1,2"),
                ("Doshi-Velez & Kim evaluation framework: Application-grounded, Human-grounded, Functionally-grounded.", 1, "1", "1,3"),
                ("Intrinsic interpretable models: Linear, GAM, EBM, decision trees, risk scores; Rudin's argument for high-stakes domains.", 2, "1,2", "1,4"),
                ("Taxonomy of XAI: Local vs Global, Intrinsic vs Post-hoc, Model-specific vs Model-agnostic.", 2, "1,2", "1,2"),
            ],
        },
        {
            "name": "Unit 2",
            "hours": 8,
            "rows": [
                ("LIME: Local Interpretable Model-Agnostic Explanations; perturbation, kernel weighting, sparse linear surrogate.", 2, "1,2", "5,6"),
                ("Shapley values from cooperative game theory; the four axioms; KernelSHAP, TreeSHAP, DeepSHAP.", 2, "1,2", "5,6"),
                ("Anchors and rule-based local explanations; Influence functions (Koh & Liang).", 1, "1,2", "5,6"),
                ("Gradient-based attribution: Vanilla saliency, SmoothGrad, Integrated Gradients (Sundararajan), DeepLIFT, LRP.", 2, "1,2", "5,7"),
                ("Grad-CAM and class-discriminative visualization for CNNs; Grad-CAM++, Score-CAM, HiResCAM.", 1, "1,2", "5,7"),
            ],
        },
        {
            "name": "Unit 3",
            "hours": 7,
            "rows": [
                ("Concept-based methods: TCAV (Kim et al.), ACE, CRAFT, Network Dissection.", 2, "2,3", "5,8"),
                ("Concept Bottleneck Models; Prototype networks (ProtoPNet); This-looks-like-that explanations.", 1, "2,3", "5,8"),
                ("Counterfactual explanations: Wachter et al. formulation; DiCE, FACE, MACE, GeCo.", 2, "2,3", "5,8"),
                ("Algorithmic recourse and the causal turn (Karimi et al.); Contrastive explanations.", 1, "2,3", "5,8"),
                ("Global methods: PDP, ICE, ALE; Permutation importance; Surrogate models; Functional ANOVA.", 1, "2,3", "5"),
            ],
        },
        {
            "name": "Unit 4",
            "hours": 9,
            "rows": [
                ("Attention Is Not Explanation debate; Jain & Wallace vs Wiegreffe & Pinter.", 1, "2,3", "9"),
                ("Attention Rollout, Attention Flow, Generic Transformer Attribution (Chefer et al.).", 2, "3,4", "9"),
                ("Probing classifiers and control tasks (Hewitt & Liang); Logit Lens and Tuned Lens.", 1, "3,4", "9,10"),
                ("Mechanistic Interpretability: Distill Circuits, Olah et al.; Mathematical Framework for Transformer Circuits.", 2, "3,4", "10,11"),
                ("Induction heads (Anthropic 2022); Indirect Object Identification circuit; Causal tracing and ROME knowledge editing.", 2, "3,4", "10,11"),
                ("Sparse Autoencoders (SAEs), Monosemanticity, superposition hypothesis; Automated Circuit Discovery (ACDC).", 1, "3,4", "10,11"),
            ],
        },
        {
            "name": "Unit 5",
            "hours": 12,
            "rows": [
                ("Evaluation metrics: Faithfulness, Plausibility, Robustness; Deletion/Insertion AUC; ROAR.", 2, "3,4", "5,12"),
                ("Sanity checks (Adebayo et al.); Infidelity & Sensitivity (Yeh et al.); ERASER benchmark; Quantus toolkit.", 2, "3,4", "5,12"),
                ("Adversarial XAI: Fooling LIME and SHAP (Slack et al.); Fairwashing; Disagreement problem (Krishna et al.).", 2, "3,4", "5,12"),
                ("Human-Centered XAI: Miller's social-science insights; Trust calibration; Bansal et al. on AI-team performance.", 2, "4",   "5,12"),
                ("XAI in Medicine: Caruana's pneumonia case, DeGrave shortcut learning; Concept-based clinical translation.", 1, "4",   "5,12"),
                ("XAI in Finance & Law: ECOA adverse action, EU AI Act, COMPAS debate, fair-prediction impossibility (Chouldechova, Kleinberg).", 1, "4",   "5,12"),
                ("XAI for LLMs: Faithful CoT, hallucination explanation, citation grounding, sycophancy.", 1, "4",   "10,11"),
                ("Research Frontiers: SAEs at scale, ZKML + Verifiable Explanations, Decentralized AI, Causal XAI.", 1, "4",   "10,11,12"),
            ],
        },
    ],
    experiments=[
        ("Train an interpretable baseline (Logistic Regression + EBM) on a tabular dataset; report coefficients.", "1",   "1,4"),
        ("Compare EBM, XGBoost and Random Forest on accuracy vs interpretability tradeoffs.", "1,2", "1,4"),
        ("Implement KernelSHAP from scratch and validate against the shap library on 5 test samples.", "2,3", "5,6"),
        ("Apply TreeSHAP and LIME to an XGBoost model; document where they disagree.", "2,3", "5,6"),
        ("Implement Anchors for high-precision rule explanations on the Adult Income dataset.", "2,3", "5"),
        ("Compute vanilla saliency and SmoothGrad heatmaps on a pretrained ResNet-50.", "2,3", "5,7"),
        ("Implement Integrated Gradients with multiple baselines; visualize differences.", "2,3", "5,7"),
        ("Apply Grad-CAM and Grad-CAM++ to ImageNet samples; compare class-discriminative behavior.", "2,3", "5,7"),
        ("Run Adebayo's model-randomization and data-randomization sanity checks on 4 saliency methods.", "3,4", "5,12"),
        ("Build a 'stripes' concept activation vector; run TCAV on a zebra-vs-spaniel classifier.", "3,4", "5,8"),
        ("Generate counterfactual explanations using DiCE for denied loan applicants; audit for fairness.", "3,4", "5,8"),
        ("Compare PDP, ICE and ALE on a dataset with correlated features; explain divergence.", "3",   "5"),
        ("Use TransformerLens to reproduce induction-head behavior on GPT-2 Small.", "4",   "9,10,11"),
        ("Browse a public Sparse Autoencoder (Neuronpedia); ablate one feature and measure output change.", "4",   "10,11"),
        ("Build a verifiable explanation prototype: prove SHAP value of a small NN with EZKL.", "4",   "10,11,12"),
    ],
    recommended=[
        "Molnar, C. (2025). Interpretable Machine Learning: A Guide for Making Black Box Models Explainable (3rd ed). Online: christophm.github.io/interpretable-ml-book/",
        "Lipton, Z. C. (2016). The Mythos of Model Interpretability. ICML WHI Workshop / Communications of the ACM 2018.",
        "Doshi-Velez, F., Kim, B. (2017). Towards a Rigorous Science of Interpretable Machine Learning.",
        "Rudin, C. (2019). Stop Explaining Black Box Machine Learning Models for High Stakes Decisions and Use Interpretable Models Instead. Nature Machine Intelligence.",
        "Ribeiro, M., Singh, S., Guestrin, C. (2016). \"Why Should I Trust You?\": Explaining the Predictions of Any Classifier. ACM KDD.",
        "Lundberg, S., Lee, S. (2017). A Unified Approach to Interpreting Model Predictions (SHAP). NeurIPS.",
        "Sundararajan, M., Taly, A., Yan, Q. (2017). Axiomatic Attribution for Deep Networks (Integrated Gradients). ICML.",
        "Selvaraju, R. et al. (2017). Grad-CAM: Visual Explanations from Deep Networks. ICCV.",
        "Wiegreffe, S., Pinter, Y. (2019). Attention Is Not Not Explanation. EMNLP.",
        "Elhage, N. et al. (2021). A Mathematical Framework for Transformer Circuits. Anthropic.",
        "Olsson, C. et al. (2022). In-Context Learning and Induction Heads. Anthropic.",
        "Adebayo, J. et al. (2018). Sanity Checks for Saliency Maps. NeurIPS.",
    ],
    other=[
        "https://christophm.github.io/interpretable-ml-book/  (Molnar — Interpretable ML, free)",
        "https://transformer-circuits.pub/  (Anthropic Transformer Circuits Thread)",
        "https://distill.pub/2020/circuits/zoom-in/  (Distill Circuits Thread)",
        "https://neelnanda.io/mechanistic-interpretability  (Neel Nanda's Mech-Interp guide)",
        "Kaggle Micro-Course: Machine Learning Explainability  (https://www.kaggle.com/learn/machine-learning-explainability)",
        "https://github.com/understandable-machine-intelligence-lab/Quantus  (Quantus evaluation toolkit)",
    ],
)


# ----------------------------------------------------------------------------
# build a syllabus
# ----------------------------------------------------------------------------
def build(course: dict, outfile: Path) -> None:
    doc = SimpleDocTemplate(
        str(outfile), pagesize=A4,
        leftMargin=2.0*cm, rightMargin=2.0*cm,
        topMargin=1.5*cm, bottomMargin=1.5*cm,
        title=f"{course['name']} — Course Syllabus",
        author="SRM University-AP",
    )
    story = []
    story += header_block()
    story += course_info_table(course["name"], course["code"])
    story += [Spacer(1, 4)]
    story += objectives_block(course["objectives"])
    story += [Spacer(1, 4)]
    story += outcomes_table(course["outcomes"])
    story += [PageBreak()]
    story += articulation_matrix(course["matrix"])
    story += [Spacer(1, 6)]
    story += utilization_table(course["units"])
    story += [PageBreak()]
    story += experiments_table(course["experiments"])
    story += [Spacer(1, 6)]
    story += resources_block(course["recommended"], course["other"])
    story += [Spacer(1, 6)]
    story += assessment_table()

    doc.build(story)
    print(f"wrote {outfile}  ({outfile.stat().st_size/1024:.1f} KB)")


def main() -> None:
    out_dir = ROOT
    build(BLOCKCHAIN, out_dir / "FINAL_Blockchain_Syllabus.pdf")
    build(XAI, out_dir / "FINAL_XAI_Syllabus.pdf")


if __name__ == "__main__":
    main()
