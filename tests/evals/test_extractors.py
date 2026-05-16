from runtime.evals import ExtractorSpec
from runtime.evals.extractors import (
    ExtractorRegistry,
    LastAssistantExtractor,
    JsonFieldExtractor,
    RegexCaptureExtractor,
    CodeBlockExtractor,
)

class TestExtractors:
    """Tests for response extractors."""
    
    def test_last_assistant_plain(self):
        """Test extracting from plain text."""
        ext = LastAssistantExtractor()
        result = ext.extract("The answer is 42.")
        assert result == "The answer is 42."
    
    def test_last_assistant_chat_format(self):
        """Test extracting from chat format."""
        ext = LastAssistantExtractor()
        response = "User: What is 2+2?\nAssistant: 4\nUser: Thanks!\nAssistant: You're welcome!"
        result = ext.extract(response)
        assert result == "You're welcome!"
    
    def test_json_field_basic(self):
        """Test JSON field extraction."""
        ext = JsonFieldExtractor(config={"field": "answer"})
        response = '{"answer": "Paris", "confidence": 0.9}'
        result = ext.extract(response)
        assert result == "Paris"
    
    def test_json_field_nested(self):
        """Test nested JSON field extraction."""
        ext = JsonFieldExtractor(config={"field": "result.value"})
        response = '{"result": {"value": 42, "unit": "meters"}}'
        result = ext.extract(response)
        assert result == "42"
    
    def test_json_field_in_markdown(self):
        """Test JSON in markdown code block."""
        ext = JsonFieldExtractor(config={"field": "answer"})
        response = "Here's the answer:\n```json\n{\"answer\": \"42\"}\n```"
        result = ext.extract(response)
        assert result == "42"
    
    def test_regex_capture(self):
        """Test regex capture extraction."""
        ext = RegexCaptureExtractor(config={"pattern": r"Answer:\s*(.+)"})
        response = "The question was easy.\nAnswer: 42\nThat's it."
        result = ext.extract(response)
        assert result == "42"
    
    def test_regex_capture_with_flags(self):
        """Test regex with case-insensitive flag."""
        ext = RegexCaptureExtractor(config={"pattern": r"answer:\s*(\w+)", "flags": "i"})
        response = "ANSWER: Paris"
        result = ext.extract(response)
        assert result == "Paris"
    
    def test_code_block_python(self):
        """Test Python code block extraction."""
        ext = CodeBlockExtractor(config={"language": "python"})
        response = "Here's the code:\n```python\ndef hello():\n    print('Hi')\n```"
        result = ext.extract(response)
        assert "def hello():" in result
        assert "print('Hi')" in result
    
    def test_registry_list(self):
        """Test listing extractors."""
        extractors = ExtractorRegistry.list_extractors()
        assert "last_assistant" in extractors
        assert "json_field" in extractors
        assert "regex" in extractors
    
    def test_registry_create(self):
        """Test creating extractor from spec."""
        spec = ExtractorSpec(name="json_field", config={"field": "answer"})
        ext = ExtractorRegistry.create(spec)
        assert isinstance(ext, JsonFieldExtractor)
