"""Unit tests for Hardware Providers and Simulation Mode."""
from agent.hardware.manager import get_hardware_snapshot, list_simulation_presets
from agent.hardware.simulated_provider import SIMULATED_PRESETS

def test_native_hardware_snapshot():
    snapshot = get_hardware_snapshot(simulate=False)
    assert snapshot is not None
    assert snapshot.is_simulation is False
    assert snapshot.cpu.cores_physical is not None
    assert snapshot.ram.total_gb > 0.0
    assert snapshot.os.system in ["Linux", "Windows"]

def test_all_simulation_presets_valid():
    presets = list_simulation_presets()
    assert len(presets) == 6
    expected_ids = {"low_end", "mid_range", "high_performance", "thermally_limited", "battery_degraded", "storage_warning"}
    actual_ids = {p["id"] for p in presets}
    assert expected_ids == actual_ids

    for p_id in expected_ids:
        snap = get_hardware_snapshot(simulate=True, preset=p_id)
        assert snap.is_simulation is True
        assert snap.simulation_profile_name is not None
        assert snap.cpu.model != "Not available"
        assert snap.ram.total_gb > 0.0
