# Update for Professor: Learning and Research Progress

Date: 27 May 2026

Respected Sir/Madam,

I am giving a short update on my learning and research work. You had asked me to learn the fundamentals of Blockchain, Explainable AI, and Agentic AI. Along with that, I have also been working on the research direction for a secure AI-based model for police and crime-data sharing in India.

## 1. Learning Progress

### 1.1 Blockchain

I have completed the basic blockchain foundation topics and have studied most of the consensus-algorithm part.

Topics completed:

- hash functions;
- Merkle trees;
- digital signatures;
- commitment schemes;
- basic distributed systems;
- CAP theorem;
- FLP impossibility;
- Bitcoin architecture;
- blocks and transactions;
- UTXO model;
- Proof of Work basic idea;
- consensus design space;
- PBFT;
- HotStuff;
- Tendermint/CometBFT;
- Ouroboros;
- Algorand BA*;
- Avalanche/Snowball;
- Solana Proof of History;
- Casper FFG basics;
- slashing;
- nothing-at-stake problem;
- long-range attack basics.

Topics still left in blockchain:

- Proof of Work variants such as SHA-256, Ethash, RandomX, Scrypt, and Equihash;
- full comparison of PoW and PoS;
- validator selection and validator rewards;
- Proof of Authority;
- consortium-chain consensus;
- LMD-GHOST in Ethereum;
- 51% attack, selfish mining, eclipse attack, bribery attack, inactivity leak, and time-bandit attack;
- final consensus comparison table;
- consensus lab and quiz.

My current blockchain progress is good at the foundation level. I still need to complete the remaining consensus and attack topics.

### 1.2 Explainable AI

I have prepared the XAI syllabus and notes. The XAI learning path includes:

- what explainability means;
- interpretable models and post-hoc explanations;
- taxonomy of XAI methods;
- LIME and SHAP;
- gradient-based explanations;
- concept-based explanations;
- counterfactual explanations;
- global explanation methods;
- explanation evaluation;
- human-centered XAI;
- XAI in law and public safety.

For my research, XAI will mainly be used to explain access decisions. The system should explain:

- why access was allowed;
- why access was denied;
- why access was sent for superior approval;
- which rule or attribute caused the decision;
- whether the explanation can be checked later during audit.

So, XAI is not only for explaining crime prediction. In this research, it is mainly for explaining sensitive data-access decisions.

### 1.3 Agentic AI

Agentic AI is the next topic I need to study more deeply. I have planned to cover:

- what an AI agent is;
- planning and task decomposition;
- tool use;
- memory;
- retrieval-augmented generation;
- multi-agent workflows;
- evaluation of agent actions;
- safety and guardrails;
- audit logging of agent actions.

For this research, Agentic AI may be useful later as an assistant for officers, auditors, or supervisors. For now, I am keeping it as a supporting future direction. The main research focus is still Blockchain + Security/Access Control + XAI.

## 2. Research Project Progress

### 2.1 Current Research Topic

The current research topic is:

**SEBA-XAI: Secure Explainable Blockchain-Audited Access Overlay for Inter-Agency Police Data Sharing in India**

This system is not meant to replace CCTNS or ICJS. It is planned as an extra secure layer on top of such systems. The goal is to support safe, explainable, and auditable access to sensitive police records.

The main research question is:

> When an officer or agency requests access to a sensitive police or crime record, should the system allow it, deny it, or send it for superior approval, and can the system later explain and audit that decision?

### 2.2 Work Completed Till Now

I have completed the following research preparation work:

1. **Problem understanding**
   - I studied the Indian policing context.
   - I identified CCTNS and ICJS as existing systems.
   - I understood that my research should support these systems, not replace them.

2. **Literature review**
   - I reviewed papers on blockchain for digital evidence.
   - I studied Hyperledger Fabric and permissioned blockchain.
   - I reviewed RBAC, ABAC, and policy-based access control.
   - I studied XAI and fairness issues in high-stakes AI.
   - I also reviewed privacy-preserving machine learning and secure data sharing.

3. **Existing model search**
   - I searched for existing models that combine blockchain, access control, and XAI.
   - I found that exact full systems are rare.
   - Closest works include BAXDT, LEChain, and two-level blockchain evidence-management systems.
   - These works are useful, but they do not fully solve the Indian police access-governance problem.

4. **Dataset study**
   - I studied public Indian datasets such as NCRB Crime in India and BPRD Data on Police Organizations.
   - I found that NCRB data is aggregate data.
   - It should not be used for individual suspect prediction.
   - For the main experiment, I plan to use synthetic multi-station access-request data.

5. **Research gap**
   - I rejected the weak idea of putting all police data directly on blockchain.
   - I also rejected unsupported individual crime prediction using public NCRB data.
   - The stronger gap is secure, explainable, and auditable access governance for sensitive police records.

6. **Architecture**
   - I designed a system where raw sensitive records stay off-chain.
   - Blockchain stores only hashes and audit information.
   - The security layer uses RBAC, ABAC/PBAC, credential checks, superior approval, and encrypted storage.
   - The XAI layer explains allow, deny, and escalate decisions.

7. **Methodology and experiments**
   - I planned baseline systems:
     - RBAC with normal log;
     - ABAC/PBAC with normal log;
     - ABAC/PBAC with signed hash-chain log;
     - proposed blockchain-audited SEBA-XAI model.
   - I planned tests for tamper detection, false allow rate, false deny rate, latency, metadata leakage, and explanation quality.

8. **Ethics and legal boundary**
   - I clearly marked that this is not a deployment-ready system.
   - I am not claiming legal compliance yet.
   - I am not using real sensitive police data.
   - I am not claiming real-world police benefit before experiments.

## 3. Model Direction

The model I am preparing is not a normal crime-prediction model. It is an access-decision model.

Input to the model/workflow:

- officer role;
- officer rank;
- officer police station;
- jurisdiction;
- case assignment;
- requested record type;
- sensitivity level;
- victim/witness/juvenile flag;
- purpose of access;
- time window;
- credential status;
- emergency flag;
- approval-token status.

Output:

- **allow**;
- **deny**;
- **escalate to superior approval**.

The explanation layer will show:

- which rule passed;
- which rule failed;
- why escalation was needed;
- what approval is required;
- which policy version was used.

The blockchain layer will not store raw police data. It will store only audit proofs such as:

- request hash;
- policy hash;
- decision hash;
- approval hash;
- model version;
- explanation hash;
- timestamp;
- actor credential hash.

## 4. Current Status

At present, I have completed the research foundation. This includes:

- problem framing;
- literature review;
- dataset study;
- research gap;
- system architecture;
- methodology;
- experiment plan;
- evaluation metrics;
- ethics and legal limitations;
- professor-ready research documents.

Implementation is not completed yet. I have not claimed any experimental results.

## 5. Next Step

The next step is to build the first prototype:

**synthetic_access_sim**

This prototype will include:

- synthetic police-station access-request data;
- policy oracle;
- RBAC baseline;
- ABAC/PBAC baseline;
- signed hash-chain log baseline;
- local blockchain-style audit ledger;
- XAI explanation generator;
- tamper tests;
- metrics output.

After this, I can compare the proposed system with baselines and start writing the results based on actual evidence.

## 6. Limitation

The work is currently in the research-design stage. I have not yet completed implementation or experiments. So I am not claiming accuracy, latency, security improvement, deployment readiness, or legal compliance at this stage.

## 7. Short Summary

I have completed important blockchain foundation topics and prepared the XAI learning path. Agentic AI fundamentals are planned next. For the research project, I have completed the problem study, literature review, dataset study, research gap, architecture, methodology, and experiment plan. The selected direction is a secure, explainable, blockchain-audited access-governance model for sensitive police data sharing in India. The next milestone is to implement the synthetic simulator and generate experimental results.
