"""
energy.py — Energy Budget & RLM Context Preserver for Agentic Engine.

Maintains:
- Active token/context budget monitoring
- Automatic refueling trigger when headroom < 20%
- RLM context window compaction and snapshot tracking
"""

import time
from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class EnergyBudget:
    """Manages active LLM context energy, token budget, and automatic refueling."""
    max_energy_tokens: int = 150_000
    consumed_tokens: int = 0
    refuel_count: int = 0
    checkpoint_history: List[str] = field(default_factory=list)

    @property
    def remaining_energy(self) -> int:
        return max(0, self.max_energy_tokens - self.consumed_tokens)

    @property
    def energy_percentage(self) -> float:
        if self.max_energy_tokens <= 0:
            return 0.0
        return (self.remaining_energy / self.max_energy_tokens) * 100.0

    def consume(self, tokens: int) -> None:
        self.consumed_tokens += max(0, tokens)

    def needs_refuel(self) -> bool:
        """Returns True if context headroom is critically low (< 20%)."""
        return self.energy_percentage < 20.0

    def refuel(self, snapshot_id: str) -> None:
        """Compacts state, resets active window pressure, and logs checkpoint."""
        self.checkpoint_history.append(snapshot_id)
        self.refuel_count += 1
        # RLM compression frees up 85% of active pressure into persistent external snapshots
        self.consumed_tokens = int(self.consumed_tokens * 0.15)
