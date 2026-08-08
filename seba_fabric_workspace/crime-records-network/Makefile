# Crime Records Access Network — operational entry points.
#
# Every command in the project is a target here, so nothing has to be
# remembered as a long path. Run `make` with no target for the list.

SHELL := /bin/bash
CHANNEL ?= crimechannel
CC_NAME ?= crimerecords
CC_VERSION ?= 1.6
CC_SEQUENCE ?= 7

# The peer/orderer binaries and the Fabric images live under the parent
# workspace; Docker may be provided by Colima rather than Docker Desktop.
export DOCKER_CONTEXT ?= colima

.PHONY: help up down deploy seed backend ollama test test-chaincode test-backend \
        smoke inspect verify-log measure evaluate results clean-containers

help:
	@echo "Setup"
	@echo "  make up            bring up the 5-organisation network (~3 min)"
	@echo "  make deploy        install and commit the chaincode"
	@echo "  make seed          register the department user identities"
	@echo "  make ollama        start the local LLM used for explanations"
	@echo "  make backend       run the API and web interface on :3001"
	@echo "  make down          stop the network and remove generated material"
	@echo
	@echo "Verification"
	@echo "  make test          all test suites"
	@echo "  make smoke         end-to-end scenario against the live network"
	@echo "  make inspect       read ledger state: blocks, endorsements, history"
	@echo "  make verify-log    check access-log integrity against on-chain anchors"
	@echo
	@echo "Measurement"
	@echo "  make measure       latency, storage, attack replay"
	@echo "  make evaluate      explanation quality: template vs local LLM"
	@echo "  make results       list generated result files"
	@echo
	@echo "Maintenance"
	@echo "  make clean-containers   remove stale chaincode build containers"

# --- setup -----------------------------------------------------------------

up:
	scripts/network-up.sh $(CHANNEL)

deploy:
	cd network && bash scripts/deployCC.sh $(CHANNEL) $(CC_NAME) $(CC_VERSION) $(CC_SEQUENCE)

seed:
	cd network && bash scripts/seed-identities.sh

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
