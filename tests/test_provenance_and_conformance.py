"""Tests for Phase 0 & Phase 1: Provenance Data Contract & Hardware Conformance."""
import pytest
from fastapi.testclient import TestClient

from agent.models import (
    SystemHardwareSnapshot, FieldProvenance, ProvenanceStatus, ProvenanceConfidence,
    CPUInfo, RAMInfo, GPUInfo, StorageDriveInfo, BatteryInfo, OSInfo
)
from agent.hardware.linux_provider import LinuxHardwareProvider
from agent.hardware.simulated_provider import SimulatedHardwareProvider, SIMULATED_PRESETS
from agent.hardware.manager import get_hardware_snapshot
from web.backend.main import app

client = TestClient(app)

def test_provenance_model_validation():
    """Verifies that FieldProvenance serializes and conforms to redesign specification."""
    prov = FieldProvenance(
        key="cpu.logical_processors",
        value=12,
        unit="count",
        source="linux:/sys/devices/system/cpu/online",
        method="os_topology",
        confidence=ProvenanceConfidence.HIGH,
        status=ProvenanceStatus.REPORTED,
        limitations=[]
    )
    dumped = prov.model_dump()
    assert dumped["key"] == "cpu.logical_processors"
    assert dumped["value"] == 12
    assert dumped["status"] == "reported"
    assert dumped["confidence"] == "high"
    assert "observed_at" in dumped

def test_linux_hardware_provider_generates_provenance():
    """Verifies that LinuxHardwareProvider returns genuine system facts and real provenance records."""
    provider = LinuxHardwareProvider()
    snapshot = provider.get_full_snapshot()

    assert snapshot.schema_version == "2.0.0"
    assert isinstance(snapshot.provenance, dict)
    assert len(snapshot.provenance) > 0

    # CPU provenance
    assert "cpu.model" in snapshot.provenance
    cpu_prov = snapshot.provenance["cpu.model"]
    assert cpu_prov.status in [ProvenanceStatus.REPORTED, ProvenanceStatus.MEASURED]
    assert cpu_prov.confidence == ProvenanceConfidence.HIGH

    # Verifies no fake channels if physical SPD access is unavailable
    if snapshot.ram.channels == "Not available":
        assert "memory.channels" in snapshot.provenance
        assert snapshot.provenance["memory.channels"].status == ProvenanceStatus.UNAVAILABLE

    # Verifies battery provenance if physical battery exists
    if snapshot.battery.present and snapshot.battery.health_pct is not None:
        assert "battery.health_pct" in snapshot.provenance
        bat_prov = snapshot.provenance["battery.health_pct"]
        assert bat_prov.status == ProvenanceStatus.MEASURED
        assert bat_prov.unit == "percent"

def test_snapshot_redaction_sanitizes_identifiers():
    """Verifies that get_redacted_snapshot properly masks hostnames and serial numbers."""
    provider = LinuxHardwareProvider()
    snap = provider.get_full_snapshot()
    redacted = snap.get_redacted_snapshot()

    assert redacted.is_redacted is True
    assert redacted.os.hostname == "[REDACTED_HOSTNAME]"
    if snap.os.serial_number:
        assert redacted.os.serial_number == "[REDACTED_SERIAL]"
    assert "os.hostname" in redacted.redacted_fields

def test_simulation_presets_marked_as_synthetic_demonstrations():
    """Verifies that simulation presets are explicitly flagged with synthetic demonstration status."""
    for preset_key in SIMULATED_PRESETS:
        prov = SimulatedHardwareProvider(preset_key=preset_key)
        snap = prov.get_full_snapshot()

        assert snap.is_simulation is True
        assert "[SYNTHETIC DEMO]" in (snap.simulation_profile_name or "")
        assert "cpu.model" in snap.provenance
        assert snap.provenance["cpu.model"].status == ProvenanceStatus.SIMULATED
        assert snap.provenance["cpu.model"].confidence == ProvenanceConfidence.SIMULATED

def test_api_hardware_supports_redaction_parameter():
    """Verifies that the /api/hardware endpoint honors ?redact=true."""
    res = client.get("/api/hardware?simulate=true&preset=mid_range&redact=true")
    assert res.status_code == 200
    data = res.json()
    assert data["schema_version"] == "2.0.0"
    assert data["is_redacted"] is True
    assert data["os"]["hostname"] == "[REDACTED_HOSTNAME]"
