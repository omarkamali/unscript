#!/usr/bin/env python3
"""
Quick performance testing utility for unscript development.

This script provides fast performance checks for individual functions
without the full benchmark suite.
"""

import time
import sys
import os

# Add src to path so we can import unscript
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from unscript import unscript, clean_script, clean_text, detect_script, ranges, in_range


def quick_test(func, *args, iterations=1000):
    """Quick timing test for a function."""
    start_time = time.perf_counter()
    for _ in range(iterations):
        func(*args)
    end_time = time.perf_counter()

    total_time = end_time - start_time
    avg_time = total_time / iterations

    return {
        "total_time": total_time,
        "avg_time_ms": avg_time * 1000,
        "ops_per_second": 1 / avg_time,
        "iterations": iterations,
    }


def test_all_functions():
    """Test all main functions with sample data."""
    print("Quick Performance Test")
    print("=" * 30)

    # Sample texts
    sample_texts = {
        "latin": "Hello world! This is a test with @user #hashtag https://example.com 😊",
        "arabic": "مرحبا بالعالم! هذا اختبار مع @مستخدم #وسم https://example.com 😊",
        "mixed": "Hello مرحبا 你好 world! Test 123 @user #tag https://example.com",
    }

    print("\n1. clean_text performance:")
    for name, text in sample_texts.items():
        result = quick_test(clean_text, text)
        print(
            f"   {name}: {result['avg_time_ms']:.3f}ms avg, {result['ops_per_second']:,.0f} ops/sec"
        )

    print("\n2. clean_script performance:")
    scripts_to_test = ["Latn", "Arab", "Hans"]
    for script in scripts_to_test:
        text = sample_texts["mixed"]
        result = quick_test(clean_script, script, text)
        print(
            f"   {script}: {result['avg_time_ms']:.3f}ms avg, {result['ops_per_second']:,.0f} ops/sec"
        )

    print("\n3. unscript performance:")
    for script in scripts_to_test:
        text = sample_texts["mixed"]
        result = quick_test(unscript, script, text)
        print(
            f"   {script}: {result['avg_time_ms']:.3f}ms avg, {result['ops_per_second']:,.0f} ops/sec"
        )

    print("\n4. detect_script performance:")
    for name, text in sample_texts.items():
        result = quick_test(detect_script, text)
        print(
            f"   {name}: {result['avg_time_ms']:.3f}ms avg, {result['ops_per_second']:,.0f} ops/sec"
        )

    print("\n5. in_range performance:")
    test_cases = [
        ("Latin char", "A", [ranges.Latn]),
        ("Arabic char", "ا", [ranges.Arab]),
        ("Number", "5", [ranges.numbers]),
        ("Multi-range", "A", [ranges.Latn, ranges.Arab, ranges.numbers]),
    ]

    for name, char, range_args in test_cases:
        # Use more iterations for in_range since it's very fast
        result = quick_test(in_range, char, *range_args, iterations=10000)
        print(
            f"   {name}: {result['avg_time_ms']:.4f}ms avg, {result['ops_per_second']:,.0f} ops/sec"
        )


def test_specific_function(func_name):
    """Test a specific function."""
    test_text = "Hello مرحبا 你好 world! Test 123 @user #tag https://example.com"

    if func_name == "clean_text":
        result = quick_test(clean_text, test_text)
        print(
            f"clean_text: {result['avg_time_ms']:.3f}ms avg, {result['ops_per_second']:,.0f} ops/sec"
        )

    elif func_name == "clean_script":
        for script in ["Latn", "Arab", "Hans"]:
            result = quick_test(clean_script, script, test_text)
            print(
                f"clean_script({script}): {result['avg_time_ms']:.3f}ms avg, {result['ops_per_second']:,.0f} ops/sec"
            )

    elif func_name == "unscript":
        for script in ["Latn", "Arab", "Hans"]:
            result = quick_test(unscript, script, test_text)
            print(
                f"unscript({script}): {result['avg_time_ms']:.3f}ms avg, {result['ops_per_second']:,.0f} ops/sec"
            )

    elif func_name == "detect_script":
        result = quick_test(detect_script, test_text)
        print(
            f"detect_script: {result['avg_time_ms']:.3f}ms avg, {result['ops_per_second']:,.0f} ops/sec"
        )

    elif func_name == "in_range":
        test_cases = [
            ("A", [ranges.Latn]),
            ("ا", [ranges.Arab]),
            ("5", [ranges.numbers]),
            ("!", [ranges.punctuation]),
        ]
        for char, range_args in test_cases:
            result = quick_test(in_range, char, *range_args, iterations=10000)
            print(
                f"in_range('{char}'): {result['avg_time_ms']:.4f}ms avg, {result['ops_per_second']:,.0f} ops/sec"
            )

    else:
        print(f"Unknown function: {func_name}")
        print(
            "Available functions: clean_text, clean_script, unscript, detect_script, in_range"
        )


def main():
    """Main function."""
    if len(sys.argv) > 1:
        func_name = sys.argv[1]
        test_specific_function(func_name)
    else:
        test_all_functions()


if __name__ == "__main__":
    main()
