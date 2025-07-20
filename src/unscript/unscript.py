import time
import unicodedata
import re

# Import script ranges from the shared module
from .script_ranges import SCRIPT_CORE_RANGES, SHARED_RANGES


def create_clean_script_function(default_config=None):
    """
    Factory function that creates a clean_script function with precalculated ranges based on config.

    Args:
        default_config (dict): Default configuration for character types to include
                             {
                                 'spaces': bool,
                                 'numbers': bool,
                                 'punctuation': bool,
                                 'symbols': bool
                             }
    """
    if default_config is None:
        default_config = {
            "spaces": True,
            "numbers": False,
            "punctuation": False,
            "symbols": False,
        }

    def clean_script(script, text, config=None):
        """
        Remove any characters that don't belong to the specified script.

        Args:
            script (str): The script code (e.g., 'Latn', 'Arab')
            text (str): The text to clean
            config (dict): Configuration to override default_config

        Returns:
            str: Text with only characters from the specified script
        """
        if not text:
            return text

        # If script is not in our dictionary, return the original text
        if script not in SCRIPT_CORE_RANGES:
            return text

        # Merge configs
        current_config = default_config.copy()
        if config:
            current_config.update(config)

        # If numbers are enabled, protect decimal numbers first
        if current_config.get("numbers", False):
            # Pattern to match decimal numbers (including various decimal separators)
            # This matches patterns like: 123.45, 123,45, 1.234.567, 1,234,567, etc.
            decimal_pattern = r"\b\d+[.,]\d+(?:[.,]\d+)*\b"
            decimal_numbers = re.findall(decimal_pattern, text)

            # Replace decimal numbers with placeholders
            placeholders = {}
            protected_text = text
            for i, number in enumerate(decimal_numbers):
                placeholder = f"__DECIMAL_{i}__"
                placeholders[placeholder] = number
                protected_text = protected_text.replace(number, placeholder, 1)
        else:
            protected_text = text
            placeholders = {}

        # Build ranges to use
        ranges_to_use = list(SCRIPT_CORE_RANGES[script])

        # Add spaces based on config
        if current_config.get("spaces", True):
            ranges_to_use.extend(SHARED_RANGES["spaces"])

        # Add other shared ranges based on config
        for category, include in current_config.items():
            if include and category in SHARED_RANGES and category != "spaces":
                ranges_to_use.extend(SHARED_RANGES[category])

        # Build ranges to exclude
        ranges_to_exclude = []
        for category, include in current_config.items():
            if not include and category in SHARED_RANGES:
                ranges_to_exclude.extend(SHARED_RANGES[category])

        # Process each character: keep included characters, replace excluded punctuation with spaces
        result = []
        i = 0
        while i < len(protected_text):
            # Check if we're at a placeholder
            if protected_text[i:].startswith("__DECIMAL_"):
                # Find the end of the placeholder
                end_pos = protected_text.find("__", i + 2) + 2
                placeholder = protected_text[i:end_pos]
                if placeholder in placeholders:
                    result.append(placeholders[placeholder])
                    i = end_pos
                    continue

            char = protected_text[i]
            code_point = ord(char)
            in_included_range = False

            # Check if character is in included ranges
            for start, end in ranges_to_use:
                if start <= code_point <= end:
                    in_included_range = True
                    break

            # Even if character is in included ranges, check if it should be excluded
            # due to configuration (e.g., numbers=False should exclude digits even if in script range)
            should_exclude = False
            if in_included_range:
                # Check if this character is in excluded categories
                # Use priority: punctuation > numbers > symbols (most specific first)
                category_priority = ["punctuation", "numbers", "symbols"]

                for category in category_priority:
                    if category in current_config:
                        include = current_config[category]
                        if category in SHARED_RANGES:
                            for start, end in SHARED_RANGES[category]:
                                if start <= code_point <= end:
                                    # Character found in this category
                                    if not include:
                                        should_exclude = True
                                    # Stop checking other categories (found the primary category)
                                    break
                            if (
                                start <= code_point <= end
                            ):  # If we found it in this category
                                break

            if in_included_range and not should_exclude:
                result.append(char)
            else:
                # Character is not in included ranges or should be excluded
                # Replace any non-letter character with space to prevent word merging
                # Only skip replacement if character is a space (already handled by spaces config)
                if not char.isspace():
                    result.append(
                        " "
                    )  # Replace non-letter with space to prevent word merging
                # If it's a space, just remove it (don't append anything) since spaces are handled by config

            i += 1

        # Collapse multiple spaces into one
        return re.sub(r"\s+", " ", "".join(result)).strip()

    return clean_script


# Create default clean_script function
clean_script = create_clean_script_function()


# Tests for clean_script function
def test_clean_script():
    # Basic tests with different configs
    assert clean_script("Latn", "Hello World 123!") == "Hello World"
    assert (
        clean_script("Latn", "Hello World 123!", {"numbers": True}) == "Hello World 123"
    )
    assert (
        clean_script("Latn", "Hello World 123!", {"punctuation": True})
        == "Hello World !"
    )
    assert (
        clean_script("Latn", "Hello World 123!", {"numbers": True, "punctuation": True})
        == "Hello World 123!"
    )

    # Test with symbols
    assert (
        clean_script("Latn", "Cost: $50 and 25°C", {"symbols": True}) == "Cost $ and °C"
    )
    assert (
        clean_script("Latn", "Cost: $50 and 25°C", {"symbols": True, "numbers": True})
        == "Cost $50 and 25°C"
    )
    assert (
        clean_script(
            "Latn",
            "Cost: $50 and 25°C",
            {"symbols": True, "numbers": True, "punctuation": True},
        )
        == "Cost: $50 and 25°C"
    )

    # Test Arabic script
    assert clean_script("Arab", "مرحبا بالعالم 123!") == "مرحبا بالعالم"
    assert (
        clean_script("Arab", "مرحبا بالعالم ١٢٣!", {"numbers": True})
        == "مرحبا بالعالم ١٢٣"
    )
    assert (
        clean_script("Arab", "مرحبا بالعالم ١٢٣!", {"punctuation": True})
        == "مرحبا بالعالم !"
    )
    assert (
        clean_script(
            "Arab", "مرحبا بالعالم ١٢٣!", {"numbers": True, "punctuation": True}
        )
        == "مرحبا بالعالم ١٢٣!"
    )

    # Test Hebrew script
    assert clean_script("Hebr", "שלום עולם 123!") == "שלום עולם"
    assert clean_script("Hebr", "שלום עולם 123!", {"numbers": True}) == "שלום עולם 123"
    assert (
        clean_script("Hebr", "שלום עולם 123!", {"punctuation": True}) == "שלום עולם !"
    )

    # Test Cyrillic script
    assert clean_script("Cyrl", "Привет мир 123!") == "Привет мир"
    assert (
        clean_script("Cyrl", "Привет мир 123!", {"punctuation": True}) == "Привет мир !"
    )
    assert (
        clean_script("Cyrl", "Привет мир 123!", {"numbers": True}) == "Привет мир 123"
    )

    # Test mixed scripts
    mixed_text = "Hello مرحبا שלום Привет 你好 こんにちは 123!"
    assert clean_script("Latn", mixed_text) == "Hello"
    assert clean_script("Latn", mixed_text, {"numbers": True}) == "Hello 123"
    assert clean_script("Latn", mixed_text, {"punctuation": True}) == "Hello !"
    assert clean_script("Arab", mixed_text) == "مرحبا"
    assert clean_script("Hebr", mixed_text) == "שלום"
    assert clean_script("Cyrl", mixed_text) == "Привет"
    assert clean_script("Hans", mixed_text) == "你好"
    assert clean_script("Jpan", mixed_text) == "你好 こんにちは"

    # Test full config
    full_config = {"numbers": True, "punctuation": True, "symbols": True}
    assert clean_script("Latn", "Hello $123.45!", full_config) == "Hello $123.45!"
    assert (
        clean_script("Latn", "Hello $123.45 € ¥ £", full_config)
        == "Hello $123.45 € ¥ £"
    )

    # Test different number systems
    assert clean_script("Arab", "عربية ١٢٣٤٥", {"numbers": True}) == "عربية ١٢٣٤٥"
    assert clean_script("Deva", "देवनागरी १२३४५", {"numbers": True}) == "देवनागरी १२३४५"
    assert clean_script("Thai", "ไทย ๑๒๓๔๕", {"numbers": True}) == "ไทย ๑๒๓๔๕"

    # Test with multiple spaces
    assert clean_script("Latn", "Hello    World") == "Hello World"
    assert (
        clean_script("Latn", "Hello    World    123", {"numbers": True})
        == "Hello World 123"
    )

    # Test with special characters
    assert (
        clean_script("Latn", "Temperature: 25°C", {"symbols": True}) == "Temperature °C"
    )
    assert clean_script("Latn", "H₂O and CO₂", {"symbols": True}) == "H₂O and CO₂"
    assert clean_script("Latn", "H₂O and CO₂", {"numbers": True}) == "HO and CO"

    # Test with emojis (should be removed as they're not in any script ranges)
    assert clean_script("Latn", "Hello 😊 World") == "Hello World"
    assert clean_script("Arab", "مرحبا 😊 بالعالم") == "مرحبا بالعالم"

    # Test with URLs and email addresses
    assert (
        clean_script("Latn", "Visit https://example.com", {"punctuation": True})
        == "Visit https:example.com"
    )
    assert (
        clean_script(
            "Latn", "Email: user@example.com", {"symbols": True, "punctuation": True}
        )
        == "Email: user@example.com"
    )

    # Test empty string
    assert clean_script("Latn", "") == ""

    # Test script not in dictionary
    assert clean_script("Unknown", "Hello World") == "Hello World"

    # Test with various punctuation
    assert (
        clean_script("Latn", "Hello, World! How are you?", {"punctuation": True})
        == "Hello, World! How are you?"
    )
    assert (
        clean_script("Latn", "Hello, World! How are you?") == "Hello World How are you"
    )

    # Test with math symbols
    assert (
        clean_script("Latn", "1 + 2 = 3", {"numbers": True, "symbols": True})
        == "1 + 2 = 3"
    )
    assert clean_script("Latn", "1 + 2 = 3", {"numbers": True}) == "1 2 3"

    # Test with fractions and superscripts
    assert (
        clean_script("Latn", "½ cup and x² value", {"symbols": True})
        == "½ cup and x² value"
    )
    assert clean_script("Latn", "½ cup and x² value") == "cup and x value"

    # Test specifically for dollar sign with symbols enabled
    assert clean_script("Latn", "$100", {"symbols": True}) == "$"
    assert clean_script("Latn", "$100", {"symbols": True, "numbers": True}) == "$100"

    print("All tests passed!")


import re


def remove_emoji(text):
    """
    Remove emojis from text
    """
    if not isinstance(text, str):
        return ""

    str_copy = text

    # Emoji keycap regex (numbers with combining enclosing keycap)
    emoji_keycap_regex = r"[\u0023-\u0039]\ufe0f?\u20e3"
    if re.search(emoji_keycap_regex, str_copy):
        str_copy = re.sub(emoji_keycap_regex, "", str_copy)

    # Extended pictographic characters (general emoji pattern)
    # Python doesn't support \p{Extended_Pictographic} directly, so we use a simplified approach
    # This is an approximation of the emoji ranges
    emoji_regex = r"[\U0001F000-\U0001FFFF]"
    if re.search(emoji_regex, str_copy):
        str_copy = re.sub(emoji_regex, "", str_copy)

    # Emoji component characters (like skin tone modifiers)
    # Again, this is an approximation as Python regex doesn't support \p{Emoji_Component}
    emoji_component_regex = (
        r"[\u200D\u20E3\uFE0F\u2640-\u2642\u2600-\u26FF\u2700-\u27BF]"
    )
    if re.search(emoji_component_regex, str_copy):
        for match in re.finditer(emoji_component_regex, str_copy):
            emoji = match.group(0)
            if not re.search(r"[\d|*|#]", emoji):
                str_copy = str_copy.replace(emoji, "")

    return str_copy


def clean_text(text, lowercase=True):
    """
    Cleans text by removing @mentions, @@mentions, +mentions, hashtags, URLs, emojis,
    invalid Unicode characters, collapsing letter repetition, and normalizing newlines.
    This function is now script-agnostic - use clean_script or unscript for script filtering.

    Args:
        text (str): The text to clean
        lowercase (bool): Whether to convert text to lowercase. Defaults to True.

    Returns:
        str: Cleaned text
    """
    if not isinstance(text, str):
        return ""

    # Remove emojis
    text = remove_emoji(text)

    # Remove @mentions and @@mentions
    text = re.sub(r"@{1,2}[a-zA-Z0-9_]+", "", text)

    # Remove +mentions
    text = re.sub(r"[+][a-zA-Z0-9_]+", "", text)

    # Remove hashtags
    text = re.sub(r"#[a-zA-Z0-9_]+", "", text)

    # Remove URLs (including those without protocol and email addresses)
    text = re.sub(r"https?://\S+", "", text)  # http/https URLs
    text = re.sub(r"ftp://\S+", "", text)  # ftp URLs
    text = re.sub(r"www\.\S+", "", text)  # www URLs
    text = re.sub(r"\S+@\S+\.\S+", "", text)  # email addresses
    # Domain names like example.com (but not decimal numbers)
    text = re.sub(r"\b[a-zA-Z]+\.[a-zA-Z]{2,}\b", "", text)

    # Normalize Unicode characters to handle invalid/error Unicode
    try:
        text = unicodedata.normalize("NFD", text)
    except UnicodeError:
        # Handle invalid Unicode by filtering out problematic characters
        text = "".join(c for c in text if ord(c) < 0x110000)
        text = unicodedata.normalize("NFD", text)

    # Convert to lowercase for normalization if requested
    if lowercase:
        text = text.lower()

    # Collapse repeating characters to maximum of 2 characters (except for numbers)
    text = re.sub(r"([^\d])\1{2,}", r"\1\1", text)

    # Replace newlines and other whitespace characters with single spaces
    text = re.sub(r"[\n\r\t]+", " ", text)

    # Clean up multiple spaces into single spaces
    text = re.sub(r"\s+", " ", text).strip()

    # Return empty string if the result is only numbers
    if re.match(r"^\d+$", text):
        return ""

    return text


def unscript(script, text, config=None, lowercase=True):
    """
    Complete text cleaning pipeline that combines general text cleaning with script filtering.

    This function applies clean_text first to remove mentions, URLs, emojis, and normalize the text,
    then applies clean_script to filter text to the specified script.

    Args:
        script (str): The Unicode script code (e.g., 'Latn', 'Arab', 'Hans')
        text (str): The text string to be cleaned
        config (dict, optional): Configuration for clean_script. Defaults to
                               {'spaces': True, 'numbers': False, 'punctuation': False, 'symbols': False}
        lowercase (bool, optional): Whether to convert text to lowercase. Defaults to True.

    Returns:
        str: Cleaned text containing only characters from the specified script,
             with mentions, URLs, and other noise removed

    Example:
        >>> unscript("Latn", "Hello @user! Check https://example.com 😊")
        "hello"

        >>> unscript("Arab", "مرحبا @user بالعالم! https://example.com", {"punctuation": True})
        "مرحبا بالعالم!"
    """
    if not isinstance(text, str):
        return ""

    # First apply general text cleaning to remove mentions, URLs, emojis
    text_cleaned = clean_text(text, lowercase=lowercase)

    # Then apply script filtering
    script_filtered = clean_script(script, text_cleaned, config)

    return script_filtered
