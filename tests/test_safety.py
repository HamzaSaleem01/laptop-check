"""Unit tests for LaptopCheck Safety Controller."""
import pytest
from agent.safety.controller import SafetyController
from agent.config import SafetyThresholds
from agent.models import SafetyLevel

def test_safety_normal_operation():
    safety = SafetyController()
    sample = safety.evaluate(cpu_temp=45.0, gpu_temp=42.0, battery_temp=30.0, elapsed_secs=1.0)
    assert sample.safety_level == SafetyLevel.NORMAL
    assert not safety.is_stopped()
    assert not safety.is_paused()

def test_safety_warning_trigger():
    thresholds = SafetyThresholds(cpu_temp_warning=80.0, cpu_temp_emergency_stop=95.0)
    safety = SafetyController(thresholds=thresholds)
    sample = safety.evaluate(cpu_temp=82.0, elapsed_secs=2.0)
    assert sample.safety_level == SafetyLevel.WARNING
    assert not safety.is_stopped()

def test_safety_reduce_load_trigger():
    thresholds = SafetyThresholds(cpu_temp_reduce_load=90.0, cpu_temp_emergency_stop=95.0)
    safety = SafetyController(thresholds=thresholds)
    sample = safety.evaluate(cpu_temp=91.0, elapsed_secs=3.0)
    assert sample.safety_level == SafetyLevel.REDUCE_LOAD
    assert not safety.is_stopped()

def test_safety_emergency_stop():
    thresholds = SafetyThresholds(cpu_temp_emergency_stop=95.0)
    safety = SafetyController(thresholds=thresholds)
    sample = safety.evaluate(cpu_temp=96.0, elapsed_secs=4.0)
    assert sample.safety_level == SafetyLevel.STOP
    assert safety.is_stopped()

def test_manual_user_stop():
    safety = SafetyController()
    assert not safety.is_stopped()
    safety.request_stop("User clicked STOP TEST")
    assert safety.is_stopped()
    assert safety.get_current_level() == SafetyLevel.STOP
