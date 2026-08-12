require("@nomicfoundation/hardhat-toolbox");

/**
 * Hardhat configuration for the SEBA-XAI Ethereum port.
 *
 * `sepolia` is wired for a public Ethereum testnet deployment; it activates
 * only when SEPOLIA_RPC_URL and DEPLOYER_PRIVATE_KEY are present in the
 * environment, so `npm test` and local runs never need secrets. Never commit a
 * private key — pass it via the environment (e.g. a local .env, git-ignored).
 */

const SEPOLIA_RPC_URL = process.env.SEPOLIA_RPC_URL || "";
const DEPLOYER_PRIVATE_KEY = process.env.DEPLOYER_PRIVATE_KEY || "";

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: {
    version: "0.8.24",
    settings: {
      optimizer: { enabled: true, runs: 200 },
      // The record/decision structs carry many fields; the IR pipeline resolves
      // the "stack too deep" these wide writes would otherwise hit.
      viaIR: true,
    },
  },
  networks: {
    hardhat: {},
    localhost: { url: "http://127.0.0.1:8545" },
    ...(SEPOLIA_RPC_URL && DEPLOYER_PRIVATE_KEY
      ? {
          sepolia: {
            url: SEPOLIA_RPC_URL,
            accounts: [DEPLOYER_PRIVATE_KEY],
          },
        }
      : {}),
  },
};
