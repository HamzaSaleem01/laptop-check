export type StatusEnum = 'PASS' | 'CAUTION' | 'FAIL' | 'NOT AVAILABLE' | 'NOT TESTED' | 'SKIPPED';

export interface CPUInfo {
  model: string;
  manufacturer: string;
  architecture: string;
  cores_physical?: number;
  threads_logical?: number;
  base_freq_mhz?: number;
  max_freq_mhz?: number;
  current_freq_mhz?: number;
  instruction_sets: string[];
  virtualization: boolean;
  usage_percent?: number;
  temperature_c?: number;
}

export interface RAMInfo {
  total_gb: number;
  available_gb: number;
  used_gb: number;
  memory_type: string;
  speed_mhz?: number;
  channels: string;
  modules_count?: number;
  bandwidth_gb_s?: number;
}

export interface GPUInfo {
  name: string;
  vendor: string;
  is_dedicated: boolean;
  vram_mb?: number;
  driver_version?: string;
  temperature_c?: number;
  utilization_pct?: number;
}

export interface StorageDriveInfo {
  device: string;
  model: string;
  media_type: string;
  capacity_gb: number;
  smart_status: string;
  health_pct?: number;
  temperature_c?: number;
  read_speed_mb_s?: number;
  write_speed_mb_s?: number;
}

export interface BatteryInfo {
  present: boolean;
  design_capacity_mwh?: number;
  full_charge_capacity_mwh?: number;
  current_capacity_mwh?: number;
  health_pct?: number;
  cycle_count?: number;
  category: string;
  is_charging?: boolean;
  ac_connected?: boolean;
  temperature_c?: number;
}

export interface OSInfo {
  system: string;
  release: string;
  version: string;
  architecture: string;
  kernel?: string;
  hostname: string;
}

export interface SystemHardwareSnapshot {
  timestamp: string;
  device_model: string;
  manufacturer: string;
  is_simulation: boolean;
  simulation_profile_name?: string;
  os: OSInfo;
  cpu: CPUInfo;
  ram: RAMInfo;
  gpus: GPUInfo[];
  storage: StorageDriveInfo[];
  battery: BatteryInfo;
}

export interface BenchmarkMetric {
  name: string;
  value: number;
  unit: string;
  description: string;
}

export interface BenchmarkResult {
  benchmark_id: string;
  display_name: string;
  duration_secs: number;
  score: number;
  metrics: BenchmarkMetric[];
  initial_performance?: number;
  sustained_performance?: number;
  degradation_pct?: number;
  status: StatusEnum;
  details: string;
}

export interface Anomaly {
  severity: 'INFO' | 'WARNING' | 'CRITICAL';
  component: string;
  title: string;
  description: string;
  recommendation: string;
}

export interface RequirementCriterion {
  key: string;
  label: string;
  priority: string;
  required_value: any;
  actual_value: any;
  unit: string;
  status: StatusEnum;
  notes: string;
}

export interface WorkloadMatchResult {
  profile_id: string;
  profile_name: string;
  overall_status: StatusEnum;
  suitability_summary: string;
  criteria: RequirementCriterion[];
}

export interface ThermalSample {
  timestamp: number;
  elapsed_secs: number;
  cpu_temp_c?: number;
  gpu_temp_c?: number;
  battery_temp_c?: number;
  cpu_freq_mhz?: number;
  cpu_usage_pct?: number;
  safety_level: string;
}

export interface DiagnosticReport {
  report_id: string;
  app_version: string;
  created_at: string;
  test_level: string;
  is_simulation: boolean;
  simulation_label?: string;
  hardware: SystemHardwareSnapshot;
  thermal_samples: ThermalSample[];
  benchmarks: BenchmarkResult[];
  workload_evaluations: WorkloadMatchResult[];
  anomalies: Anomaly[];
  summary_categories: Record<string, StatusEnum>;
  executive_summary?: string;
}
