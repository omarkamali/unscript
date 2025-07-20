# Performance Report - Version 0.0.4

**Generated:** 2025-07-20T16:10:45.589907
**Python Version:** 3.13.3 (main, Apr  8 2025, 13:54:08) [Clang 17.0.0 (clang-1700.0.13.3)]

## Summary

| Function | Best Performance | Typical Use Case | Notes |
|----------|------------------|------------------|--------|
| `clean_text` | 1,802,741 chars/sec | General text cleaning | Handles URLs, mentions, emojis |
| `clean_script` | 66,284 chars/sec | Script-specific filtering | Performance varies by script |
| `unscript` | 60,244 chars/sec | Complete text processing | Combines cleaning + filtering |
| `detect_script` | 434,904 chars/sec | Script detection | Slower for mixed scripts |
| `in_range` | 2,391,290 calls/sec | Character checking | Very fast single-char ops |

## Detailed Results

### clean_text

| Text Size | Length | Mean (ms) | Median (ms) | Std Dev (ms) | Chars/sec |
|-----------|--------|-----------|-------------|--------------|-----------|
| small_text | 211 | 0.1181 | 0.0584 | 0.2315 | 1,786,791 |
| medium_text | 942 | 0.5225 | 0.3725 | 0.6803 | 1,802,741 |
| large_text | 3,598 | 1.5751 | 1.2603 | 0.9373 | 2,284,301 |

### clean_script

#### Latn Script

| Configuration | Length | Mean (ms) | Median (ms) | Std Dev (ms) | Chars/sec |
|---------------|--------|-----------|-------------|--------------|-----------|
| default | 884 | 13.3366 | 12.2135 | 5.5406 | 66,284 |
| with_numbers | 884 | 16.3172 | 11.4699 | 22.1379 | 54,176 |
| with_punctuation | 884 | 17.7299 | 14.5166 | 9.6117 | 49,859 |
| full_config | 884 | 23.1436 | 15.1101 | 21.6586 | 38,196 |

#### Arab Script

| Configuration | Length | Mean (ms) | Median (ms) | Std Dev (ms) | Chars/sec |
|---------------|--------|-----------|-------------|--------------|-----------|
| default | 634 | 14.5561 | 12.2881 | 7.0182 | 43,556 |
| with_numbers | 634 | 11.2724 | 8.9115 | 6.3879 | 56,244 |
| with_punctuation | 634 | 9.3601 | 6.2504 | 8.4882 | 67,734 |
| full_config | 634 | 18.5497 | 9.7687 | 27.6778 | 34,178 |

#### Hans Script

| Configuration | Length | Mean (ms) | Median (ms) | Std Dev (ms) | Chars/sec |
|---------------|--------|-----------|-------------|--------------|-----------|
| default | 279 | 3.1906 | 2.8035 | 1.6422 | 87,445 |
| with_numbers | 279 | 2.3722 | 2.3631 | 0.2210 | 117,611 |
| with_punctuation | 279 | 3.2327 | 3.2513 | 0.5697 | 86,306 |
| full_config | 279 | 6.1894 | 4.8720 | 3.3209 | 45,077 |

#### Cyrl Script

| Configuration | Length | Mean (ms) | Median (ms) | Std Dev (ms) | Chars/sec |
|---------------|--------|-----------|-------------|--------------|-----------|
| default | 719 | 13.6691 | 12.7917 | 3.4601 | 52,600 |
| with_numbers | 719 | 12.7077 | 11.4621 | 5.9363 | 56,580 |
| with_punctuation | 719 | 11.1091 | 10.8068 | 3.2846 | 64,721 |
| full_config | 719 | 16.0494 | 13.3319 | 10.4541 | 44,799 |

#### Deva Script

| Configuration | Length | Mean (ms) | Median (ms) | Std Dev (ms) | Chars/sec |
|---------------|--------|-----------|-------------|--------------|-----------|
| default | 504 | 9.2714 | 8.7233 | 5.3851 | 54,361 |
| with_numbers | 504 | 4.9410 | 4.9937 | 0.4762 | 102,003 |
| with_punctuation | 504 | 8.5852 | 7.6304 | 4.0800 | 58,706 |
| full_config | 504 | 6.9293 | 6.3930 | 1.8693 | 72,734 |

### unscript

#### Latn Script

| Configuration | Length | Mean (ms) | Median (ms) | Std Dev (ms) | Chars/sec |
|---------------|--------|-----------|-------------|--------------|-----------|
| default | 935 | 15.5203 | 12.6880 | 7.7668 | 60,244 |
| with_numbers | 935 | 14.7634 | 14.6632 | 4.5096 | 63,332 |
| preserve_case | 935 | 28.0643 | 13.0770 | 56.0021 | 33,316 |

#### Arab Script

| Configuration | Length | Mean (ms) | Median (ms) | Std Dev (ms) | Chars/sec |
|---------------|--------|-----------|-------------|--------------|-----------|
| default | 672 | 11.6921 | 9.8610 | 7.2873 | 57,474 |
| with_numbers | 672 | 7.1452 | 5.7600 | 2.1157 | 94,049 |
| preserve_case | 672 | 7.8695 | 7.6177 | 1.6338 | 85,393 |

#### Hans Script

| Configuration | Length | Mean (ms) | Median (ms) | Std Dev (ms) | Chars/sec |
|---------------|--------|-----------|-------------|--------------|-----------|
| default | 279 | 5.9195 | 5.3907 | 2.5328 | 47,132 |
| with_numbers | 279 | 6.8384 | 6.6916 | 2.4290 | 40,799 |
| preserve_case | 279 | 2.9498 | 2.6381 | 0.7017 | 94,582 |

### detect_script

#### Mono-script Detection

| Script | Mode | Length | Mean (ms) | Median (ms) | Std Dev (ms) | Chars/sec |
|--------|------|--------|-----------|-------------|--------------|-----------|
| Latn | basic | 530 | 1.2187 | 1.1890 | 0.1142 | 434,904 |
| Latn | with_categories | 530 | 5.1477 | 2.5411 | 13.0707 | 102,958 |
| Latn | with_threshold | 530 | 5.8995 | 2.7788 | 8.6349 | 89,838 |
| Arab | basic | 380 | 1.5604 | 1.5090 | 0.1541 | 243,522 |
| Arab | with_categories | 380 | 2.2202 | 2.2157 | 0.0528 | 171,158 |
| Arab | with_threshold | 380 | 1.9693 | 1.5737 | 1.2340 | 192,958 |
| Hans | basic | 167 | 2.4658 | 1.2998 | 5.3369 | 67,726 |
| Hans | with_categories | 167 | 1.5931 | 0.9612 | 1.8647 | 104,828 |
| Hans | with_threshold | 167 | 1.2253 | 0.8474 | 1.0037 | 136,290 |
| Cyrl | basic | 431 | 4.6603 | 3.6304 | 2.6165 | 92,484 |
| Cyrl | with_categories | 431 | 6.5894 | 4.6411 | 6.4183 | 65,408 |
| Cyrl | with_threshold | 431 | 5.4898 | 4.2704 | 4.0920 | 78,510 |
| Deva | basic | 302 | 6.2613 | 5.0174 | 5.0979 | 48,233 |
| Deva | with_categories | 302 | 3.7785 | 3.3323 | 1.0083 | 79,926 |
| Deva | with_threshold | 302 | 2.4267 | 2.4190 | 0.0591 | 124,446 |
| Jpan | basic | 209 | 1.0111 | 0.9975 | 0.0328 | 206,710 |
| Jpan | with_categories | 209 | 1.2945 | 1.0929 | 0.6557 | 161,448 |
| Jpan | with_threshold | 209 | 2.0083 | 1.3084 | 1.8643 | 104,068 |
| Hang | basic | 251 | 2.6400 | 2.0927 | 1.2630 | 95,075 |
| Hang | with_categories | 251 | 3.7753 | 3.1513 | 1.6834 | 66,484 |
| Hang | with_threshold | 251 | 2.9931 | 2.0603 | 2.6676 | 83,861 |

#### Mixed-script Detection

| Scenario | Length | Mean (ms) | Median (ms) | Std Dev (ms) | Chars/sec |
|----------|--------|-----------|-------------|--------------|-----------|
| latin_arabic | 607 | 6.0495 | 4.0005 | 5.8908 | 100,338 |
| latin_chinese | 465 | 3.9106 | 2.4374 | 2.7779 | 118,909 |
| multi_script | 1,007 | 4.5243 | 4.2119 | 0.6146 | 222,578 |

### in_range

| Test Case | Mean (ms) | Median (ms) | Std Dev (ms) | Calls/sec |
|-----------|-----------|-------------|--------------|-----------|
| single_range_latin | 0.0004 | 0.0004 | 0.0001 | 2,391,290 |
| single_range_arabic | 0.0004 | 0.0004 | 0.0003 | 2,250,645 |
| single_range_number | 0.0004 | 0.0004 | 0.0003 | 2,305,710 |
| multi_range_2 | 0.0004 | 0.0004 | 0.0002 | 2,316,268 |
| multi_range_4 | 0.0037 | 0.0036 | 0.0010 | 271,500 |
| category_check | 0.0005 | 0.0005 | 0.0001 | 1,959,079 |
| text_processing | 1.3227 | 1.3077 | 0.0478 | 458,907 |

## Benchmark Notes

- All timings are averaged over multiple iterations
- Measurements were taken using `time.perf_counter()` for high precision
- Text samples include realistic multilingual content with various character types
- Standard deviation indicates timing consistency (lower is better)
- Characters per second indicates throughput performance
