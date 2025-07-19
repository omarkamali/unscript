# Unscript: Multilingual Text Cleaning

Unscript is a Python package designed for robust and flexible text cleaning, particularly for multilingual data. It provides functions to sanitize text by removing unwanted elements like mentions, hashtags, URLs, and emojis, and to filter text based on specific Unicode script ranges.

## Installation

To install Unscript, you can use `pip`:

```bash
pip install unscript
```

## Quick Start

```python
from unscript import unscript, clean_text, clean_script

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
```

## Functions

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
from unscript.unscript import unscript

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
from unscript.unscript import clean_text

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
from unscript.unscript import clean_script

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

## Supported Scripts

`unscript` and `clean_script` functions support a wide range of Unicode scripts. Below is a table of the supported script codes and their common names:

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





