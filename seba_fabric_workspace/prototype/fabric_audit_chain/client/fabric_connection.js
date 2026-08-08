"use strict";

const crypto = require("crypto");
const fs = require("fs/promises");
const path = require("path");
const grpc = require("@grpc/grpc-js");
const { connect, signers } = require("@hyperledger/fabric-gateway");

function env(name, fallback) {
  return process.env[name] || fallback;
}

function defaultFabricSamplesDir() {
  return path.resolve(__dirname, "..", ".local", "fabric-samples");
}

async function firstFile(directory) {
  const files = await fs.readdir(directory);
  const selected = files.find((file) => !file.startsWith("."));
  if (!selected) {
    throw new Error(`No usable file found in ${directory}`);
  }
  return path.join(directory, selected);
}

async function newGrpcConnection() {
  const fabricSamplesDir = env("FABRIC_SAMPLES_DIR", defaultFabricSamplesDir());
  const tlsCertPath = env(
    "TLS_CERT_PATH",
    path.join(
      fabricSamplesDir,
      "test-network/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt",
    ),
  );
  const peerEndpoint = env("PEER_ENDPOINT", "localhost:7051");
  const peerHostAlias = env("PEER_HOST_ALIAS", "peer0.org1.example.com");
  const tlsRootCert = await fs.readFile(tlsCertPath);
  const tlsCredentials = grpc.credentials.createSsl(tlsRootCert);
  return new grpc.Client(peerEndpoint, tlsCredentials, {
    "grpc.ssl_target_name_override": peerHostAlias,
  });
}

async function newIdentity() {
  const fabricSamplesDir = env("FABRIC_SAMPLES_DIR", defaultFabricSamplesDir());
  const mspId = env("MSP_ID", "Org1MSP");
  const certDirectoryPath = env(
    "CERT_DIRECTORY_PATH",
    path.join(
      fabricSamplesDir,
      "test-network/organizations/peerOrganizations/org1.example.com/users/User1@org1.example.com/msp/signcerts",
    ),
  );
  const certPath = await firstFile(certDirectoryPath);
  const credentials = await fs.readFile(certPath);
  return { mspId, credentials };
}

async function newSigner() {
  const fabricSamplesDir = env("FABRIC_SAMPLES_DIR", defaultFabricSamplesDir());
  const keyDirectoryPath = env(
    "KEY_DIRECTORY_PATH",
    path.join(
      fabricSamplesDir,
      "test-network/organizations/peerOrganizations/org1.example.com/users/User1@org1.example.com/msp/keystore",
    ),
  );
  const keyPath = await firstFile(keyDirectoryPath);
  const privateKeyPem = await fs.readFile(keyPath);
  const privateKey = crypto.createPrivateKey(privateKeyPem);
  return signers.newPrivateKeySigner(privateKey);
}

async function getContract() {
  const client = await newGrpcConnection();
  const gateway = connect({
    client,
    identity: await newIdentity(),
    signer: await newSigner(),
    evaluateOptions: () => ({ deadline: Date.now() + 5000 }),
    endorseOptions: () => ({ deadline: Date.now() + 15000 }),
    submitOptions: () => ({ deadline: Date.now() + 15000 }),
    commitStatusOptions: () => ({ deadline: Date.now() + 60000 }),
  });
  const channelName = env("CHANNEL_NAME", "seba");
  const chaincodeName = env("CHAINCODE_NAME", "seba-audit");
  const network = gateway.getNetwork(channelName);
  return {
    client,
    gateway,
    contract: network.getContract(chaincodeName),
    channelName,
    chaincodeName,
  };
}

module.exports = {
  getContract,
};
