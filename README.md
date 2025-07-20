# Unscript: Multilingual Text Cleaning

[![Unscript Tests](https://github.com/omarkamali/unscript/actions/workflows/pytest.yml/badge.svg)](https://github.com/omarkamali/unscript/actions/workflows/pytest.yml)

Unscript is a Python package designed for robust and flexible text cleaning, particularly for multilingual data. It provides functions to sanitize text by removing unwanted elements like mentions, hashtags, URLs, and emojis, to filter text based on specific Unicode script ranges, and to detect and analyze the script composition of text.

## Installation

To install Unscript, you can use `pip`:

```bash
pip install unscript
```

## Quick Start

```python
from unscript import unscript, clean_text, clean_script, detect_script, ranges, in_range

# Most common use case: complete text cleaning for a specific script
text = "Hello @user! Check https://example.com 😊 مرحبا $123.45"
result = unscript("Latn", text, {"numbers": True, "symbols": True})
print(result)  # Output: "hello check $123.45"

# For general cleaning without script filtering
clean_result = clean_text(text)
print(clean_result)  # Output: "hello ! check مرحبا $123.45"

# For script filtering only (keeps original case, URLs, mentions)
script_result = clean_script("Latn", text, {"numbers": True, "symbols": True})
print(script_result)  # Output: "Hello @user Check https //example com 😊 $123.45"

# For detecting script composition
detect_result = detect_script(text)
print(detect_result)  # Output: {'Latn': 71.43, 'Arab': 28.57}

# For checking individual characters against Unicode ranges
print(in_range('ا', ranges.Arab))    # True - Arabic character
print(in_range('A', ranges.Latn))    # True - Latin character
print(in_range('5', ranges.numbers)) # True - Digit character

# Check multiple ranges (OR logic)
print(in_range('5', ranges.Arab, ranges.numbers))  # True - character is a number
```

## Functions

### Text Cleaning Functions

### `unscript(script: str, text: str, config: dict = None, lowercase: bool = True) -> str`

This is the **primary function** that combines script filtering with general text cleaning in an optimal pipeline. It first applies `clean_text` to remove mentions, URLs, and emojis, then applies `clean_script` to filter by the specified Unicode script.

**Arguments:**
-   `script` (`str`): The Unicode script code (e.g., `'Latn'`, `'Arab'`, `'Hans'`).
-   `text` (`str`): The text string to be cleaned.
-   `config` (`dict`, optional): Configuration for script filtering. Defaults to `{'spaces': True, 'numbers': False, 'punctuation': False, 'symbols': False}`.
-   `lowercase` (`bool`, optional): Whether to convert text to lowercase. Defaults to `True`.

**Returns:**
-   `str`: Cleaned text containing only characters from the specified script, with mentions, URLs, and other noise removed.

**Example Usage:**

```python
from unscript import unscript

# Basic usage with Latin script
text1 = "Hello @user! Check https://example.com 😊 مرحبا"
result1 = unscript("Latn", text1)
print(result1)
# Expected output: "hello check"

# Arabic script with punctuation
text2 = "مرحبا @user بالعالم! https://example.com"
result2 = unscript("Arab", text2, {"punctuation": True})
print(result2)
# Expected output: "مرحبا بالعالم!"

# Latin script with numbers and symbols
text3 = "Price: $123.45 @user!"
result3 = unscript("Latn", text3, {"numbers": True, "symbols": True})
print(result3)
# Expected output: "price $123.45"

# Preserve case
text4 = "HELLO @user WORLD!"
result4 = unscript("Latn", text4, lowercase=False)
print(result4)
# Expected output: "HELLO WORLD"
```

### `clean_text(text: str, lowercase: bool = True) -> str`

This function provides a general-purpose text cleaning utility. It's designed to prepare raw text for analysis by removing common noisy elements like mentions, URLs, and emojis. **Note**: For script-specific filtering (removing punctuation, symbols, etc.), use `clean_script` or the `unscript` function.

**Features:**
-   Removes `@mentions`, `@@mentions`, and `+mentions`.
-   Removes `#hashtags`.
-   Removes URLs (e.g., `http://`, `https://`, `ftp://`, `www.`, and email addresses).
-   Removes domain names (e.g., `example.com`) but preserves decimal numbers (e.g., `123.45`).
-   Removes emojis.
-   Normalizes Unicode characters.
-   Converts text to lowercase (optional with `lowercase` parameter).
-   Collapses repeating characters to a maximum of two characters (e.g., "coooooolllll" becomes "cooll"), except for numbers.
-   Replaces newlines and tabs with spaces.
-   Collapses multiple spaces into single spaces.
-   Returns an empty string if the cleaned text consists only of numbers.

**Example Usage:**

```python
from unscript import clean_text

text1 = "Hello world! This is a test @user #python https://example.com 😊 coooooolllll"
cleaned_text1 = clean_text(text1)
print(cleaned_text1)
# Expected output: "hello world! this is a test cooll"

text2 = "Price is $123.45 @user"
cleaned_text2 = clean_text(text2)
print(cleaned_text2)
# Expected output: "price is $123.45"

# Preserve case
text3 = "Hello WORLD @user"
cleaned_text3 = clean_text(text3, lowercase=False)
print(cleaned_text3)
# Expected output: "Hello WORLD"
```

### `clean_script(script: str, text: str, config: dict = None) -> str`

This function filters text to include only characters belonging to a specified Unicode script, with configurable options for numbers, punctuation, and symbols. It's ideal for tasks requiring strict script adherence.

**Arguments:**
-   `script` (`str`): The Unicode script code (e.g., `'Latn'`, `'Arab'`, `'Hans'`).
-   `text` (`str`): The text string to be cleaned.
-   `config` (`dict`, optional): A dictionary to customize character inclusion. Defaults to `{'spaces': True, 'numbers': False, 'punctuation': False, 'symbols': False}`.
    -   `'spaces'` (`bool`): Include common whitespace characters (default: `True`).
    -   `'numbers'` (`bool`): Include digits (e.g., '0-9', Arabic, Devanagari digits) (default: `False`).
    -   `'punctuation'` (`bool`): Include common and script-specific punctuation marks (default: `False`).
    -   `'symbols'` (`bool`): Include various symbols (e.g., currency, mathematical) (default: `False`).

**Behavior:**
-   Characters not belonging to the specified `script` or excluded by the `config` are replaced with spaces.
-   Multiple spaces are collapsed into a single space.
-   **Priority for overlapping ranges**: If a character falls into multiple categories, the more specific one takes precedence (`punctuation` > `numbers` > `symbols`). This ensures correct filtering.

**Example Usage:**

```python
from unscript import clean_script

# Example 1: Latin script, no numbers or punctuation
text_latin = "Hello World! 123 مرحبا"
cleaned_latin = clean_script("Latn", text_latin)
print(cleaned_latin)
# Expected output: "Hello World"

# Example 2: Arabic script, with numbers
text_arabic = "مرحبا بالعالم 123! Hello"
cleaned_arabic = clean_script("Arab", text_arabic, {"numbers": True})
print(cleaned_arabic)
# Expected output: "مرحبا بالعالم 123"

# Example 3: Chinese script, with punctuation
text_chinese = "你好。世界！This is a test."
cleaned_chinese = clean_script("Hans", text_chinese, {"punctuation": True})
print(cleaned_chinese)
# Expected output: "你好。世界！"

# Example 4: Devanagari script, with punctuation
text_devanagari = "नमस्ते। यह है॥ 987"
cleaned_devanagari = clean_script("Deva", text_devanagari, {"punctuation": True})
print(cleaned_devanagari)
# Expected output: "नमस्ते। यह है॥"
```

### Unicode Ranges and Character Checking

### `ranges` Module

The `ranges` module provides direct access to Unicode ranges for all supported scripts and character categories. This allows for fine-grained control over character detection and filtering.

**Available Ranges:**
- **Script ranges**: Access via `ranges.Arab`, `ranges.Latn`, `ranges.Hans`, etc.
- **Category ranges**: Access via `ranges.numbers`, `ranges.punctuation`, `ranges.spaces`, `ranges.symbols`

**Example Usage:**

```python
from unscript import ranges

# Access script ranges
arabic_ranges = ranges.Arab
print(len(arabic_ranges))  # Number of Unicode ranges for Arabic script

# Access category ranges  
number_ranges = ranges.numbers
punctuation_ranges = ranges.punctuation

# Alternative access through organized objects
latin_ranges = ranges.scripts.Latn
symbol_ranges = ranges.categories.symbols

# List all available ranges
print(ranges.list_scripts())    # ['Arab', 'Armn', 'Beng', 'Brai', ...]
print(ranges.list_categories()) # ['numbers', 'punctuation', 'spaces', 'symbols']

# Get information about a range
info = ranges.get_range_info('Arab')
print(info['type'])         # 'script'
print(info['range_count'])  # Number of Unicode ranges
```

### `in_range(character, *ranges) -> bool`

Check if a character belongs to one or more Unicode ranges. This function supports both script ranges and category ranges, and can check multiple ranges simultaneously (OR logic).

**Arguments:**
- `character` (`str`): A single character to check
- `*ranges`: One or more range lists (script or category ranges)

**Returns:**
- `bool`: True if the character is in any of the specified ranges, False otherwise

**Example Usage:**

```python
from unscript import ranges, in_range

# Check if character is in a single range
print(in_range('ا', ranges.Arab))      # True - Arabic character
print(in_range('A', ranges.Latn))      # True - Latin character  
print(in_range('5', ranges.numbers))   # True - Digit character
print(in_range('!', ranges.punctuation)) # True - Punctuation

# Check multiple ranges (OR logic)
print(in_range('5', ranges.Arab, ranges.numbers))  # True - in numbers
print(in_range('ا', ranges.Arab, ranges.numbers))  # True - in Arabic
print(in_range('A', ranges.Arab, ranges.numbers))  # False - in neither

# Mix script and category ranges
print(in_range('!', ranges.Latn, ranges.punctuation))  # True - punctuation
print(in_range('A', ranges.Latn, ranges.punctuation))  # True - Latin
print(in_range('你', ranges.Latn, ranges.punctuation)) # False - Chinese

# Advanced filtering example
text = "Hello مرحبا 123!"
latin_or_arabic = [char for char in text if in_range(char, ranges.Latn, ranges.Arab)]
print(''.join(latin_or_arabic))  # "Helloمرحبا"

# Check if character is Arabic OR a digit
is_arabic_or_digit = lambda c: in_range(c, ranges.Arab, ranges.numbers)
print(is_arabic_or_digit('ا'))  # True
print(is_arabic_or_digit('5'))  # True
print(is_arabic_or_digit('A'))  # False
```

**Real-world Examples:**

```python
from unscript import ranges, in_range

# Filter multilingual text by script
def filter_by_scripts(text, *script_ranges):
    """Keep only characters from specified scripts."""
    return ''.join(char for char in text 
                  if in_range(char, *script_ranges) or char.isspace())

# Example usage
mixed_text = "Hello مرحبا 你好 123!"
latin_arabic = filter_by_scripts(mixed_text, ranges.Latn, ranges.Arab)
print(latin_arabic)  # "Hello مرحبا   !"

# Content validation
def is_script_compliant(text, script_range, allow_numbers=True, allow_punctuation=True):
    """Check if text only contains allowed character types."""
    allowed_ranges = [script_range]
    if allow_numbers:
        allowed_ranges.append(ranges.numbers)
    if allow_punctuation:
        allowed_ranges.append(ranges.punctuation)
    
    for char in text:
        if char.isspace():
            continue
        if not in_range(char, *allowed_ranges):
            return False
    return True

# Example usage
arabic_text = "مرحبا بالعالم 123!"
print(is_script_compliant(arabic_text, ranges.Arab))  # True

latin_text = "Hello World 你好!"  # Contains Chinese
print(is_script_compliant(latin_text, ranges.Latn))   # False
```

### Script Detection Functions

### `detect_script(text: str, include_categories: bool = False, min_threshold: float = 0.01) -> dict`

Analyzes text and returns the percentage distribution of different Unicode scripts found. By default, it only considers script characters (ignoring spaces, punctuation, numbers, and symbols) to provide clean script percentages.

**Arguments:**
-   `text` (`str`): The text to analyze.
-   `include_categories` (`bool`, optional): Whether to include shared categories (spaces, numbers, punctuation, symbols) in the analysis. Defaults to `False`.
-   `min_threshold` (`float`, optional): Minimum percentage threshold to include in results. Scripts below this threshold are excluded. Defaults to `0.01` (1%).

**Returns:**
-   `dict`: Dictionary mapping script codes to their percentages. When `include_categories=True`, also includes categories like 'spaces', 'numbers', etc.

**Example Usage:**

```python
from unscript import detect_script

# Basic usage - only script percentages
text1 = "Hello World!"
result1 = detect_script(text1)
print(result1)
# Expected output: {'Latn': 100.0}

# Mixed scripts
text2 = "Hello مرحبا 你好"
result2 = detect_script(text2)
print(result2)
# Expected output: {'Latn': 41.67, 'Arab': 41.67, 'Hans': 16.67}

# Including categories for detailed analysis
text3 = "Hello مرحبا 123!"
result3 = detect_script(text3, include_categories=True)
print(result3)
# Expected output: {'Latn': 41.67, 'Arab': 25.0, 'spaces': 16.67, 'punctuation': 8.33, 'numbers': 8.33}

# With minimum threshold to filter out minor scripts
text4 = "Hello World! مرحبا"
result4 = detect_script(text4, min_threshold=10.0)
print(result4)
# Expected output: {'Latn': 77.78, 'Arab': 22.22}
```

### `detect_script_detailed(text: str, normalize_whitespace: bool = False) -> dict`

Provides detailed script detection analysis including character-by-character breakdown and character collections.

**Arguments:**
-   `text` (`str`): The text to analyze.
-   `normalize_whitespace` (`bool`, optional): Whether to treat all whitespace as generic spaces for analysis purposes. Defaults to `False`.

**Returns:**
-   `dict`: Dictionary with detailed analysis including:
    -   `'summary'`: Same as `detect_script()` output with categories included
    -   `'total_chars'`: Total number of characters analyzed
    -   `'breakdown'`: List of dicts with character, script/category, and position info
    -   `'script_chars'`: Dict mapping scripts to character lists
    -   `'category_chars'`: Dict mapping categories to character lists

**Example Usage:**

```python
from unscript import detect_script_detailed

text = "Hi! 你好"
result = detect_script_detailed(text)

print(result['summary'])
# Expected output: {'Latn': 40.0, 'Hans': 40.0, 'punctuation': 20.0}

print(result['total_chars'])
# Expected output: 5

print(result['script_chars'])
# Expected output: {'Latn': ['H', 'i'], 'Hans': ['你', '好']}

print(result['category_chars'])
# Expected output: {'punctuation': ['!']}
```

### `get_dominant_script(text: str, min_percentage: float = 30.0) -> str | None`

Determines the dominant script in the text, if any single script meets the minimum percentage threshold.

**Arguments:**
-   `text` (`str`): The text to analyze.
-   `min_percentage` (`float`, optional): Minimum percentage required to be considered dominant. Defaults to `30.0`.

**Returns:**
-   `str | None`: The dominant script code if found, `None` otherwise.

**Example Usage:**

```python
from unscript import get_dominant_script

# Clear majority
text1 = "Hello world! This is a long English sentence."
result1 = get_dominant_script(text1)
print(result1)
# Expected output: "Latn"

# Mixed text with no clear dominant script
text2 = "Hello مرحبا 你好"
result2 = get_dominant_script(text2)
print(result2)
# Expected output: None

# Custom threshold
text3 = "Hello مرحبا"
result3 = get_dominant_script(text3, min_percentage=20.0)
print(result3)
# Expected output: "Latn" (since Latin has >20%)
```

### `is_script_mixed(text: str, threshold: float = 10.0) -> bool`

Determines if text contains a significant mix of different scripts based on a threshold.

**Arguments:**
-   `text` (`str`): The text to analyze.
-   `threshold` (`float`, optional): Minimum percentage for a script to be considered significant. Defaults to `10.0`.

**Returns:**
-   `bool`: `True` if text contains multiple scripts above the threshold, `False` otherwise.

**Example Usage:**

```python
from unscript import is_script_mixed

# Mixed scripts
text1 = "Hello مرحبا"
result1 = is_script_mixed(text1)
print(result1)
# Expected output: True

# Single script
text2 = "Hello world!"
result2 = is_script_mixed(text2)
print(result2)
# Expected output: False

# Custom threshold
text3 = "Hello World مرحبا"  # ~75% Latin, ~25% Arabic
result3 = is_script_mixed(text3, threshold=30.0)
print(result3)
# Expected output: False (Arabic doesn't meet 30% threshold)
```

## Supported Scripts

`unscript`, `clean_script`, and `detect_script` functions support a wide range of Unicode scripts. Below is a table of the supported script codes and their common names:

| Script Code | Common Name                |
|-------------|----------------------------|
| `Latn`      | Latin                      |
| `Arab`      | Arabic                     |
| `Hebr`      | Hebrew                     |
| `Thai`      | Thai                       |
| `Khmr`      | Khmer                      |
| `Hang`      | Hangul (Korean)            |
| `Hans`      | Han (Simplified Chinese)   |
| `Jpan`      | Japanese (Hiragana & Katakana, Han) |
| `Cyrl`      | Cyrillic                   |
| `Geor`      | Georgian                   |
| `Deva`      | Devanagari                 |
| `Beng`      | Bengali                    |
| `Gujr`      | Gujarati                   |
| `Guru`      | Gurmukhi                   |
| `Ethi`      | Ethiopic                   |
| `Grek`      | Greek                      |
| `Taml`      | Tamil                      |
| `Mlym`      | Malayalam                  |
| `Telu`      | Telugu                     |
| `Knda`      | Kannada                    |
| `Orya`      | Oriya                      |
| `Sinh`      | Sinhala                    |
| `Mymr`      | Myanmar                    |
| `Laoo`      | Lao                        |
| `Tibt`      | Tibetan                    |
| `Armn`      | Armenian                   |
| `Thaa`      | Thaana                     |
| `Mong`      | Mongolian                  |
| `Viet`      | Vietnamese (Latin Extended) |
| `Brai`      | Braille                    |
| `Tfng`      | Tifinagh                   |
| `Hant`      | Han (Traditional Chinese)  |
| `Cans`      | Canadian Aboriginal Syllabics |
| `Cher`      | Cherokee                   |
| `Goth`      | Gothic                     |
| `Olck`      | Ol Chiki                   |
| `Mtei`      | Meetei Mayek               |
| `Syrc`      | Syriac                     |
| `Tale`      | Tai Le                     |
| `Yiii`      | Yi                         |

## Use Cases

### Text Preprocessing for NLP
```python
from unscript import unscript, detect_script

# Clean text for specific language models
arabic_text = unscript("Arab", "مرحبا @user! تحقق من https://example.com 😊")
print(arabic_text)  # "مرحبا تحقق من"

# Detect script composition for language routing
mixed_text = "Hello مرحبا 你好"
scripts = detect_script(mixed_text)
if scripts.get("Arab", 0) > 30:
    # Route to Arabic NLP pipeline
    process_arabic(mixed_text)
```

### Content Filtering and Validation
```python
from unscript import is_script_mixed, get_dominant_script

# Validate content language
user_input = "User's multilingual text"
if is_script_mixed(user_input):
    print("Please use a single language")
else:
    dominant = get_dominant_script(user_input)
    print(f"Detected language script: {dominant}")
```

### Data Analysis and Statistics
```python
from unscript import detect_script_detailed

# Analyze document composition
document = "Large multilingual document..."
analysis = detect_script_detailed(document)
print(f"Total characters: {analysis['total_chars']}")
print(f"Script distribution: {analysis['summary']}")
print(f"Scripts found: {list(analysis['script_chars'].keys())}")
```

### Custom Character Filtering with Ranges
```python
from unscript import ranges, in_range

# Advanced content filtering
def filter_content(text, allowed_scripts=None, allow_digits=True, allow_punctuation=True):
    """Filter text to only include specific character types."""
    if allowed_scripts is None:
        allowed_scripts = [ranges.Latn]  # Default to Latin
    
    extra_ranges = []
    if allow_digits:
        extra_ranges.append(ranges.numbers)
    if allow_punctuation:
        extra_ranges.append(ranges.punctuation)
    
    filtered_chars = []
    for char in text:
        if char.isspace():  # Always allow spaces
            filtered_chars.append(char)
        elif in_range(char, *(allowed_scripts + extra_ranges)):
            filtered_chars.append(char)
        else:
            filtered_chars.append(' ')  # Replace unwanted chars with space
    
    return ''.join(filtered_chars).strip()

# Example usage
multilingual_text = "Hello مرحبا 你好 123! Welcome to unscript."

# Keep only Latin + numbers + punctuation
latin_only = filter_content(multilingual_text, [ranges.Latn])
print(latin_only)  # "Hello     123! Welcome to unscript."

# Keep Arabic + Latin + numbers
arabic_latin = filter_content(multilingual_text, [ranges.Arab, ranges.Latn])
print(arabic_latin)  # "Hello مرحبا   123! Welcome to unscript."

# Input validation for forms
def validate_script_input(text, script_range, max_other_script_ratio=0.1):
    """Validate that text is primarily in the expected script."""
    script_chars = sum(1 for char in text if in_range(char, script_range))
    total_chars = len([char for char in text if not char.isspace()])
    
    if total_chars == 0:
        return True
    
    script_ratio = script_chars / total_chars
    return script_ratio >= (1 - max_other_script_ratio)

# Examples
arabic_form_input = "مرحبا بك في موقعنا"
print(validate_script_input(arabic_form_input, ranges.Arab))  # True

mixed_input = "مرحبا hello world"  # Mixed Arabic and Latin
print(validate_script_input(mixed_input, ranges.Arab))       # False
```

## Contributing

We welcome contributions to Unscript! If you'd like to contribute, please follow these steps:

1.  **Fork the repository** on GitHub.
2.  **Clone your forked repository** to your local machine.
3.  **Create a new branch** for your feature or bug fix: `git checkout -b feature/your-feature-name` or `git checkout -b bugfix/your-bug-fix`.
4.  **Make your changes** and write clear, concise commit messages.
5.  **Write and run tests** to ensure your changes work as expected and don't introduce regressions. We do not use mocks in our tests.
6.  **Ensure all tests pass** by running `python -m unittest` from the project root.
7.  **Push your changes** to your forked repository.
8.  **Open a Pull Request** to the `master` branch of this repository, describing your changes in detail.

## License

Unscript is released under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Contributors

[Omar Kamali](https://github.com/omarkamali)

## Acknowledgments

This project is supported by [Omneity Labs](https://omneitylabs.com), a research lab focused on building NLP and generative AI models for low-resource languages and techniques for cultural alignment.

## Citation

If you use Unscript in your research, please cite it as follows:

```bibtex
@software{unscript2025,
  title={Unscript: Multilingual Text Cleaning},
  author={Omar Kamali},
  year={2025},
  url={https://github.com/omarkamali/unscript}
  note={Project developed under Omneity Labs}
}
```