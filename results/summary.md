# Experiment results

## Setup

- Python: 3.10.10
- Platform: Windows-10-10.0.26200-SP0
- Processor: Intel64 Family 6 Model 140 Stepping 1, GenuineIntel
- Depth limit: 3 plies
- Timing: median of 5 runs if a run takes <0.5 s, else 1 run
- Memory: tracemalloc peak in a separate run, skipped (-) when a search takes >5 s; max_depth = recursion depth
- Quick mode: True
- Total runtime: 234 s

## Initial states

- **S0** - Official start (attacker to move, 10 plies left)
- **S1** - After Exploit(H1) (defender to move)
- **S2** - Worked-example line: E(H1), Patch(H3), E(H4)
- **S3** - Attacker holds H3, next to the database (attacker to move)
- **S4** - Database H5 already compromised (defender to move)
- **S5** - Attacker via H2-H4-H6, 4 plies left (attacker to move)

## Experiment 1: algorithm comparison

| state | algorithm | ordering | move | value | optimal_value | regret | expanded | leaves | pruned | max_depth | time_s | peak_mem_kb |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S0 | minimax | naive | Exploit(H1) | -44 | -44 | 0 | 2402797 | 5648999 | 0 | 10 | 59.26313 | - |
| S0 | minimax | smart | Exploit(H1) | -44 | -44 | 0 | 2402797 | 5648999 | 0 | 10 | 61.94974 | - |
| S0 | alphabeta | naive | Exploit(H1) | -44 | -44 | 0 | 15277 | 12617 | 13588 | 10 | 0.2189 | 12.1 |
| S0 | alphabeta | smart | Exploit(H1) | -44 | -44 | 0 | 17900 | 16433 | 23274 | 10 | 0.29401 | 9.3 |
| S0 | minimax-d3 | naive | Exploit(H1) | -33 | -44 | 0 | 61 | 179 | 0 | 3 | 0.00302 | 4.1 |
| S0 | minimax-d3 | smart | Exploit(H1) | -33 | -44 | 0 | 61 | 179 | 0 | 3 | 0.00301 | 3.2 |
| S0 | alphabeta-d3 | naive | Exploit(H1) | -33 | -44 | 0 | 27 | 32 | 82 | 3 | 0.00074 | 3.3 |
| S0 | alphabeta-d3 | smart | Exploit(H1) | -33 | -44 | 0 | 25 | 30 | 82 | 3 | 0.00091 | 3.2 |
| S1 | minimax | naive | Restore(H1) | -44 | -44 | 0 | 1126556 | 2468041 | 0 | 9 | 26.76851 | - |
| S1 | minimax | smart | Patch(H3) | -44 | -44 | 0 | 1126556 | 2468041 | 0 | 9 | 27.64224 | - |
| S1 | alphabeta | naive | Restore(H1) | -44 | -44 | 0 | 13867 | 11679 | 12580 | 9 | 0.20358 | 11.2 |
| S1 | alphabeta | smart | Patch(H3) | -44 | -44 | 0 | 7720 | 6189 | 12050 | 9 | 0.12018 | 8.2 |
| S1 | minimax-d3 | naive | Restore(H1) | -10 | -44 | 0 | 90 | 940 | 0 | 3 | 0.01577 | 4.8 |
| S1 | minimax-d3 | smart | Restore(H1) | -10 | -44 | 0 | 90 | 940 | 0 | 3 | 0.01517 | 4.8 |
| S1 | alphabeta-d3 | naive | Restore(H1) | -10 | -44 | 0 | 42 | 249 | 72 | 3 | 0.00391 | 4.9 |
| S1 | alphabeta-d3 | smart | Restore(H1) | -10 | -44 | 0 | 47 | 287 | 99 | 3 | 0.00502 | 4.8 |
| S2 | minimax | naive | Patch(H6) | -44 | -44 | 0 | 19206 | 37771 | 0 | 7 | 0.4064 | 8.8 |
| S2 | minimax | smart | Patch(H6) | -44 | -44 | 0 | 19206 | 37771 | 0 | 7 | 0.42483 | 8.6 |
| S2 | alphabeta | naive | Patch(H6) | -44 | -44 | 0 | 2060 | 1864 | 1311 | 7 | 0.02862 | 8.8 |
| S2 | alphabeta | smart | Patch(H6) | -44 | -44 | 0 | 1544 | 1316 | 1918 | 7 | 0.02321 | 6.9 |
| S2 | minimax-d3 | naive | Pass | -27 | -44 | 60 | 86 | 357 | 0 | 3 | 0.00576 | 4.7 |
| S2 | minimax-d3 | smart | Pass | -27 | -44 | 60 | 86 | 357 | 0 | 3 | 0.00593 | 4.6 |
| S2 | alphabeta-d3 | naive | Pass | -27 | -44 | 60 | 48 | 130 | 98 | 3 | 0.00242 | 4.9 |
| S2 | alphabeta-d3 | smart | Pass | -27 | -44 | 60 | 46 | 132 | 84 | 3 | 0.00238 | 4.7 |
| S3 | minimax | naive | Exploit(H5) | -110 | -110 | 0 | 24529 | 90855 | 0 | 6 | 0.92799 | 7.6 |
| S3 | minimax | smart | Exploit(H5) | -110 | -110 | 0 | 24529 | 90855 | 0 | 6 | 0.96433 | 7.5 |
| S3 | alphabeta | naive | Exploit(H5) | -110 | -110 | 0 | 3707 | 7254 | 4822 | 6 | 0.09403 | 7.8 |
| S3 | alphabeta | smart | Exploit(H5) | -110 | -110 | 0 | 547 | 502 | 1413 | 6 | 0.01217 | 7.5 |
| S3 | minimax-d3 | naive | Exploit(H5) | -208 | -110 | 0 | 101 | 428 | 0 | 3 | 0.0069 | 3.4 |
| S3 | minimax-d3 | smart | Exploit(H5) | -208 | -110 | 0 | 101 | 428 | 0 | 3 | 0.00711 | 3.4 |
| S3 | alphabeta-d3 | naive | Exploit(H5) | -208 | -110 | 0 | 73 | 162 | 162 | 3 | 0.00296 | 3.5 |
| S3 | alphabeta-d3 | smart | Exploit(H5) | -208 | -110 | 0 | 29 | 40 | 151 | 3 | 0.00082 | 3.3 |
| S4 | minimax | naive | Restore(H5) | -110 | -110 | 0 | 5366 | 20298 | 0 | 5 | 0.21826 | 7.0 |
| S4 | minimax | smart | Restore(H5) | -110 | -110 | 0 | 5366 | 20298 | 0 | 5 | 0.2204 | 6.8 |
| S4 | alphabeta | naive | Restore(H5) | -110 | -110 | 0 | 1363 | 3089 | 2042 | 5 | 0.03635 | 7.2 |
| S4 | alphabeta | smart | Restore(H5) | -110 | -110 | 0 | 72 | 56 | 171 | 5 | 0.00107 | 4.1 |
| S4 | minimax-d3 | naive | Restore(H5) | -50 | -110 | 0 | 108 | 1031 | 0 | 3 | 0.01646 | 4.9 |
| S4 | minimax-d3 | smart | Restore(H5) | -50 | -110 | 0 | 108 | 1031 | 0 | 3 | 0.01647 | 4.8 |
| S4 | alphabeta-d3 | naive | Restore(H5) | -50 | -110 | 0 | 63 | 366 | 163 | 3 | 0.00546 | 4.9 |
| S4 | alphabeta-d3 | smart | Restore(H5) | -50 | -110 | 0 | 26 | 39 | 112 | 3 | 0.00083 | 3.5 |
| S5 | minimax | naive | Exploit(H3) | -65 | -65 | 0 | 372 | 3133 | 0 | 4 | 0.03269 | 5.4 |
| S5 | minimax | smart | Exploit(H3) | -65 | -65 | 0 | 372 | 3133 | 0 | 4 | 0.03437 | 5.3 |
| S5 | alphabeta | naive | Exploit(H3) | -65 | -65 | 0 | 151 | 831 | 329 | 4 | 0.00986 | 5.6 |
| S5 | alphabeta | smart | Exploit(H3) | -65 | -65 | 0 | 102 | 433 | 384 | 4 | 0.00518 | 5.4 |
| S5 | minimax-d3 | naive | Exploit(H3) | -120 | -65 | 0 | 81 | 291 | 0 | 3 | 0.00487 | 3.3 |
| S5 | minimax-d3 | smart | Exploit(H3) | -120 | -65 | 0 | 81 | 291 | 0 | 3 | 0.00498 | 3.3 |
| S5 | alphabeta-d3 | naive | Exploit(H3) | -120 | -65 | 0 | 58 | 111 | 111 | 3 | 0.00216 | 3.4 |
| S5 | alphabeta-d3 | smart | Exploit(H3) | -120 | -65 | 0 | 38 | 57 | 108 | 3 | 0.00125 | 3.4 |

## Experiment 2: depth sweep from S0

| depth | algorithm | ordering | move | value | expanded | visited | pruned | time_s |
|---|---|---|---|---|---|---|---|---|
| 1 | minimax | naive | Exploit(H1) | -43.333333333333336 | 1 | 4 | 0 | 7e-05 |
| 1 | alphabeta | naive | Exploit(H1) | -43.333333333333336 | 1 | 4 | 0 | 5e-05 |
| 1 | alphabeta | smart | Exploit(H1) | -43.333333333333336 | 1 | 4 | 0 | 8e-05 |
| 2 | minimax | naive | Exploit(H2) | -17 | 4 | 61 | 0 | 0.00091 |
| 2 | alphabeta | naive | Exploit(H2) | -17 | 4 | 43 | 18 | 0.00061 |
| 2 | alphabeta | smart | Exploit(H2) | -17 | 4 | 43 | 18 | 0.00063 |
| 3 | minimax | naive | Exploit(H1) | -33 | 61 | 240 | 0 | 0.00284 |
| 3 | alphabeta | naive | Exploit(H1) | -33 | 27 | 59 | 82 | 0.00069 |
| 3 | alphabeta | smart | Exploit(H1) | -33 | 25 | 55 | 82 | 0.00085 |
| 4 | minimax | naive | Exploit(H1) | -10 | 240 | 2679 | 0 | 0.04123 |
| 4 | alphabeta | naive | Exploit(H1) | -10 | 61 | 361 | 210 | 0.00538 |
| 4 | alphabeta | smart | Exploit(H1) | -10 | 98 | 697 | 204 | 0.01033 |
| 5 | minimax | naive | Exploit(H1) | -25 | 2679 | 10523 | 0 | 0.1372 |
| 5 | alphabeta | naive | Exploit(H1) | -25 | 365 | 703 | 722 | 0.00869 |
| 5 | alphabeta | smart | Exploit(H1) | -25 | 682 | 1380 | 1612 | 0.02075 |
| 6 | minimax | naive | Exploit(H1) | -20 | 10523 | 49920 | 0 | 0.74356 |
| 6 | alphabeta | naive | Exploit(H1) | -20 | 833 | 2579 | 1199 | 0.03359 |
| 6 | alphabeta | smart | Exploit(H1) | -20 | 1420 | 4279 | 2094 | 0.05715 |
| 7 | minimax | naive | Exploit(H1) | -35 | 49920 | 183505 | 0 | 2.3073 |
| 7 | alphabeta | naive | Exploit(H1) | -35 | 2342 | 4034 | 4623 | 0.04644 |
| 7 | alphabeta | smart | Exploit(H1) | -35 | 3885 | 7065 | 9589 | 0.08447 |
| 8 | minimax | naive | Exploit(H1) | -35 | 182644 | 698824 | 0 | 8.60778 |
| 8 | alphabeta | naive | Exploit(H1) | -35 | 4036 | 9070 | 4644 | 0.10804 |
| 8 | alphabeta | smart | Exploit(H1) | -35 | 5454 | 10680 | 9504 | 0.12884 |
| 9 | alphabeta | naive | Exploit(H1) | -44 | 9628 | 15246 | 13450 | 0.1638 |
| 9 | alphabeta | smart | Exploit(H1) | -44 | 15586 | 26952 | 28349 | 0.31098 |
| 10 | alphabeta | naive | Exploit(H1) | -44 | 15277 | 27894 | 13588 | 0.22582 |
| 10 | alphabeta | smart | Exploit(H1) | -44 | 17900 | 34333 | 23274 | 0.29838 |

## Experiment 3: self-play from S0

| attacker | defender | final_utility | exfiltrated | total_nodes | moves |
|---|---|---|---|---|---|
| optimal | optimal | -44 | False | 56172 | Exploit(H1) Restore(H1) ZeroDay(H1) Patch(H3) Exploit(H4) Patch(H6) Exploit(H2) Pass Pass Pass |
| optimal | depth-3 | -90 | False | 31161 | Exploit(H1) Restore(H1) ZeroDay(H1) Pass Exploit(H3) Restore(H3) Exploit(H4) Pass Exploit(H6) Pass |
| depth-3 | optimal | -44 | False | 26635 | Exploit(H1) Restore(H1) ZeroDay(H1) Patch(H3) Exploit(H4) Patch(H6) Exploit(H2) Pass Pass Pass |
| depth-3 | depth-3 | -60 | False | 953 | Exploit(H1) Restore(H1) ZeroDay(H1) Pass Exploit(H4) Pass Exploit(H3) Pass Exploit(H5) Restore(H5) |
