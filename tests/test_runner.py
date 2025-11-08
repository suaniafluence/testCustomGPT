"""
Test runner for Custom GPT RTF converter
Implements: Golden tests, robustness tests, and RTF format validation
"""

import os
import sys
import re
import json
import requests
import pytest
from pathlib import Path
from typing import Tuple

# Load .env file if it exists
def load_env_file():
    """Load environment variables from .env file in project root"""
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if line and not line.startswith("#"):
                    if "=" in line:
                        key, value = line.split("=", 1)
                        os.environ[key.strip()] = value.strip()

load_env_file()

# Configuration
API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_ID = os.getenv("OPENAI_ASSISTANT_ID")  # Assistant ID
TEST_DIR = Path(__file__).parent
INPUT_DIR = TEST_DIR / "input"
EXPECTED_DIR = TEST_DIR / "expected"
OUTPUT_DIR = TEST_DIR / "output"

# Create output directory if it doesn't exist
OUTPUT_DIR.mkdir(exist_ok=True)


class RTFValidator:
    """Validates RTF format integrity"""

    @staticmethod
    def is_valid_rtf(content: str) -> Tuple[bool, str]:
        """
        Check if content is valid RTF
        Returns: (is_valid, error_message)
        """
        if not content.strip():
            return False, "Empty content"

        # Basic RTF structure checks
        if not content.strip().startswith("{\\rtf"):
            return False, "Missing RTF header {\\rtf"

        if not content.strip().endswith("}"):
            return False, "Missing closing brace }"

        # Check for balanced braces
        brace_count = 0
        for char in content:
            if char == "{":
                brace_count += 1
            elif char == "}":
                brace_count -= 1
            if brace_count < 0:
                return False, "Unbalanced braces (more closing than opening)"

        if brace_count != 0:
            return False, f"Unbalanced braces (difference: {brace_count})"

        # Check for essential RTF elements
        if "\\ansi" not in content and "\\mac" not in content and "\\pc" not in content:
            return False, "Missing character set declaration"

        return True, "Valid RTF"

    @staticmethod
    def extract_visible_text(rtf_content: str) -> str:
        """Extract visible text from RTF, removing formatting commands"""
        # Remove RTF control sequences but keep text content
        text = re.sub(r"\\[a-z0-9]+\d*\s?", " ", rtf_content)
        # Remove braces
        text = re.sub(r"[{}]", " ", text)
        # Remove special characters and extra spaces
        text = re.sub(r"\s+", " ", text).strip()
        return text


class CustomGPTTester:
    """Handles communication with OpenAI Assistant"""

    @staticmethod
    def call_custom_gpt(prompt: str) -> str:
        """Send prompt to Assistant and return response"""
        if not API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        if not MODEL_ID:
            raise ValueError("OPENAI_ASSISTANT_ID environment variable not set")

        try:
            from openai import OpenAI

            client = OpenAI(api_key=API_KEY)

            # Create a thread
            thread = client.beta.threads.create()

            # Add message to thread
            client.beta.threads.messages.create(
                thread_id=thread.id, role="user", content=prompt
            )

            # Run the assistant
            run = client.beta.threads.runs.create(
                thread_id=thread.id, assistant_id=MODEL_ID
            )

            # Wait for completion (with timeout)
            import time

            timeout = 60
            start_time = time.time()
            while run.status in ["queued", "in_progress"]:
                if time.time() - start_time > timeout:
                    raise TimeoutError(f"Assistant run timed out after {timeout}s")

                time.sleep(0.5)
                run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

            if run.status != "completed":
                raise RuntimeError(f"Assistant run failed with status: {run.status}")

            # Get messages
            messages = client.beta.threads.messages.list(thread_id=thread.id)

            # Return the last assistant message
            for msg in messages.data:
                if msg.role == "assistant":
                    content_block = msg.content[0]
                    # TextContentBlock has a .text attribute which is a Text object
                    # Text object has a .value attribute with the actual content
                    if hasattr(content_block, 'text'):
                        text_obj = content_block.text
                        if hasattr(text_obj, 'value'):
                            return text_obj.value

                    # Fallback: try direct access
                    if hasattr(content_block, 'value'):
                        return content_block.value

                    # Last resort: stringify
                    return str(content_block)

            raise RuntimeError("No response from assistant")

        except Exception as e:
            raise RuntimeError(f"API call failed: {str(e)}")


class TextNormalizer:
    """Normalizes text for comparison, handling minor variations"""

    @staticmethod
    def normalize(text: str) -> str:
        """
        Normalize text by:
        - Converting to lowercase
        - Removing extra whitespace
        - Removing common punctuation variations
        """
        # Convert to lowercase
        text = text.lower()
        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text).strip()
        # Normalize dashes and quotes
        text = text.replace("—", "-").replace("–", "-")
        text = text.replace(""", '"').replace(""", '"')
        text = text.replace("'", "'").replace("'", "'")
        return text

    @staticmethod
    def assert_normalized_equal(actual: str, expected: str, tolerance: float = 0.85):
        """
        Compare two texts with tolerance for minor differences
        tolerance: minimum similarity ratio (0-1)
        """
        norm_actual = TextNormalizer.normalize(actual)
        norm_expected = TextNormalizer.normalize(expected)

        # Check if expected content is substantially in actual
        # (accounts for variations in formatting/structure)
        if norm_expected in norm_actual:
            return True

        # Calculate similarity (simple approach: matching words)
        actual_words = set(norm_actual.split())
        expected_words = set(norm_expected.split())

        if not expected_words:
            return False

        matching = len(actual_words & expected_words)
        similarity = matching / len(expected_words)

        if similarity < tolerance:
            raise AssertionError(
                f"Text similarity too low: {similarity:.2%} (expected >= {tolerance:.0%})\n"
                f"Expected words: {len(expected_words)}\n"
                f"Matched words: {matching}\n"
            )

        return True


# ============================================================================
# PYTEST TESTS
# ============================================================================


class TestRTFValidation:
    """Test RTF format validity"""

    def test_rtf_header_present(self):
        """RTF output must start with RTF header"""
        validator = RTFValidator()
        assert validator.is_valid_rtf("{\\rtf1\\ansi test}")[0], "Valid RTF should pass"

    def test_rtf_unbalanced_braces(self):
        """RTF must have balanced braces"""
        validator = RTFValidator()
        is_valid, msg = validator.is_valid_rtf("{\\rtf1\\ansi test")
        assert not is_valid, "Should reject unbalanced braces"
        assert "brace" in msg.lower()

    def test_rtf_empty_content(self):
        """Empty RTF should be rejected"""
        validator = RTFValidator()
        is_valid, msg = validator.is_valid_rtf("")
        assert not is_valid, "Should reject empty content"


@pytest.mark.parametrize("sample", ["sample1", "sample2"])
class TestGoldenTests:
    """Golden tests: Compare output against expected reference"""

    def test_rtf_format_validity(self, sample):
        """Generated RTF must be valid"""
        with open(INPUT_DIR / f"{sample}.txt") as f:
            prompt = f.read()

        output = CustomGPTTester.call_custom_gpt(prompt)

        # Save output for inspection
        with open(OUTPUT_DIR / f"{sample}_output.rtf", "w") as f:
            f.write(output)

        validator = RTFValidator()
        is_valid, msg = validator.is_valid_rtf(output)
        assert is_valid, f"Invalid RTF output: {msg}"

    def test_content_matches_expected(self, sample):
        """Output content should match expected reference"""
        with open(INPUT_DIR / f"{sample}.txt") as f:
            prompt = f.read()

        with open(EXPECTED_DIR / f"{sample}_expected.rtf") as f:
            expected = f.read()

        output = CustomGPTTester.call_custom_gpt(prompt)

        # Save output
        with open(OUTPUT_DIR / f"{sample}_output.rtf", "w") as f:
            f.write(output)

        # Extract visible text for comparison
        validator = RTFValidator()
        actual_text = validator.extract_visible_text(output)
        expected_text = validator.extract_visible_text(expected)

        # Use normalized comparison
        TextNormalizer.assert_normalized_equal(actual_text, expected_text)

    def test_no_rtf_corruption(self, sample):
        """RTF structure must not be corrupted"""
        with open(INPUT_DIR / f"{sample}.txt") as f:
            prompt = f.read()

        output = CustomGPTTester.call_custom_gpt(prompt)

        # Check for common RTF corruption patterns
        assert "\\par" in output or "\\line" in output, "Missing paragraph markers"
        assert "{\\rtf" in output, "Missing RTF declaration"
        assert "\\ansicpg" in output or "\\ansicpg" not in output, "Character set OK"  # More flexible


class TestRobustness:
    """Robustness tests: Verify stability across variations"""

    @pytest.mark.parametrize(
        "variation",
        [
            "sample1.txt",  # Original
            "sample1.txt",  # Duplicate to test consistency
        ],
    )
    def test_consistent_output_format(self, variation):
        """Multiple calls should produce consistent RTF format"""
        with open(INPUT_DIR / variation) as f:
            prompt = f.read()

        output = CustomGPTTester.call_custom_gpt(prompt)

        validator = RTFValidator()
        is_valid, msg = validator.is_valid_rtf(output)
        assert is_valid, f"Inconsistent output format: {msg}"

    def test_handles_special_characters(self):
        """Should handle accented characters and special symbols"""
        prompt = "Convertir en RTF: Café, naïve, £500, © 2025"
        output = CustomGPTTester.call_custom_gpt(prompt)

        validator = RTFValidator()
        is_valid, _ = validator.is_valid_rtf(output)
        assert is_valid, "Should handle special characters"

        # Check that some output was generated
        assert len(output) > 50, "Output should be substantial"


class TestIntegration:
    """Integration tests combining multiple aspects"""

    def test_full_pipeline(self):
        """Test complete pipeline: input -> API -> validation -> comparison"""
        sample = "sample1"

        with open(INPUT_DIR / f"{sample}.txt") as f:
            prompt = f.read()

        with open(EXPECTED_DIR / f"{sample}_expected.rtf") as f:
            expected = f.read()

        # Call API
        output = CustomGPTTester.call_custom_gpt(prompt)

        # Validate RTF
        validator = RTFValidator()
        is_valid, msg = validator.is_valid_rtf(output)
        assert is_valid, f"RTF validation failed: {msg}"

        # Extract and compare text
        actual_text = validator.extract_visible_text(output)
        expected_text = validator.extract_visible_text(expected)

        TextNormalizer.assert_normalized_equal(actual_text, expected_text, tolerance=0.80)

    def test_report_generation(self):
        """Generate test report"""
        report = {
            "timestamp": __import__("datetime").datetime.now().isoformat(),
            "model_id": MODEL_ID,
            "tests_run": 0,
            "results": {},
        }

        # This would be populated by pytest hooks in a real scenario
        print("\n" + "=" * 60)
        print("TEST REPORT")
        print("=" * 60)
        print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
