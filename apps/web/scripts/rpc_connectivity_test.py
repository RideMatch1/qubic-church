#!/usr/bin/env python3
"""
MANHATTAN PROJECT - Phase 2: RPC Connectivity Test
====================================================

This script performs comprehensive connectivity tests to the Qubic RPC endpoint.
All tests are READ-ONLY and do not modify any state on the network.

Tests:
1. Basic HTTP connectivity to RPC endpoint
2. Tick-Info retrieval (network status)
3. Balance API for test identities
4. QubiPy library functionality
5. Network status check

Author: qubic-academic-docs
Date: 2026-01-16
"""

import sys
import time
import json
import os
from pathlib import Path
from datetime import datetime

# HTTP library
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("ERROR: requests library not available. Install with: pip install requests")

# Environment loading
try:
    from dotenv import load_dotenv
    load_dotenv()
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

# QubiPy imports
try:
    from qubipy.crypto.utils import (
        get_subseed_from_seed,
        get_private_key_from_subseed,
        get_public_key_from_private_key,
        get_identity_from_public_key,
        get_public_key_from_identity
    )
    QUBIPY_AVAILABLE = True
except ImportError:
    QUBIPY_AVAILABLE = False


# Configuration
RPC_URL = "https://rpc.qubic.org"
TIMEOUT = 10  # seconds

# Test identities (from verified nodes)
TEST_IDENTITIES = {
    "ENTRY": "VKZTPCKVHOMAXBQZYOYHKCXUIQODAGJKKXJJAPBDFGOYYSIWRQHFRRWFOQCH",
    "VOID": "SCBGQAOHIGFHPCJCMYNYUBIOKJWCKAWGGSLFTXLZSGWZRLOODRUPTDNCYBEB",
    "GUARDIAN": "DXASUXXKJAEJVGQEUXLIVNIQWDUCCNFTLEHCDCNZNBVGLPRTJRUQKZDECIPG",
}


class RPCTester:
    """RPC connectivity test suite."""

    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "rpc_url": RPC_URL,
            "tests": {}
        }
        self.passed = 0
        self.failed = 0

    def log_test(self, name: str, passed: bool, details: dict = None):
        """Log test result."""
        status = "PASS" if passed else "FAIL"
        icon = "✓" if passed else "✗"

        if passed:
            self.passed += 1
        else:
            self.failed += 1

        self.results["tests"][name] = {
            "passed": passed,
            "details": details or {}
        }

        print(f"  [{icon}] {name}: {status}")
        if details and not passed:
            for k, v in details.items():
                print(f"      {k}: {v}")

    def test_dependencies(self):
        """Test 1: Check required dependencies."""
        print("\n[TEST 1] Dependency Check")
        print("-" * 40)

        # requests
        self.log_test("requests library", REQUESTS_AVAILABLE,
                      {} if REQUESTS_AVAILABLE else {"error": "Install: pip install requests"})

        # dotenv
        self.log_test("python-dotenv", DOTENV_AVAILABLE,
                      {} if DOTENV_AVAILABLE else {"warning": "Optional, but recommended"})

        # QubiPy
        self.log_test("QubiPy crypto", QUBIPY_AVAILABLE,
                      {} if QUBIPY_AVAILABLE else {"error": "Run with .venv_qubic/bin/python"})

        return REQUESTS_AVAILABLE and QUBIPY_AVAILABLE

    def test_rpc_basic(self):
        """Test 2: Basic RPC connectivity."""
        print("\n[TEST 2] RPC Basic Connectivity")
        print("-" * 40)

        if not REQUESTS_AVAILABLE:
            self.log_test("RPC reachable", False, {"error": "requests not available"})
            return False

        try:
            # Simple GET to tick-info
            response = requests.get(f"{RPC_URL}/v1/tick-info", timeout=TIMEOUT)

            self.log_test("HTTP connection", response.status_code == 200,
                         {"status_code": response.status_code})

            if response.status_code == 200:
                data = response.json()
                tick = data.get('tickInfo', {}).get('tick', 0)
                epoch = data.get('tickInfo', {}).get('epoch', 0)

                self.log_test("JSON response valid", tick > 0,
                             {"current_tick": tick, "epoch": epoch})

                return tick > 0
            return False

        except requests.exceptions.Timeout:
            self.log_test("HTTP connection", False, {"error": "Timeout"})
            return False
        except requests.exceptions.ConnectionError as e:
            self.log_test("HTTP connection", False, {"error": str(e)[:100]})
            return False
        except Exception as e:
            self.log_test("HTTP connection", False, {"error": str(e)[:100]})
            return False

    def test_tick_monitoring(self):
        """Test 3: Verify tick progression."""
        print("\n[TEST 3] Tick Progression Monitor")
        print("-" * 40)

        if not REQUESTS_AVAILABLE:
            self.log_test("Tick monitoring", False, {"error": "requests not available"})
            return False

        try:
            # Get tick twice with delay
            r1 = requests.get(f"{RPC_URL}/v1/tick-info", timeout=TIMEOUT)
            tick1 = r1.json().get('tickInfo', {}).get('tick', 0)

            print(f"      First tick: {tick1}")
            print(f"      Waiting 3 seconds...")
            time.sleep(3)

            r2 = requests.get(f"{RPC_URL}/v1/tick-info", timeout=TIMEOUT)
            tick2 = r2.json().get('tickInfo', {}).get('tick', 0)

            print(f"      Second tick: {tick2}")

            # Tick should have increased (or at least not decreased)
            progressed = tick2 >= tick1
            self.log_test("Tick progression", progressed,
                         {"tick1": tick1, "tick2": tick2, "delta": tick2 - tick1})

            return progressed

        except Exception as e:
            self.log_test("Tick progression", False, {"error": str(e)[:100]})
            return False

    def test_balance_api(self):
        """Test 4: Balance API for test identities."""
        print("\n[TEST 4] Balance API Check")
        print("-" * 40)

        if not REQUESTS_AVAILABLE:
            self.log_test("Balance API", False, {"error": "requests not available"})
            return False

        all_passed = True

        for name, identity in TEST_IDENTITIES.items():
            try:
                url = f"{RPC_URL}/v1/balances/{identity}"
                response = requests.get(url, timeout=TIMEOUT)

                if response.status_code == 200:
                    data = response.json()
                    balance = data.get('balance', {}).get('balance', 'N/A')
                    last_in = data.get('balance', {}).get('latestIncomingTransferTick', 0)
                    last_out = data.get('balance', {}).get('latestOutgoingTransferTick', 0)

                    self.log_test(f"Balance {name}", True,
                                 {"balance": balance, "last_in": last_in, "last_out": last_out})
                else:
                    self.log_test(f"Balance {name}", False,
                                 {"status_code": response.status_code})
                    all_passed = False

            except Exception as e:
                self.log_test(f"Balance {name}", False, {"error": str(e)[:100]})
                all_passed = False

        return all_passed

    def test_qubipy_crypto(self):
        """Test 5: QubiPy cryptographic functions."""
        print("\n[TEST 5] QubiPy Crypto Functions")
        print("-" * 40)

        if not QUBIPY_AVAILABLE:
            self.log_test("QubiPy crypto", False, {"error": "QubiPy not available"})
            return False

        try:
            # Test seed -> identity derivation
            test_seed = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"  # 55 'a's
            seed_bytes = test_seed.encode('utf-8')

            subseed = get_subseed_from_seed(seed_bytes)
            self.log_test("get_subseed_from_seed", subseed is not None and len(subseed) == 32,
                         {"subseed_len": len(subseed) if subseed else 0})

            privkey = get_private_key_from_subseed(subseed)
            self.log_test("get_private_key_from_subseed", privkey is not None and len(privkey) == 32,
                         {"privkey_len": len(privkey) if privkey else 0})

            pubkey = get_public_key_from_private_key(privkey)
            self.log_test("get_public_key_from_private_key", pubkey is not None and len(pubkey) == 32,
                         {"pubkey_len": len(pubkey) if pubkey else 0})

            identity = get_identity_from_public_key(pubkey)
            self.log_test("get_identity_from_public_key", identity is not None and len(identity) == 60,
                         {"identity": identity[:20] + "..." if identity else None, "len": len(identity) if identity else 0})

            # Test identity -> pubkey (reverse)
            recovered_pubkey = get_public_key_from_identity(identity)
            self.log_test("get_public_key_from_identity", recovered_pubkey == pubkey,
                         {"match": recovered_pubkey == pubkey})

            return True

        except Exception as e:
            self.log_test("QubiPy crypto chain", False, {"error": str(e)[:100]})
            return False

    def test_env_config(self):
        """Test 6: Environment configuration check."""
        print("\n[TEST 6] Environment Configuration")
        print("-" * 40)

        # Check for MASTER_SEED (don't log the value!)
        master_seed = os.getenv("MASTER_SEED")
        has_seed = master_seed is not None and len(master_seed) == 55

        if has_seed:
            self.log_test("MASTER_SEED configured", True,
                         {"length": len(master_seed), "first_chars": master_seed[:3] + "***"})
        else:
            seed_len = len(master_seed) if master_seed else 0
            self.log_test("MASTER_SEED configured", False,
                         {"warning": "MASTER_SEED not found or invalid length",
                          "actual_length": seed_len,
                          "required_length": 55})

        # Check .env file exists
        env_path = Path(__file__).parent.parent.parent.parent / ".env"
        if not env_path.exists():
            env_path = Path(__file__).parent / ".env"

        self.log_test(".env file exists", env_path.exists(),
                     {"path": str(env_path)})

        return has_seed

    def run_all_tests(self):
        """Run all tests and generate report."""
        print("=" * 60)
        print("MANHATTAN PROJECT - PHASE 2: RPC CONNECTIVITY TEST")
        print("=" * 60)
        print(f"RPC Endpoint: {RPC_URL}")
        print(f"Timestamp: {self.results['timestamp']}")

        # Run all tests
        dep_ok = self.test_dependencies()
        rpc_ok = self.test_rpc_basic() if dep_ok else False
        tick_ok = self.test_tick_monitoring() if rpc_ok else False
        balance_ok = self.test_balance_api() if rpc_ok else False
        crypto_ok = self.test_qubipy_crypto()
        env_ok = self.test_env_config()

        # Summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"  Tests Passed: {self.passed}")
        print(f"  Tests Failed: {self.failed}")
        print(f"  Total Tests:  {self.passed + self.failed}")

        # Critical checks
        print("\n" + "-" * 40)
        print("CRITICAL CHECKS:")
        critical_pass = dep_ok and rpc_ok and crypto_ok
        print(f"  Dependencies OK:     {'YES' if dep_ok else 'NO'}")
        print(f"  RPC Connectivity OK: {'YES' if rpc_ok else 'NO'}")
        print(f"  Tick Progression OK: {'YES' if tick_ok else 'NO'}")
        print(f"  Balance API OK:      {'YES' if balance_ok else 'NO'}")
        print(f"  QubiPy Crypto OK:    {'YES' if crypto_ok else 'NO'}")
        print(f"  MASTER_SEED Set:     {'YES' if env_ok else 'NO (required for broadcasting)'}")

        # Save results
        self.results["summary"] = {
            "passed": self.passed,
            "failed": self.failed,
            "critical_checks": {
                "dependencies": dep_ok,
                "rpc_connectivity": rpc_ok,
                "tick_progression": tick_ok,
                "balance_api": balance_ok,
                "qubipy_crypto": crypto_ok,
                "master_seed": env_ok
            }
        }

        output_path = Path(__file__).parent / "RPC_CONNECTIVITY_RESULTS.json"
        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"\nResults saved to: {output_path}")

        # Final verdict
        print("\n" + "=" * 60)
        if critical_pass:
            if env_ok:
                print("PHASE 2 RESULT: PASS - RPC connectivity verified!")
                print("Ready for Phase 3: Strategic Node Validation")
                return 0
            else:
                print("PHASE 2 RESULT: PARTIAL - RPC works, but MASTER_SEED not configured")
                print("Configure MASTER_SEED in .env before broadcasting transactions")
                return 0
        else:
            print("PHASE 2 RESULT: FAIL - Critical connectivity issues!")
            print("Fix issues before proceeding.")
            return 1


def main():
    if not REQUESTS_AVAILABLE:
        print("ERROR: requests library required. Install: pip install requests")
        return 1

    tester = RPCTester()
    return tester.run_all_tests()


if __name__ == "__main__":
    sys.exit(main())
