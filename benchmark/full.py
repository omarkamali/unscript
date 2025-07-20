#!/usr/bin/env python3
"""
Performance benchmarking script for unscript package.

This script benchmarks all core functions with various script scenarios
and generates a comprehensive performance report in performance.md.
"""

import time
import statistics
import random
import string
import datetime
from pathlib import Path
import sys
import os

# Add src to path so we can import unscript
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from unscript import unscript, clean_script, clean_text, detect_script, ranges, in_range


def get_version():
    """Get the current version of unscript."""
    try:
        # Try to read from pyproject.toml
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        if pyproject_path.exists():
            with open(pyproject_path, "r") as f:
                for line in f:
                    if line.strip().startswith("version = "):
                        return line.split("=")[1].strip().strip('"').strip("'")
        return "unknown"
    except Exception:
        return "unknown"


class TestDataGenerator:
    """Generate test data for different script scenarios."""

    # Sample texts for different scripts
    SCRIPT_SAMPLES = {
        "Latn": "Hello world! This is a sample text in Latin script. It contains various characters, numbers 123, and punctuation marks. Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        "Arab": "مرحبا بالعالم! هذا نص تجريبي باللغة العربية. يحتوي على أرقام ۱۲۳ وعلامات ترقيم مختلفة. النص العربي يُكتب من اليمين إلى اليسار.",
        "Hans": "你好世界！这是一个中文简体的示例文本。包含各种字符、数字123和标点符号。中文是世界上使用人数最多的语言之一。",
        "Hant": "你好世界！這是一個繁體中文的示例文本。包含各種字符、數字123和標點符號。繁體中文在台灣和香港被廣泛使用。",
        "Jpan": "こんにちは世界！これは日本語のサンプルテキストです。ひらがな、カタカナ、漢字、数字123、句読点が含まれています。日本語は美しい言語です。",
        "Hang": "안녕하세요 세계! 이것은 한국어 샘플 텍스트입니다. 한글, 숫자 123, 구두점이 포함되어 있습니다. 한국어는 과학적인 문자 체계를 가지고 있습니다.",
        "Cyrl": "Привет мир! Это образец текста на кириллице. Содержит различные символы, числа 123 и знаки препинания. Кириллица используется во многих языках.",
        "Grek": "Γεια σας κόσμε! Αυτό είναι ένα δείγμα κειμένου στα ελληνικά. Περιέχει διάφορους χαρακτήρες, αριθμούς 123 και σημεία στίξης.",
        "Hebr": "שלום עולם! זהו טקסט לדוגמה בעברית. הוא מכיל תווים שונים, מספרים 123 וסימני פיסוק. העברית נכתבת מימין לשמאל.",
        "Deva": "नमस्ते संसार! यह देवनागरी में एक नमूना पाठ है। इसमें विभिन्न अक्षर, संख्याएं १२३ और विराम चिह्न हैं।",
        "Beng": "হ্যালো বিশ্ব! এটি বাংলা লিপিতে একটি নমুনা পাঠ। এতে বিভিন্ন অক্ষর, সংখ্যা ১২৩ এবং যতিচিহ্ন রয়েছে।",
        "Gujr": "નમસ્તે વિશ્વ! આ ગુજરાતી લિપિમાં એક નમૂનો પાઠ છે। તેમાં વિવિધ અક્ષરો, સંખ્યાઓ ૧૨૩ અને વિરામચિહ્નો છે।",
        "Guru": "ਸਤ ਸ੍ਰੀ ਅਕਾਲ ਸੰਸਾਰ! ਇਹ ਗੁਰਮੁਖੀ ਵਿੱਚ ਇੱਕ ਨਮੂਨਾ ਪਾਠ ਹੈ। ਇਸ ਵਿੱਚ ਵੱਖ-ਵੱਖ ਅੱਖਰ, ਸੰਖਿਆਵਾਂ ੧੨੩ ਅਤੇ ਵਿਰਾਮ ਚਿੰਨ੍ਹ ਹਨ।",
    }

    def __init__(self):
        self.available_scripts = list(self.SCRIPT_SAMPLES.keys())

    def generate_mono_script_text(self, script, length_multiplier=1):
        """Generate text for a single script."""
        base_text = self.SCRIPT_SAMPLES.get(script, self.SCRIPT_SAMPLES["Latn"])
        # Repeat the text to reach desired length
        repeated_text = (base_text + " ") * length_multiplier
        return repeated_text.strip()

    def generate_mixed_script_text(self, scripts, length_multiplier=1):
        """Generate mixed script text."""
        if not scripts:
            scripts = ["Latn", "Arab", "Hans"]

        mixed_parts = []
        for script in scripts:
            text = self.generate_mono_script_text(script, length_multiplier)
            mixed_parts.append(text)

        # Randomly interleave the scripts
        random.shuffle(mixed_parts)
        return " ".join(mixed_parts)

    def generate_text_with_noise(self, base_text):
        """Add URLs, mentions, hashtags, and emojis to text."""
        noise_elements = [
            "@user123",
            "#hashtag",
            "https://example.com",
            "http://test.org",
            "😊",
            "🌍",
            "💡",
            "@mention",
            "#tag",
            "www.example.com",
            "user@email.com",
        ]

        words = base_text.split()
        # Insert noise elements randomly
        for _ in range(min(5, len(words) // 10)):
            insert_pos = random.randint(0, len(words))
            words.insert(insert_pos, random.choice(noise_elements))

        return " ".join(words)


class PerformanceBenchmark:
    """Main benchmarking class."""

    def __init__(self):
        self.data_generator = TestDataGenerator()
        self.results = {}

    def time_function(self, func, *args, iterations=100):
        """Time a function with multiple iterations for accuracy."""
        times = []
        for _ in range(iterations):
            start_time = time.perf_counter()
            func(*args)
            end_time = time.perf_counter()
            times.append(end_time - start_time)

        return {
            "mean": statistics.mean(times),
            "median": statistics.median(times),
            "min": min(times),
            "max": max(times),
            "std_dev": statistics.stdev(times) if len(times) > 1 else 0,
            "iterations": iterations,
        }

    def benchmark_clean_text(self):
        """Benchmark clean_text function."""
        print("Benchmarking clean_text...")
        results = {}

        # Test different text sizes
        for size_name, multiplier in [("small", 1), ("medium", 5), ("large", 20)]:
            test_text = self.data_generator.generate_mono_script_text(
                "Latn", multiplier
            )
            test_text = self.data_generator.generate_text_with_noise(test_text)

            timing = self.time_function(clean_text, test_text)
            results[f"{size_name}_text"] = {
                "timing": timing,
                "text_length": len(test_text),
                "chars_per_second": len(test_text) / timing["mean"],
            }

        return results

    def benchmark_clean_script(self):
        """Benchmark clean_script function."""
        print("Benchmarking clean_script...")
        results = {}

        # Test with different scripts
        test_scripts = ["Latn", "Arab", "Hans", "Cyrl", "Deva"]

        for script in test_scripts:
            test_text = self.data_generator.generate_mono_script_text(script, 5)

            # Test with different configurations
            configs = [
                ("default", {}),
                ("with_numbers", {"numbers": True}),
                ("with_punctuation", {"punctuation": True}),
                (
                    "full_config",
                    {"numbers": True, "punctuation": True, "symbols": True},
                ),
            ]

            script_results = {}
            for config_name, config in configs:
                timing = self.time_function(clean_script, script, test_text, config)
                script_results[config_name] = {
                    "timing": timing,
                    "text_length": len(test_text),
                    "chars_per_second": len(test_text) / timing["mean"],
                }

            results[script] = script_results

        return results

    def benchmark_unscript(self):
        """Benchmark unscript function."""
        print("Benchmarking unscript...")
        results = {}

        # Test with different scripts and scenarios
        test_scripts = ["Latn", "Arab", "Hans"]

        for script in test_scripts:
            test_text = self.data_generator.generate_mono_script_text(script, 5)
            test_text = self.data_generator.generate_text_with_noise(test_text)

            # Test different configurations
            configs = [
                ("default", {}),
                ("with_numbers", {"numbers": True}),
                ("preserve_case", {}, False),  # lowercase=False
            ]

            script_results = {}
            for config_name, config, *extra_args in configs:
                lowercase = extra_args[0] if extra_args else True
                timing = self.time_function(
                    unscript, script, test_text, config, lowercase
                )
                script_results[config_name] = {
                    "timing": timing,
                    "text_length": len(test_text),
                    "chars_per_second": len(test_text) / timing["mean"],
                }

            results[script] = script_results

        return results

    def benchmark_detect_script(self):
        """Benchmark detect_script function."""
        print("Benchmarking detect_script...")
        results = {}

        # Test mono-script scenarios
        mono_results = {}
        test_scripts = ["Latn", "Arab", "Hans", "Cyrl", "Deva", "Jpan", "Hang"]

        for script in test_scripts:
            test_text = self.data_generator.generate_mono_script_text(script, 3)

            # Test different detection modes
            modes = [
                ("basic", [test_text]),
                ("with_categories", [test_text, True]),  # include_categories=True
                ("with_threshold", [test_text, False, 5.0]),  # min_threshold=5.0
            ]

            script_results = {}
            for mode_name, args in modes:
                timing = self.time_function(detect_script, *args)
                script_results[mode_name] = {
                    "timing": timing,
                    "text_length": len(test_text),
                    "chars_per_second": len(test_text) / timing["mean"],
                }

            mono_results[script] = script_results

        results["mono_script"] = mono_results

        # Test mixed-script scenarios
        mixed_results = {}
        mixed_scenarios = [
            ("latin_arabic", ["Latn", "Arab"]),
            ("latin_chinese", ["Latn", "Hans"]),
            ("multi_script", ["Latn", "Arab", "Hans", "Cyrl"]),
        ]

        for scenario_name, scripts in mixed_scenarios:
            test_text = self.data_generator.generate_mixed_script_text(scripts, 2)
            timing = self.time_function(detect_script, test_text)
            mixed_results[scenario_name] = {
                "timing": timing,
                "text_length": len(test_text),
                "chars_per_second": len(test_text) / timing["mean"],
            }

        results["mixed_script"] = mixed_results

        return results

    def benchmark_in_range(self):
        """Benchmark in_range function."""
        print("Benchmarking in_range...")
        results = {}

        # Test different character types and range combinations
        test_cases = [
            ("single_range_latin", "A", [ranges.Latn]),
            ("single_range_arabic", "ا", [ranges.Arab]),
            ("single_range_number", "5", [ranges.numbers]),
            ("multi_range_2", "A", [ranges.Latn, ranges.Arab]),
            (
                "multi_range_4",
                "!",
                [ranges.Latn, ranges.Arab, ranges.numbers, ranges.punctuation],
            ),
            ("category_check", "5", [ranges.numbers, ranges.punctuation]),
        ]

        for case_name, char, range_args in test_cases:
            # Use more iterations for in_range since it's very fast
            timing = self.time_function(in_range, char, *range_args, iterations=10000)
            results[case_name] = {
                "timing": timing,
                "calls_per_second": 1 / timing["mean"],
                "ranges_checked": len(range_args),
            }

        # Test performance with long text processing
        test_text = self.data_generator.generate_mixed_script_text(["Latn", "Arab"], 2)

        def process_text_with_in_range():
            count = 0
            for char in test_text:
                if in_range(char, ranges.Latn, ranges.Arab):
                    count += 1
            return count

        timing = self.time_function(process_text_with_in_range, iterations=50)
        results["text_processing"] = {
            "timing": timing,
            "text_length": len(test_text),
            "chars_per_second": len(test_text) / timing["mean"],
        }

        return results

    def run_all_benchmarks(self):
        """Run all benchmarks and collect results."""
        print("Starting comprehensive performance benchmarks...")
        print(f"Testing unscript version: {get_version()}")
        print(f"Benchmark started at: {datetime.datetime.now()}")
        print()

        self.results = {
            "metadata": {
                "version": get_version(),
                "timestamp": datetime.datetime.now().isoformat(),
                "python_version": sys.version,
            },
            "clean_text": self.benchmark_clean_text(),
            "clean_script": self.benchmark_clean_script(),
            "unscript": self.benchmark_unscript(),
            "detect_script": self.benchmark_detect_script(),
            "in_range": self.benchmark_in_range(),
        }

        print("All benchmarks completed!")
        return self.results


class ReportGenerator:
    """Generate performance reports in markdown format."""

    def __init__(self, results):
        self.results = results

    def format_timing(self, timing_data):
        """Format timing data into readable strings."""
        mean_ms = timing_data["mean"] * 1000
        median_ms = timing_data["median"] * 1000
        std_ms = timing_data["std_dev"] * 1000

        return {
            "mean_ms": f"{mean_ms:.4f}",
            "median_ms": f"{median_ms:.4f}",
            "std_ms": f"{std_ms:.4f}",
            "iterations": timing_data["iterations"],
        }

    def generate_report(self):
        """Generate the full performance report."""
        metadata = self.results["metadata"]

        report = []
        report.append(f"# Performance Report - Version {metadata['version']}")
        report.append("")
        report.append(f"**Generated:** {metadata['timestamp']}")
        report.append(f"**Python Version:** {metadata['python_version']}")
        report.append("")
        report.append("## Summary")
        report.append("")

        # Generate summary table
        self._add_summary_table(report)

        report.append("")
        report.append("## Detailed Results")
        report.append("")

        # Add detailed sections for each function
        self._add_clean_text_section(report)
        self._add_clean_script_section(report)
        self._add_unscript_section(report)
        self._add_detect_script_section(report)
        self._add_in_range_section(report)

        # Add benchmark notes
        report.append("")
        report.append("## Benchmark Notes")
        report.append("")
        report.append("- All timings are averaged over multiple iterations")
        report.append(
            "- Measurements were taken using `time.perf_counter()` for high precision"
        )
        report.append(
            "- Text samples include realistic multilingual content with various character types"
        )
        report.append(
            "- Standard deviation indicates timing consistency (lower is better)"
        )
        report.append("- Characters per second indicates throughput performance")
        report.append("")

        return "\n".join(report)

    def _add_summary_table(self, report):
        """Add performance summary table."""
        report.append("| Function | Best Performance | Typical Use Case | Notes |")
        report.append("|----------|------------------|------------------|--------|")

        # Extract key metrics for summary
        clean_text_perf = self.results["clean_text"]["medium_text"]["chars_per_second"]

        # Get a representative clean_script performance
        clean_script_perf = self.results["clean_script"]["Latn"]["default"][
            "chars_per_second"
        ]

        # Get a representative unscript performance
        unscript_perf = self.results["unscript"]["Latn"]["default"]["chars_per_second"]

        # Get a representative detect_script performance
        detect_script_perf = self.results["detect_script"]["mono_script"]["Latn"][
            "basic"
        ]["chars_per_second"]

        # Get in_range performance
        in_range_perf = self.results["in_range"]["single_range_latin"][
            "calls_per_second"
        ]

        report.append(
            f"| `clean_text` | {clean_text_perf:,.0f} chars/sec | General text cleaning | Handles URLs, mentions, emojis |"
        )
        report.append(
            f"| `clean_script` | {clean_script_perf:,.0f} chars/sec | Script-specific filtering | Performance varies by script |"
        )
        report.append(
            f"| `unscript` | {unscript_perf:,.0f} chars/sec | Complete text processing | Combines cleaning + filtering |"
        )
        report.append(
            f"| `detect_script` | {detect_script_perf:,.0f} chars/sec | Script detection | Slower for mixed scripts |"
        )
        report.append(
            f"| `in_range` | {in_range_perf:,.0f} calls/sec | Character checking | Very fast single-char ops |"
        )

    def _add_clean_text_section(self, report):
        """Add clean_text benchmark section."""
        report.append("### clean_text")
        report.append("")
        report.append(
            "| Text Size | Length | Mean (ms) | Median (ms) | Std Dev (ms) | Chars/sec |"
        )
        report.append(
            "|-----------|--------|-----------|-------------|--------------|-----------|"
        )

        for size_name, data in self.results["clean_text"].items():
            timing = self.format_timing(data["timing"])
            report.append(
                f"| {size_name} | {data['text_length']:,} | {timing['mean_ms']} | {timing['median_ms']} | {timing['std_ms']} | {data['chars_per_second']:,.0f} |"
            )

    def _add_clean_script_section(self, report):
        """Add clean_script benchmark section."""
        report.append("")
        report.append("### clean_script")
        report.append("")

        for script, script_data in self.results["clean_script"].items():
            report.append(f"#### {script} Script")
            report.append("")
            report.append(
                "| Configuration | Length | Mean (ms) | Median (ms) | Std Dev (ms) | Chars/sec |"
            )
            report.append(
                "|---------------|--------|-----------|-------------|--------------|-----------|"
            )

            for config_name, data in script_data.items():
                timing = self.format_timing(data["timing"])
                report.append(
                    f"| {config_name} | {data['text_length']:,} | {timing['mean_ms']} | {timing['median_ms']} | {timing['std_ms']} | {data['chars_per_second']:,.0f} |"
                )
            report.append("")

    def _add_unscript_section(self, report):
        """Add unscript benchmark section."""
        report.append("### unscript")
        report.append("")

        for script, script_data in self.results["unscript"].items():
            report.append(f"#### {script} Script")
            report.append("")
            report.append(
                "| Configuration | Length | Mean (ms) | Median (ms) | Std Dev (ms) | Chars/sec |"
            )
            report.append(
                "|---------------|--------|-----------|-------------|--------------|-----------|"
            )

            for config_name, data in script_data.items():
                timing = self.format_timing(data["timing"])
                report.append(
                    f"| {config_name} | {data['text_length']:,} | {timing['mean_ms']} | {timing['median_ms']} | {timing['std_ms']} | {data['chars_per_second']:,.0f} |"
                )
            report.append("")

    def _add_detect_script_section(self, report):
        """Add detect_script benchmark section."""
        report.append("### detect_script")
        report.append("")

        # Mono-script results
        report.append("#### Mono-script Detection")
        report.append("")
        report.append(
            "| Script | Mode | Length | Mean (ms) | Median (ms) | Std Dev (ms) | Chars/sec |"
        )
        report.append(
            "|--------|------|--------|-----------|-------------|--------------|-----------|"
        )

        for script, script_data in self.results["detect_script"]["mono_script"].items():
            for mode_name, data in script_data.items():
                timing = self.format_timing(data["timing"])
                report.append(
                    f"| {script} | {mode_name} | {data['text_length']:,} | {timing['mean_ms']} | {timing['median_ms']} | {timing['std_ms']} | {data['chars_per_second']:,.0f} |"
                )

        report.append("")

        # Mixed-script results
        report.append("#### Mixed-script Detection")
        report.append("")
        report.append(
            "| Scenario | Length | Mean (ms) | Median (ms) | Std Dev (ms) | Chars/sec |"
        )
        report.append(
            "|----------|--------|-----------|-------------|--------------|-----------|"
        )

        for scenario_name, data in self.results["detect_script"][
            "mixed_script"
        ].items():
            timing = self.format_timing(data["timing"])
            report.append(
                f"| {scenario_name} | {data['text_length']:,} | {timing['mean_ms']} | {timing['median_ms']} | {timing['std_ms']} | {data['chars_per_second']:,.0f} |"
            )

        report.append("")

    def _add_in_range_section(self, report):
        """Add in_range benchmark section."""
        report.append("### in_range")
        report.append("")
        report.append(
            "| Test Case | Mean (ms) | Median (ms) | Std Dev (ms) | Calls/sec |"
        )
        report.append(
            "|-----------|-----------|-------------|--------------|-----------|"
        )

        for case_name, data in self.results["in_range"].items():
            timing = self.format_timing(data["timing"])
            if "calls_per_second" in data:
                calls_per_sec = f"{data['calls_per_second']:,.0f}"
            else:
                calls_per_sec = f"{data['chars_per_second']:,.0f}"

            report.append(
                f"| {case_name} | {timing['mean_ms']} | {timing['median_ms']} | {timing['std_ms']} | {calls_per_sec} |"
            )


def update_performance_md(new_report):
    """Update performance.md with the new report, keeping historical data."""
    performance_file = Path("performance.md")

    # Read existing content if file exists
    existing_content = ""
    if performance_file.exists():
        with open(performance_file, "r", encoding="utf-8") as f:
            existing_content = f.read()

    # Prepare the new content
    separator = "\n\n---\n\n"

    if existing_content:
        # Prepend new report to existing content
        new_content = new_report + separator + existing_content
    else:
        new_content = new_report

    # Write the updated content
    with open(performance_file, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"Performance report updated in {performance_file}")


def main():
    """Main function to run benchmarks and generate report."""
    print("Unscript Performance Benchmarking")
    print("=" * 40)
    print()

    # Run benchmarks
    benchmark = PerformanceBenchmark()
    results = benchmark.run_all_benchmarks()

    # Generate report
    print("\nGenerating performance report...")
    report_generator = ReportGenerator(results)
    report = report_generator.generate_report()

    # Update performance.md
    update_performance_md(report)

    print("\nBenchmarking completed successfully!")
    print("Results saved to performance.md")


if __name__ == "__main__":
    main()
