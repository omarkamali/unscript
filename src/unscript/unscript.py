import time
import unicodedata
import re

# Import script ranges from the shared module
from unscript.script_ranges import (
    SCRIPT_CORE_RANGES,
    SHARED_RANGES,
    PUNCTUATION_ASCII,
    PUNCTUATION_EXTENDED,
    PUNCTUATION_ALL,
)

DEFAULT_CONFIG = {
    "spaces": True,
    "numbers": False,
    "punctuation": False,
    "symbols": False,
    "max_foreign_words": 0,
    "foreign_scripts": None,
}

def clean_script(script, text, config=None):
    """
    Remove any characters that don't belong to the specified script.

    Args:
        script (str | list | tuple | set): One or more script codes (e.g., 'Latn', 'Arab')
        text (str): The text to clean
        config (dict): Configuration overriding DEFAULT_CONFIG

    Returns:
        str: Text with only characters from the specified script
    """
    if not text:
        return text

    # Normalize scripts argument to a list of valid script codes
    if isinstance(script, str):
        primary_scripts = [script]
    else:
        try:
            primary_scripts = list(script)
        except TypeError:
            primary_scripts = [str(script)]

    primary_scripts = [s for s in primary_scripts if s in SCRIPT_CORE_RANGES]
    if not primary_scripts:
        return text

    # Merge configs
    current_config = DEFAULT_CONFIG.copy()
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

    # Build ranges to use (non-cached)
    ranges_to_use = []
    for s in primary_scripts:
        ranges_to_use.extend(SCRIPT_CORE_RANGES[s])
    # Add spaces based on config
    if current_config.get("spaces", True):
        ranges_to_use.extend(SHARED_RANGES["spaces"])

    # Handle punctuation levels (boolean or string)
    punct_cfg = current_config.get("punctuation", False)
    active_punct_ranges = []
    if isinstance(punct_cfg, str):
        level = punct_cfg.lower()
        if level == "ascii":
            active_punct_ranges = list(PUNCTUATION_ASCII)
        elif level == "extended":
            active_punct_ranges = list(PUNCTUATION_EXTENDED)
        elif level == "all":
            active_punct_ranges = list(PUNCTUATION_ALL)
        # Unknown string -> keep active empty (no punctuation)
    elif punct_cfg:
        # Backward-compatible mapping: True -> ASCII level
        active_punct_ranges = list(PUNCTUATION_ASCII)

    # Include active punctuation ranges in the allowed set
    if active_punct_ranges:
        ranges_to_use.extend(active_punct_ranges)

    # Add other shared ranges based on config (exclude punctuation handled above and spaces handled already)
    for category, include in current_config.items():
        if category in ("spaces", "punctuation"):
            continue
        if include and category in SHARED_RANGES:
            ranges_to_use.extend(SHARED_RANGES[category])

    # Precompute up to N other-script token spans on protected_text
    allow_n = int(current_config.get("max_foreign_words", 0) or 0)
    allowed_whitelist = current_config.get("foreign_scripts", None)
    if isinstance(allowed_whitelist, str):
        allowed_whitelist = [allowed_whitelist]
    if allowed_whitelist is not None:
        allowed_whitelist = [s for s in allowed_whitelist if s in SCRIPT_CORE_RANGES]

    other_token_spans = []
    if allow_n > 0:
        def token_dominant_script(tok: str):
            counts = {}
            for ch in tok:
                cp = ord(ch)
                for sc in SCRIPT_CORE_RANGES:
                    for a, b in SCRIPT_CORE_RANGES[sc]:
                        if a <= cp <= b:
                            counts[sc] = counts.get(sc, 0) + 1
                            break
                    else:
                        continue
                    break
            if not counts:
                return None
            return max(counts.items(), key=lambda x: x[1])[0]

        taken = 0
        for m in re.finditer(r"\S+", protected_text):
            if taken >= allow_n:
                break
            tok = m.group(0)
            dom = token_dominant_script(tok)
            if dom is None:
                continue
            if dom in primary_scripts:
                continue
            if allowed_whitelist is not None and dom not in allowed_whitelist:
                continue
            other_token_spans.append((m.start(), m.end(), dom))
            taken += 1

    # Process each character: keep included characters, replace excluded punctuation with spaces
    result = []
    i = 0
    span_idx = 0
    current_span = other_token_spans[span_idx] if other_token_spans else None
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

        # Advance current span pointer if needed
        if current_span is not None and i >= current_span[1]:
            span_idx += 1
            current_span = other_token_spans[span_idx] if span_idx < len(other_token_spans) else None

        # Check if character is in included ranges
        for start, end in ranges_to_use:
            if start <= code_point <= end:
                in_included_range = True
                break

        # If not included, but inside an allowed other-script token, allow letters from that token's dominant script
        if not in_included_range and current_span is not None and current_span[0] <= i < current_span[1]:
            dom_script = current_span[2]
            for start, end in SCRIPT_CORE_RANGES[dom_script]:
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

            matched_primary = False
            for category in category_priority:
                if category in current_config:
                    include = current_config[category]
                    # Treat string punctuation levels as enabled for category checks
                    if category == "punctuation" and isinstance(include, str):
                        include_bool = True
                    else:
                        include_bool = bool(include)

                    if category == "punctuation":
                        # Detect punctuation using the shared superset first
                        is_punct = False
                        for start, end in SHARED_RANGES["punctuation"]:
                            if start <= code_point <= end:
                                is_punct = True
                                break
                        if is_punct:
                            # If punctuation is disabled entirely -> exclude
                            if not include_bool:
                                should_exclude = True
                            else:
                                # If enabled with a level, only allow if inside the active set
                                if active_punct_ranges:
                                    in_active = False
                                    for s, e in active_punct_ranges:
                                        if s <= code_point <= e:
                                            in_active = True
                                            break
                                    if not in_active:
                                        should_exclude = True
                                else:
                                    # include_bool True but no active ranges -> treat as disabled
                                    should_exclude = True
                            matched_primary = True
                    else:
                        if category in SHARED_RANGES:
                            for start, end in SHARED_RANGES[category]:
                                if start <= code_point <= end:
                                    if not include_bool:
                                        should_exclude = True
                                    matched_primary = True
                                    break
                if matched_primary:
                    # We matched a category; do not check lower-priority categories
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
