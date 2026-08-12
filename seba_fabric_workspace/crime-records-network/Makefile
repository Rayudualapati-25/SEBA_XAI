# Crime Records Access Network — operational entry points.
#
# Every command in the project is a target here, so nothing has to be
# remembered as a long path. Run `make` with no target for the list.

SHELL := /bin/bash
CHANNEL ?= crimechannel
CC_NAME ?= crimerecords
CC_VERSION ?= 2.3
# 'auto' resolves to committed sequence + 1, so a fresh network deploys at 1 and
# an upgrade increments correctly. Override only to pin a specific sequence:
#   make deploy CC_SEQUENCE=3
CC_SEQUENCE ?= auto

# The peer/orderer binaries and the Fabric images live under the parent
# workspace; Docker may be provided by Colima rather than Docker Desktop.
export DOCKER_CONTEXT ?= colima

.PHONY: help all up down deploy seed seed-users seed-domain seed-records backend ollama test test-chaincode \
        test-backend smoke prove inspect verify-log measure evaluate results clean-containers

help:
	@echo "Setup"
	@echo "  make all           everything: network, chaincode, users, then the app"
	@echo "  make up            bring up the 5-organisation network (~3 min)"
	@echo "  make deploy        install and commit the chaincode"
	@echo "  make seed          issue the department users their certificates (Fabric CA)"
	@echo "  make seed-users    write those users onto the ledger (needed to sign in)"
	@echo "  make seed-domain   write departments and deterministic demo cases"
	@echo "  make seed-records  write synthetic metadata + agency-vault demo content"
	@echo "  make ollama        start the local LLM used for explanations"
	@echo "  make backend       run the API and web interface on :3001"
	@echo "  make down          stop the network and remove generated material"
	@echo
	@echo "Verification"
	@echo "  make test          all test suites"
	@echo "  make smoke         end-to-end scenario against the live network"
	@echo "  make prove         prove it is a real permissioned blockchain (10 checks)"
	@echo "  make inspect       read ledger state: blocks, endorsements, history"
	@echo "  make verify-log    read direct-ledger access events and integrity status"
	@echo
	@echo "Measurement"
	@echo "  make measure       latency, storage, attack replay"
	@echo "  make evaluate      explanation quality: template vs local LLM"
	@echo "  make results       list generated result files"
	@echo
	@echo "Maintenance"
	@echo "  make clean-containers   remove stale chaincode build containers"

# --- setup -----------------------------------------------------------------

# One command from nothing to a working system. The order is not arbitrary:
# the chaincode has to be committed before any user can be written to the
# ledger, and the users have to be on the ledger before anyone can sign in.
all: up deploy seed seed-users seed-domain seed-records
	@echo
	@echo "Everything is up. Start the web interface with:  make backend"
	@echo "Then open http://localhost:3001 and select the sho.reddy Fabric identity"

up:
	scripts/network-up.sh $(CHANNEL)

deploy:
	cd network && bash scripts/deployCC.sh $(CHANNEL) $(CC_NAME) $(CC_VERSION) $(CC_SEQUENCE)

# Step 1 of registration: the Fabric CAs issue X.509 certificates.
seed:
	cd network && bash scripts/seed-identities.sh

# Step 2: the accounts themselves, written onto the blockchain. Sign-in reads
# from here — there is no user database.
seed-users:
	node scripts/seed-users-onchain.js

seed-domain:
	node scripts/seed-domain.js

seed-records:
	node scripts/seed-demo-records.js

ollama:
	scripts/setup-ollama.sh

backend:
	cd backend && npm start

down:
	scripts/network-down.sh

# --- verification ----------------------------------------------------------

test: test-chaincode test-backend

test-chaincode:
	cd chaincode/crimerecords && npm test

test-backend:
	cd backend && npm test

smoke:
	scripts/smoke-test.sh $(CHANNEL) $(CC_NAME)

prove:
	scripts/prove-permissioned.sh

inspect:
	scripts/inspect-ledger.sh

verify-log:
	scripts/verify-access-log.sh

# --- measurement -----------------------------------------------------------

measure:
	node experiments/measure.js $(N)

evaluate:
	node experiments/evaluate-explanations.js

results:
	@ls -1 experiments/results/

# --- maintenance -----------------------------------------------------------

# Each chaincode deployment leaves inert build containers behind. Enough of them
# make Docker slow enough to cause spurious test failures.
clean-containers:
	@ids=$$(docker ps -aq --filter status=created); \
	if [ -n "$$ids" ]; then docker rm $$ids >/dev/null && echo "removed $$(echo $$ids | wc -w | tr -d ' ') stale containers"; \
	else echo "no stale containers"; fi
