#!/usr/bin/env python3
"""
AIGARTH ITU TRAINING - EVOLUTIONARY ARITHMETIC
===============================================

This script trains an Aigarth ITU to learn integer addition
through evolutionary mutation and selection.

The algorithm:
1. Create random ITU
2. Test on training data
3. Mutate weights
4. If performance improves, keep mutation
5. Repeat until convergence

Date: January 17, 2026
"""

import copy
import json
import random
import secrets
import sys
from collections import namedtuple
from datetime import datetime
from pathlib import Path

from aigarth_it.common import ternary_clamp, random_trit_vector
from aigarth_it.neuron_cl import AITClNeuron
from aigarth_it.itu_cl import AigarthITUCl
from aigarth_it.icap.itucl_aai_i2x7o8 import (
    ITUClArithmeticAdditionIntI2x7O8,
    AAIInputDatasetRow
)

# Training configuration
CONFIG = {
    "max_generations": 500,
    "training_samples": 20,
    "test_samples": 10,
    "report_interval": 50,
    "target_accuracy": 0.9,  # 90% correct
}

# Results storage
RESULTS = {
    "timestamp": datetime.now().isoformat(),
    "config": CONFIG,
    "generations": [],
    "best_accuracy": 0,
    "final_neurons": 0
}

def log(msg):
    print(msg)

def generate_training_data(count: int) -> list:
    """Generate random addition training data."""
    data = []
    for _ in range(count):
        # Range: [-64, 63] for 7-bit signed integers
        a = random.randint(-64, 63)
        b = random.randint(-64, 63)
        c = a + b  # Result in range [-128, 126]
        data.append(AAIInputDatasetRow(a=a, b=b, c=c))
    return data

def evaluate_itu(itu, test_data: list) -> tuple:
    """Evaluate ITU accuracy on test data."""
    correct = 0
    total = len(test_data)
    unknown = 0

    for row in test_data:
        try:
            reflection = itu.reflect(row.a, row.b)
            result = reflection.integer

            if result is None:
                unknown += 1
            elif result == row.c:
                correct += 1
        except Exception:
            pass

    accuracy = correct / total if total > 0 else 0
    return accuracy, correct, unknown, total

def mutate_itu_manual(itu) -> bool:
    """Manually mutate ITU weights (without version tracking)."""
    # Pick a random neuron
    if len(itu._circle) == 0:
        return False

    idx_neuron = secrets.randbelow(len(itu._circle))
    neuron = itu._circle[idx_neuron]

    # Pick a random weight
    if len(neuron._input_weights) == 0:
        return False

    idx_weight = secrets.randbelow(len(neuron._input_weights))
    old_weight = neuron._input_weights[idx_weight]

    # Change by +1 or -1
    delta = secrets.choice([-1, 1])
    new_weight = old_weight + delta

    if new_weight in (-1, 0, 1):
        # Valid ternary weight - apply change
        neuron._input_weights[idx_weight] = new_weight
        return True
    else:
        # Weight went out of range - spawn new neuron
        # Clone a neighbor neuron
        neighbor_idx = (idx_neuron + 1) % len(itu._circle)
        neighbor = itu._circle[neighbor_idx]

        new_neuron = AITClNeuron(
            input_weights=neighbor._input_weights[:],
            input_skew=neighbor._input_skew
        )

        itu._circle.insert(idx_neuron + 1, new_neuron)
        return True

def deep_copy_itu(itu):
    """Create a deep copy of ITU for rollback."""
    # Copy all neurons
    new_circle = []
    new_neurons_i = []
    new_neurons_o = []

    for neuron in itu._circle:
        new_neuron = AITClNeuron(
            input_weights=neuron._input_weights[:],
            input_skew=neuron._input_skew
        )
        new_circle.append(new_neuron)

        if neuron in itu._neurons_i:
            new_neurons_i.append(new_neuron)
        if neuron in itu._neurons_o:
            new_neurons_o.append(new_neuron)

    # Create new ITU with copied structure
    new_itu = ITUClArithmeticAdditionIntI2x7O8.__new__(ITUClArithmeticAdditionIntI2x7O8)
    new_itu._circle = new_circle
    new_itu._neurons_i = new_neurons_i if new_neurons_i else new_circle[:itu.meta.input_bitwidth]
    new_itu._neurons_o = new_neurons_o if new_neurons_o else new_circle[-itu.meta.output_bitwidth:]
    new_itu.meta = itu.meta
    new_itu.ff_cycle_cap = itu.ff_cycle_cap
    new_itu.lm_prefix = itu.lm_prefix

    return new_itu

def train():
    """Train ITU using evolutionary algorithm."""
    log("="*60)
    log("  AIGARTH EVOLUTIONARY TRAINING")
    log("="*60)
    log(f"  Max generations: {CONFIG['max_generations']}")
    log(f"  Training samples: {CONFIG['training_samples']}")
    log(f"  Test samples: {CONFIG['test_samples']}")
    log(f"  Target accuracy: {CONFIG['target_accuracy']*100}%")
    log("="*60)

    # Create ITU
    itu = ITUClArithmeticAdditionIntI2x7O8()
    log(f"\n  Initial ITU:")
    log(f"    Neurons: {len(itu._circle)}")
    log(f"    Input bitwidth: {itu.meta.input_bitwidth}")
    log(f"    Output bitwidth: {itu.meta.output_bitwidth}")

    # Generate fixed test data for consistent evaluation
    test_data = generate_training_data(CONFIG['test_samples'])
    log(f"\n  Test data sample: {test_data[0]}")

    # Initial evaluation
    accuracy, correct, unknown, total = evaluate_itu(itu, test_data)
    log(f"\n  Initial accuracy: {accuracy*100:.1f}% ({correct}/{total})")

    best_accuracy = accuracy
    best_itu = deep_copy_itu(itu)
    generations_without_improvement = 0

    log(f"\n  Training started...")
    log("-"*60)

    for gen in range(1, CONFIG['max_generations'] + 1):
        # Generate fresh training data each generation
        train_data = generate_training_data(CONFIG['training_samples'])

        # Try multiple mutations per generation
        for _ in range(5):
            # Save current state
            old_circle = [(n._input_weights[:], n._input_skew) for n in itu._circle]
            old_len = len(itu._circle)

            # Mutate
            mutate_itu_manual(itu)

            # Evaluate
            new_accuracy, correct, unknown, total = evaluate_itu(itu, test_data)

            if new_accuracy > best_accuracy:
                # Improvement! Keep mutation
                best_accuracy = new_accuracy
                best_itu = deep_copy_itu(itu)
                generations_without_improvement = 0

                if gen % CONFIG['report_interval'] == 0 or new_accuracy >= CONFIG['target_accuracy']:
                    log(f"  Gen {gen:4d}: Accuracy {new_accuracy*100:5.1f}% ↑ ({correct}/{total}) Neurons: {len(itu._circle)}")
            elif new_accuracy >= best_accuracy:
                # Same or better - keep exploring
                pass
            else:
                # Worse - rollback
                # Restore old weights
                if len(itu._circle) == old_len:
                    for i, (weights, skew) in enumerate(old_circle):
                        itu._circle[i]._input_weights = weights
                        itu._circle[i]._input_skew = skew
                else:
                    # Neuron was added - can't easily rollback, accept it
                    pass

        generations_without_improvement += 1

        # Progress report
        if gen % CONFIG['report_interval'] == 0:
            curr_accuracy, correct, unknown, total = evaluate_itu(itu, test_data)
            if curr_accuracy < best_accuracy:
                log(f"  Gen {gen:4d}: Accuracy {curr_accuracy*100:5.1f}% (best: {best_accuracy*100:.1f}%) Neurons: {len(itu._circle)}")

        # Store generation data
        RESULTS["generations"].append({
            "generation": gen,
            "accuracy": best_accuracy,
            "neurons": len(itu._circle)
        })

        # Early stopping
        if best_accuracy >= CONFIG['target_accuracy']:
            log(f"\n  TARGET REACHED at generation {gen}!")
            break

        # Stagnation check
        if generations_without_improvement > 100:
            log(f"\n  Stagnation detected - reinitializing random weights...")
            # Reset some weights randomly
            for neuron in itu._circle:
                if random.random() < 0.3:  # 30% chance
                    neuron._input_weights = random_trit_vector(len(neuron._input_weights))
            generations_without_improvement = 0

    log("-"*60)
    log(f"\n  Training complete!")

    # Final evaluation
    final_accuracy, correct, unknown, total = evaluate_itu(best_itu, test_data)

    log(f"\n  Final Results:")
    log(f"    Best accuracy: {best_accuracy*100:.1f}%")
    log(f"    Final neurons: {len(best_itu._circle)}")

    RESULTS["best_accuracy"] = best_accuracy
    RESULTS["final_neurons"] = len(best_itu._circle)

    # Test on new random data
    log(f"\n  Validation on new random data:")
    val_data = generate_training_data(20)
    val_accuracy, correct, unknown, total = evaluate_itu(best_itu, val_data)
    log(f"    Validation accuracy: {val_accuracy*100:.1f}% ({correct}/{total})")

    RESULTS["validation_accuracy"] = val_accuracy

    # Show some examples
    log(f"\n  Sample predictions:")
    for i, row in enumerate(val_data[:5]):
        reflection = best_itu.reflect(row.a, row.b)
        result = reflection.integer if reflection.integer else "?"
        status = "✓" if result == row.c else "✗"
        log(f"    {status} {row.a:4d} + {row.b:4d} = {str(result):>4} (expected: {row.c:4d})")

    # Save results
    output_path = Path(__file__).parent / "AIGARTH_TRAINING_RESULTS.json"
    with open(output_path, 'w') as f:
        json.dump(RESULTS, f, indent=2)
    log(f"\n  Results saved to: {output_path}")

    log("\n" + "="*60)

    return best_accuracy >= CONFIG['target_accuracy']

if __name__ == "__main__":
    success = train()
    sys.exit(0 if success else 1)
