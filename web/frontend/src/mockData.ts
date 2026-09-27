import type { SystemHardwareSnapshot, DiagnosticReport } from './types';

export const MOCK_SIMULATION_PRESETS_LIST = [
  { id: 'low_end', label: '1. Low-End Budget Laptop (Celeron, 4GB RAM, eMMC)' },
  { id: 'mid_range', label: '2. Mid-Range Laptop (i5-1240P, 16GB RAM, NVMe)' },
  { id: 'high_performance', label: '3. High-Performance Workstation (i9, 64GB, RTX A4500)' },
  { id: 'thermally_limited', label: '4. Thermally Limited Laptop (Heavy Throttling)' },
  { id: 'battery_degraded', label: '5. Battery Degraded Laptop (42% Health, 980 Cycles)' },
  { id: 'storage_warning', label: '6. Storage Warning Laptop (SMART Failing)' },
];

export const MOCK_HARDWARE_PRESETS: Record<string, SystemHardwareSnapshot> = {
  mid_range: {
    timestamp: '2026-09-27 19:42:32',
    device_model: 'ThinkPad E14 Gen 4',
    manufacturer: 'Lenovo',
    is_simulation: true,
    simulation_profile_name: 'Mid-Range Productivity Laptop',
    os: {
      system: 'Linux',
      release: 'Ubuntu 24.04 LTS',
      version: '6.8.0-generic',
      architecture: 'x86_64',
      hostname: 'thinkpad-e14'
    },
    cpu: {
      model: '12th Gen Intel Core i5-1240P',
      manufacturer: 'Intel',
      architecture: 'x86_64',
      cores_physical: 12,
      threads_logical: 16,
      base_freq_mhz: 1700,
      max_freq_mhz: 4400,
      current_freq_mhz: 2800,
      instruction_sets: ['AVX', 'AVX2', 'FMA', 'AES', 'VMX'],
      virtualization: true,
      usage_percent: 8,
      temperature_c: 48
    },
    ram: {
      total_gb: 16,
      available_gb: 12.4,
      used_gb: 3.6,
      memory_type: 'DDR4',
      speed_mhz: 3200,
      channels: 'Dual Channel',
      modules_count: 2,
      bandwidth_gb_s: 25.6
    },
    gpus: [
      { name: 'Intel Iris Xe Graphics', vendor: 'Intel', is_dedicated: false, vram_mb: 2048 }
    ],
    storage: [
      {
        device: '/dev/nvme0n1',
        model: 'Samsung PM991a 512GB NVMe',
        media_type: 'NVMe SSD',
        capacity_gb: 476.9,
        smart_status: 'PASSED',
        health_pct: 98,
        read_speed_mb_s: 2800,
        write_speed_mb_s: 1800,
        temperature_c: 41
      }
    ],
    battery: {
      present: true,
      design_capacity_mwh: 57000,
      full_charge_capacity_mwh: 52400,
      health_pct: 91.9,
      cycle_count: 185,
      category: 'Healthy',
      is_charging: false,
      ac_connected: true,
      temperature_c: 31
    }
  },
  low_end: {
    timestamp: '2026-09-27 19:42:32',
    device_model: 'EcoBook 14 (Dual-Core Celeron)',
    manufacturer: 'BudgetTech',
    is_simulation: true,
    simulation_profile_name: 'Low-End Budget Laptop',
    os: {
      system: 'Linux',
      release: 'Ubuntu 22.04 LTS',
      version: '5.15.0-generic',
      architecture: 'x86_64',
      hostname: 'budget-ecobook'
    },
    cpu: {
      model: 'Intel Celeron N4020 @ 1.10GHz',
      manufacturer: 'Intel',
      architecture: 'x86_64',
      cores_physical: 2,
      threads_logical: 2,
      base_freq_mhz: 1100,
      max_freq_mhz: 2800,
      current_freq_mhz: 2100,
      instruction_sets: ['SSE4_2'],
      virtualization: true,
      usage_percent: 14,
      temperature_c: 42
    },
    ram: {
      total_gb: 4,
      available_gb: 1.6,
      used_gb: 2.4,
      memory_type: 'LPDDR4',
      speed_mhz: 2400,
      channels: 'Single Channel',
      modules_count: 1,
      bandwidth_gb_s: 9.6
    },
    gpus: [
      { name: 'Intel UHD Graphics 600', vendor: 'Intel', is_dedicated: false, vram_mb: 512 }
    ],
    storage: [
      {
        device: '/dev/mmcblk0',
        model: 'SanDisk 64GB eMMC',
        media_type: 'eMMC / Flash',
        capacity_gb: 58.2,
        smart_status: 'Operational',
        health_pct: 92,
        read_speed_mb_s: 180,
        write_speed_mb_s: 95
      }
    ],
    battery: {
      present: true,
      design_capacity_mwh: 35000,
      full_charge_capacity_mwh: 31500,
      health_pct: 90,
      cycle_count: 120,
      category: 'Healthy',
      is_charging: false,
      ac_connected: true,
      temperature_c: 29
    }
  },
  high_performance: {
    timestamp: '2026-09-27 19:42:32',
    device_model: 'Precision 7770 Workstation',
    manufacturer: 'Dell',
    is_simulation: true,
    simulation_profile_name: 'High-Performance Workstation Laptop',
    os: {
      system: 'Linux',
      release: 'Ubuntu 24.04 LTS',
      version: '6.8.0-generic',
      architecture: 'x86_64',
      hostname: 'dell-precision'
    },
    cpu: {
      model: '12th Gen Intel Core i9-12950HX',
      manufacturer: 'Intel',
      architecture: 'x86_64',
      cores_physical: 16,
      threads_logical: 24,
      base_freq_mhz: 2300,
      max_freq_mhz: 5000,
      current_freq_mhz: 3400,
      instruction_sets: ['AVX', 'AVX2', 'FMA', 'AES', 'VMX'],
      virtualization: true,
      usage_percent: 5,
      temperature_c: 44
    },
    ram: {
      total_gb: 64,
      available_gb: 56.8,
      used_gb: 7.2,
      memory_type: 'DDR5 ECC',
      speed_mhz: 4800,
      channels: 'Quad Channel',
      modules_count: 4,
      bandwidth_gb_s: 68.4
    },
    gpus: [
      { name: 'NVIDIA RTX A4500 Laptop GPU', vendor: 'NVIDIA', is_dedicated: true, vram_mb: 16384 },
      { name: 'Intel UHD Graphics', vendor: 'Intel', is_dedicated: false, vram_mb: 2048 }
    ],
    storage: [
      {
        device: '/dev/nvme0n1',
        model: 'Samsung 980 Pro 2TB NVMe',
        media_type: 'NVMe SSD',
        capacity_gb: 1907.7,
        smart_status: 'PASSED',
        health_pct: 99,
        read_speed_mb_s: 6900,
        write_speed_mb_s: 5000,
        temperature_c: 38
      }
    ],
    battery: {
      present: true,
      design_capacity_mwh: 93000,
      full_charge_capacity_mwh: 89000,
      health_pct: 95.7,
      cycle_count: 45,
      category: 'Healthy',
      is_charging: true,
      ac_connected: true,
      temperature_c: 32
    }
  },
  thermally_limited: {
    timestamp: '2026-09-27 19:42:32',
    device_model: 'AeroBook 13 Pro (Clogged Fan)',
    manufacturer: 'SlimTech',
    is_simulation: true,
    simulation_profile_name: 'Thermally Limited Laptop',
    os: {
      system: 'Linux',
      release: 'Ubuntu 22.04 LTS',
      version: '5.15.0-generic',
      architecture: 'x86_64',
      hostname: 'aerobook-hot'
    },
    cpu: {
      model: '11th Gen Intel Core i7-1165G7',
      manufacturer: 'Intel',
      architecture: 'x86_64',
      cores_physical: 4,
      threads_logical: 8,
      base_freq_mhz: 2800,
      max_freq_mhz: 4700,
      current_freq_mhz: 1800,
      instruction_sets: ['AVX', 'AVX2', 'FMA'],
      virtualization: true,
      usage_percent: 25,
      temperature_c: 72
    },
    ram: {
      total_gb: 16,
      available_gb: 11.2,
      used_gb: 4.8,
      memory_type: 'LPDDR4X',
      speed_mhz: 4266,
      channels: 'Dual Channel',
      modules_count: 2,
      bandwidth_gb_s: 22.4
    },
    gpus: [
      { name: 'Intel Iris Xe Graphics', vendor: 'Intel', is_dedicated: false, vram_mb: 2048 }
    ],
    storage: [
      {
        device: '/dev/nvme0n1',
        model: 'SK Hynix 512GB NVMe',
        media_type: 'NVMe SSD',
        capacity_gb: 476.9,
        smart_status: 'PASSED',
        health_pct: 94,
        read_speed_mb_s: 2200,
        write_speed_mb_s: 1400,
        temperature_c: 58
      }
    ],
    battery: {
      present: true,
      design_capacity_mwh: 52000,
      full_charge_capacity_mwh: 43000,
      health_pct: 82.7,
      cycle_count: 340,
      category: 'Healthy',
      is_charging: false,
      ac_connected: true,
      temperature_c: 44
    }
  },
  battery_degraded: {
    timestamp: '2026-09-27 19:42:32',
    device_model: 'EliteBook 840 G6',
    manufacturer: 'RefurbTech',
    is_simulation: true,
    simulation_profile_name: 'Battery Degraded Laptop',
    os: {
      system: 'Linux',
      release: 'Ubuntu 22.04 LTS',
      version: '5.15.0-generic',
      architecture: 'x86_64',
      hostname: 'elitebook-worn'
    },
    cpu: {
      model: 'Intel Core i5-8365U',
      manufacturer: 'Intel',
      architecture: 'x86_64',
      cores_physical: 4,
      threads_logical: 8,
      base_freq_mhz: 1600,
      max_freq_mhz: 4100,
      current_freq_mhz: 2200,
      instruction_sets: ['AVX', 'AVX2'],
      virtualization: true,
      usage_percent: 10,
      temperature_c: 45
    },
    ram: {
      total_gb: 8,
      available_gb: 4.8,
      used_gb: 3.2,
      memory_type: 'DDR4',
      speed_mhz: 2400,
      channels: 'Single Channel',
      modules_count: 1,
      bandwidth_gb_s: 14.2
    },
    gpus: [
      { name: 'Intel UHD Graphics 620', vendor: 'Intel', is_dedicated: false, vram_mb: 1024 }
    ],
    storage: [
      {
        device: '/dev/sda',
        model: 'Crucial 256GB SATA SSD',
        media_type: 'SATA SSD',
        capacity_gb: 238.5,
        smart_status: 'PASSED',
        health_pct: 88,
        read_speed_mb_s: 510,
        write_speed_mb_s: 460
      }
    ],
    battery: {
      present: true,
      design_capacity_mwh: 50000,
      full_charge_capacity_mwh: 21000,
      health_pct: 42,
      cycle_count: 980,
      category: 'Significantly Reduced',
      is_charging: false,
      ac_connected: false,
      temperature_c: 34
    }
  },
  storage_warning: {
    timestamp: '2026-09-27 19:42:32',
    device_model: 'ProBook 450 G5',
    manufacturer: 'OldWorkstation',
    is_simulation: true,
    simulation_profile_name: 'Storage Warning Laptop',
    os: {
      system: 'Linux',
      release: 'Ubuntu 20.04 LTS',
      version: '5.4.0-generic',
      architecture: 'x86_64',
      hostname: 'probook-disk-fail'
    },
    cpu: {
      model: 'Intel Core i5-8250U',
      manufacturer: 'Intel',
      architecture: 'x86_64',
      cores_physical: 4,
      threads_logical: 8,
      base_freq_mhz: 1600,
      max_freq_mhz: 3400,
      current_freq_mhz: 2100,
      instruction_sets: ['AVX', 'AVX2'],
      virtualization: true,
      usage_percent: 18,
      temperature_c: 50
    },
    ram: {
      total_gb: 8,
      available_gb: 4.2,
      used_gb: 3.8,
      memory_type: 'DDR4',
      speed_mhz: 2400,
      channels: 'Single Channel',
      modules_count: 1,
      bandwidth_gb_s: 14.2
    },
    gpus: [
      { name: 'Intel UHD Graphics 620', vendor: 'Intel', is_dedicated: false, vram_mb: 1024 }
    ],
    storage: [
      {
        device: '/dev/sda',
        model: 'Seagate BarraCuda 1TB HDD',
        media_type: 'HDD (Rotating Platter)',
        capacity_gb: 931.5,
        smart_status: 'WARNING / REALLOCATED SECTORS',
        health_pct: 54,
        read_speed_mb_s: 68,
        write_speed_mb_s: 42,
        temperature_c: 46
      }
    ],
    battery: {
      present: true,
      design_capacity_mwh: 48000,
      full_charge_capacity_mwh: 36000,
      health_pct: 75,
      cycle_count: 410,
      category: 'Reduced Capacity',
      is_charging: false,
      ac_connected: true,
      temperature_c: 30
    }
  }
};

export function createMockReport(presetId: string, testLevel: string, customHw?: SystemHardwareSnapshot): DiagnosticReport {
  const hw = customHw || MOCK_HARDWARE_PRESETS[presetId] || MOCK_HARDWARE_PRESETS.mid_range;
  const isCustom = !!customHw;
  const isFail = !isCustom && (presetId === 'low_end' || presetId === 'storage_warning');
  const isCaution = !isCustom && (presetId === 'mid_range' || presetId === 'battery_degraded' || presetId === 'thermally_limited');

  return {
    report_id: `LC-${isCustom ? 'HOST' : 'SIM'}-${Date.now().toString(36).toUpperCase()}`,
    app_version: '1.0.0',
    created_at: new Date().toISOString().replace('T', ' ').slice(0, 19),
    test_level: testLevel,
    is_simulation: !isCustom,
    simulation_label: isCustom ? 'Host Device Live Scan' : hw.simulation_profile_name,
    hardware: hw,
    summary_categories: {
      CPU: isCustom ? (hw.cpu.threads_logical && hw.cpu.threads_logical >= 4 ? 'PASS' : 'CAUTION') : (presetId === 'thermally_limited' ? 'CAUTION' : (presetId === 'low_end' ? 'CAUTION' : 'PASS')),
      RAM: isCustom ? (hw.ram.total_gb >= 16 ? 'PASS' : (hw.ram.total_gb >= 8 ? 'CAUTION' : 'FAIL')) : (presetId === 'low_end' ? 'FAIL' : 'PASS'),
      Storage: isCustom ? 'PASS' : (presetId === 'storage_warning' ? 'FAIL' : 'PASS'),
      GPU: 'PASS',
      Thermals: isCustom ? 'PASS' : (presetId === 'thermally_limited' ? 'CAUTION' : 'PASS'),
      Battery: isCustom ? (hw.battery.health_pct && hw.battery.health_pct < 60 ? 'CAUTION' : 'PASS') : (presetId === 'battery_degraded' ? 'FAIL' : 'PASS'),
      Stability: 'PASS'
    },
    anomalies: (() => {
      if (isCustom) {
        if (hw.ram.total_gb < 16) {
          return [
            {
              severity: 'INFO',
              component: 'Memory',
              title: 'Host Memory Sizing Observation',
              description: `Host system reports ${hw.ram.total_gb.toFixed(1)} GB RAM detected via browser WebAPI.`,
              recommendation: 'For heavy computational materials science workloads or large Docker stacks, 16+ GB is recommended.'
            }
          ];
        }
        return [];
      }
      if (presetId === 'storage_warning') {
        return [
          {
            severity: 'CRITICAL',
            component: 'Storage',
            title: 'Failing Mechanical HDD SMART Status',
            description: 'Drive reports reallocated sector count exceeding critical threshold with high read latency.',
            recommendation: 'Back up all personal data immediately and replace drive with modern SATA or NVMe SSD.'
          }
        ];
      }
      if (presetId === 'battery_degraded') {
        return [
          {
            severity: 'WARNING',
            component: 'Battery',
            title: 'Severe Battery Capacity Degradation Detected',
            description: 'Battery health measured at 42% of design capacity after 980 recharge cycles.',
            recommendation: 'Replace the internal battery pack to restore portable operating runtime.'
          }
        ];
      }
      if (presetId === 'thermally_limited') {
        return [
          {
            severity: 'WARNING',
            component: 'Cooling / Thermals',
            title: 'Significant Thermal Throttling Under Continuous Load',
            description: 'CPU core temperatures exceeded 91°C causing a 34% drop in sustained clock frequency.',
            recommendation: 'Clean internal cooling fans, clear heatsink exhaust fins, and consider repasting CPU.'
          }
        ];
      }
      return [];
    })(),
    workload_evaluations: [
      {
        profile_id: 'comp_materials_science',
        profile_name: 'Computational Materials Science / Physics',
        overall_status: isFail ? 'FAIL' : (isCaution ? 'CAUTION' : 'PASS'),
        suitability_summary: isFail 
          ? 'This system does not satisfy minimum requirements for Density Functional Theory workloads.' 
          : 'Conditionally suitable with minor computational compromises.',
        criteria: [
          {
            key: 'cpu_cores',
            label: 'CPU Physical Cores',
            priority: 'VERY HIGH',
            required_value: 'Min 6 (Pref 12)',
            actual_value: `${hw.cpu.cores_physical} cores`,
            unit: 'cores',
            status: (hw.cpu.cores_physical || 0) >= 12 ? 'PASS' : ((hw.cpu.cores_physical || 0) >= 6 ? 'PASS' : 'FAIL'),
            notes: (hw.cpu.cores_physical || 0) >= 6 ? 'Core count satisfies requirement.' : 'Below minimum recommended core count.'
          },
          {
            key: 'ram_capacity',
            label: 'RAM Capacity',
            priority: 'VERY HIGH',
            required_value: 'Min 16.0 GB (Pref 32.0 GB)',
            actual_value: `${hw.ram.total_gb.toFixed(1)} GB`,
            unit: 'GB',
            status: hw.ram.total_gb >= 32 ? 'PASS' : (hw.ram.total_gb >= 16 ? 'CAUTION' : 'FAIL'),
            notes: hw.ram.total_gb >= 16 ? 'Meets minimum capacity.' : 'Insufficient memory for realistic DFT plane waves.'
          }
        ]
      },
      {
        profile_id: 'programming',
        profile_name: 'Software Development & Engineering',
        overall_status: hw.ram.total_gb >= 16 ? 'PASS' : (hw.ram.total_gb >= 8 ? 'CAUTION' : 'FAIL'),
        suitability_summary: hw.ram.total_gb >= 16 
          ? 'Well suited for multi-container Docker, IDEs, and local test runners.'
          : 'Suitable for basic scripting, but may bottleneck on large container stacks.',
        criteria: [
          {
            key: 'ram_dev',
            label: 'System RAM',
            priority: 'VERY HIGH',
            required_value: 'Min 16.0 GB',
            actual_value: `${hw.ram.total_gb.toFixed(1)} GB`,
            unit: 'GB',
            status: hw.ram.total_gb >= 16 ? 'PASS' : 'CAUTION',
            notes: 'Evaluation based on development memory load.'
          }
        ]
      }
    ],
    benchmarks: [
      {
        benchmark_id: 'cpu_multi_core',
        display_name: 'CPU Multi-Core & Sustained Performance',
        duration_secs: 15,
        score: hw.cpu.cores_physical ? hw.cpu.cores_physical * 450 : 2000,
        status: 'PASS',
        details: 'Evaluated compute throughput and sustained clock frequency.',
        metrics: [
          { name: 'Initial Performance', value: hw.cpu.cores_physical ? hw.cpu.cores_physical * 620 : 2500, unit: 'k ops/sec', description: 'Initial burst multi-core rate' },
          { name: 'Sustained Performance', value: hw.cpu.cores_physical ? hw.cpu.cores_physical * 580 : 2200, unit: 'k ops/sec', description: 'Continuous multi-threaded load' }
        ]
      },
      {
        benchmark_id: 'ram_bandwidth',
        display_name: 'RAM Memory Bandwidth & Integrity',
        duration_secs: 5,
        score: Math.round(hw.ram.bandwidth_gb_s || 20),
        status: 'PASS',
        details: 'Sequential memory throughput verified.',
        metrics: [
          { name: 'Average Bandwidth', value: Math.round((hw.ram.bandwidth_gb_s || 20) * 10) / 10, unit: 'GB/s', description: 'Mean RAM memory throughput' }
        ]
      },
      {
        benchmark_id: 'storage_sequential',
        display_name: 'Storage Sequential Read/Write',
        duration_secs: 6,
        score: Math.round((hw.storage[0]?.read_speed_mb_s || 1500) / 10),
        status: presetId === 'storage_warning' ? 'FAIL' : 'PASS',
        details: 'Non-destructive sequential file transfer performance.',
        metrics: [
          { name: 'Sequential Read', value: hw.storage[0]?.read_speed_mb_s || 1800, unit: 'MB/s', description: 'Buffered sequential read speed' },
          { name: 'Sequential Write', value: hw.storage[0]?.write_speed_mb_s || 1200, unit: 'MB/s', description: 'Controlled temporary file write speed' }
        ]
      }
    ],
    thermal_samples: [
      { elapsed_secs: 1.0, cpu_temp_c: 48, cpu_freq_mhz: 2800, timestamp: 1790520001, safety_level: 'NORMAL' },
      { elapsed_secs: 3.0, cpu_temp_c: 58, cpu_freq_mhz: 2750, timestamp: 1790520003, safety_level: 'NORMAL' },
      { elapsed_secs: 6.0, cpu_temp_c: 66, cpu_freq_mhz: 2700, timestamp: 1790520006, safety_level: 'NORMAL' },
      { elapsed_secs: 9.0, cpu_temp_c: 69, cpu_freq_mhz: 2650, timestamp: 1790520009, safety_level: 'NORMAL' },
      { elapsed_secs: 12.0, cpu_temp_c: 71, cpu_freq_mhz: 2600, timestamp: 1790520012, safety_level: 'NORMAL' }
    ]
  };
}
