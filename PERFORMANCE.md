# Performance Benchmark Results

This document shows the performance trade-offs of FriendlyID, focusing on the two key aspects: CPU overhead vs I/O efficiency.

## Running the Benchmark

```bash
# Basic benchmark with 1000 UUIDs
python benchmark.py

# Custom count and iterations
python benchmark.py --count 10000 --iterations 5

# Verbose output with standard deviation
python benchmark.py --verbose
```

## Key Findings

The benchmark focuses on two fundamental aspects:

### ⚡ Serialization Performance (CPU)
- **Base62 encoding overhead**: ~6x slower than UUID string conversion
- **Per-ID cost**: ~3 microseconds additional overhead per UUID
- **Real impact**: 3ms overhead per 1,000 IDs (negligible for most applications)

**Analysis**: The base62 mathematical conversion requires more CPU cycles than simple string formatting. However, the overhead is measured in microseconds per ID, making it negligible for typical web applications.

### 📡 Bandwidth Efficiency (I/O)
- **Character savings**: 39% fewer characters (22 vs 36 chars per ID)
- **Bandwidth savings**: 39% less network traffic for text-based transmission
- **Real impact**: 14KB saved per 1,000 IDs in APIs, URLs, and logs

**Analysis**: FriendlyID provides substantial I/O benefits for text-based formats (JSON APIs, URLs, log files, CSV exports). Database storage uses the underlying UUID, so no storage savings there.

## Sample Results

Here's what the benchmark typically shows:

```
⚡ Serialization Performance (CPU)
==================================================
Operation                           Mean (ms)    
---------------------------------------------------------------------------
UUID -> string                      0.60
FriendlyID -> base62              3.70
UUID -> JSON                        0.71
FriendlyID -> JSON                3.72

💡 Performance Analysis:
   Base62 encoding is 6.1x slower than UUID string conversion
   Overhead: 3.10ms per 1,000 IDs
   Per ID: 3.10 microseconds

📡 Bandwidth Efficiency (I/O)
==================================================
String Length Comparison (1,000 IDs):
  Standard UUIDs:    36,000 chars (36 per ID)
  FriendlyIDs:     21,871 chars (22 per ID)
  Character savings: 39.2%

💡 I/O Impact Analysis:
   Network: 13.8 KB less data per 1,000 IDs
   Log files: 39.2% reduction in text-based storage
   URLs: 39.2% shorter (better for SEO and UX)
   Note: Database storage unchanged (stores UUID internally)
```

The benchmark provides concrete performance data. Run it with your expected workload to get numbers specific to your use case.
