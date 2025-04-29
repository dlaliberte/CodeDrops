"""
# CodeDrops Extractor
## Requirements:
- Parse a single file containing requirements, design, implementation, and testing sections
- Extract each section into separate components
- Include appropriate documentation in generated files
- Support multiple programming languages
- Preserve code formatting and comments
- Provide a simple API for integration with other tools

## Design:
- Use regular expressions to identify section markers
- Support customizable section identifiers
- Return structured data containing each extracted component
- Include validation to ensure all required sections are present
- Add documentation headers to generated files
- Implement as a standalone module that can be imported by other CodeDrops tools
"""

import re
import os
from enum import Enum
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime

class SectionType(Enum):
    """Enumeration of possible sections in a CodeDrop."""
    REQUIREMENTS = "requirements"
    DESIGN = "design"
    IMPLEMENTATION = "implementation"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    UNKNOWN = "unknown"

class CodeDropExtractor:
    """
    Extracts different sections from a CodeDrop file.

    A CodeDrop file contains requirements, design, implementation, and testing
    all in a single file. This class parses such files and extracts each section.
    """

    # Default section markers (can be customized)
    DEFAULT_MARKERS = {
        SectionType.REQUIREMENTS: [
            r"#+\s*Requirements:?",
            r"#+\s*Specification:?",
            r"/\*+\s*Requirements:?\s*\*+/",
            r"//+\s*Requirements:?",
            r"\"\"\"[\s\S]*?Requirements:?[\s\S]*?\"\"\""
        ],
        SectionType.DESIGN: [
            r"#+\s*Design:?",
            r"#+\s*Architecture:?",
            r"/\*+\s*Design:?\s*\*+/",
            r"//+\s*Design:?",
            r"\"\"\"[\s\S]*?Design:?[\s\S]*?\"\"\""
        ],
        SectionType.IMPLEMENTATION: [
            r"#+\s*Implementation:?",
            r"#+\s*Code:?",
            r"/\*+\s*Implementation:?\s*\*+/",
            r"//+\s*Implementation:?",
            r"\"\"\"[\s\S]*?Implementation:?[\s\S]*?\"\"\""
        ],
        SectionType.TESTING: [
            r"#+\s*Testing:?",
            r"#+\s*Tests:?",
            r"/\*+\s*Testing:?\s*\*+/",
            r"//+\s*Testing:?",
            r"\"\"\"[\s\S]*?Testing:?[\s\S]*?\"\"\""
        ],
        SectionType.DOCUMENTATION: [
            r"#+\s*Documentation:?",
            r"/\*+\s*Documentation:?\s*\*+/",
            r"//+\s*Documentation:?",
            r"\"\"\"[\s\S]*?Documentation:?[\s\S]*?\"\"\""
        ]
    }

    def __init__(self, custom_markers: Optional[Dict[SectionType, List[str]]] = None):
        """
        Initialize the CodeDropExtractor with optional custom section markers.

        Args:
            custom_markers: Optional dictionary mapping SectionType to regex patterns
        """
        self.markers = self.DEFAULT_MARKERS.copy()
        if custom_markers:
            for section_type, patterns in custom_markers.items():
                if section_type in self.markers:
                    self.markers[section_type].extend(patterns)

    def extract_from_file(self, file_path: str) -> Dict[SectionType, str]:
        """
        Extract sections from a CodeDrop file.

        Args:
            file_path: Path to the CodeDrop file

        Returns:
            Dictionary mapping section types to their content

        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file doesn't contain valid CodeDrop sections
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"CodeDrop file not found: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract the base name from the file path for documentation
        self.source_file = os.path.basename(file_path)
        self.component_name = os.path.splitext(self.source_file)[0]

        return self.extract_from_string(content)

    def extract_from_string(self, content: str, component_name: str = "component") -> Dict[SectionType, str]:
        """
        Extract sections from a CodeDrop string.

        Args:
            content: String containing the CodeDrop content
            component_name: Name to use for the component in documentation

        Returns:
            Dictionary mapping section types to their content

        Raises:
            ValueError: If the content doesn't contain valid CodeDrop sections
        """
        # Store component name for documentation
        self.component_name = component_name
        self.source_file = "string input"

        # Find all section markers and their positions
        sections = []
        for section_type, patterns in self.markers.items():
            for pattern in patterns:
                for match in re.finditer(pattern, content, re.IGNORECASE):
                    sections.append((match.start(), section_type, match.group()))

        # Sort sections by their position in the file
        sections.sort()

        if not sections:
            raise ValueError("No CodeDrop sections found in the content")

        # Extract content between section markers
        result = {}
        for i, (pos, section_type, marker) in enumerate(sections):
            # Find the end of this section (start of next section or end of file)
            end_pos = len(content)
            if i < len(sections) - 1:
                end_pos = sections[i + 1][0]

            # Extract section content (skip the marker itself)
            marker_end = pos + len(marker)
            section_content = content[marker_end:end_pos].strip()

            # For implementation and testing sections, extract code from code blocks
            if section_type in [SectionType.IMPLEMENTATION, SectionType.TESTING]:
                section_content = self._extract_code_from_markdown(section_content)

            # For other sections, keep as-is (they're already in markdown format)
            result[section_type] = section_content

        # Validate that we have the required sections
        missing_sections = {SectionType.REQUIREMENTS, SectionType.DESIGN, SectionType.IMPLEMENTATION} - set(result.keys())
        if missing_sections:
            missing = ", ".join(s.value for s in missing_sections)
            print(f"Warning: Missing sections in CodeDrop: {missing}")

        return result

    def _extract_code_from_markdown(self, content: str) -> str:
        """
        Extract code from markdown code blocks.

        Args:
            content: Markdown content with code blocks

        Returns:
            Extracted code without the markdown code block syntax
        """
        # Look for code blocks with language specifier
        code_block_pattern = r'```(?:\w+)?\n([\s\S]*?)\n```'
        matches = re.findall(code_block_pattern, content)

        if matches:
            # Join all code blocks if multiple are found
            return '\n\n'.join(matches)

        # If no code blocks found, return the original content
        return content

    def save_sections_to_files(self, sections: Dict[SectionType, str],
                            base_path: str, base_name: str = None) -> Dict[SectionType, str]:
        """
        Save extracted sections to separate files with documentation headers.

        Args:
            sections: Dictionary of sections from extract_from_string/file
            base_path: Directory to save the files
            base_name: Base filename to use (without extension)

        Returns:
            Dictionary mapping section types to file paths

        Raises:
            IOError: If files cannot be written
        """
        os.makedirs(base_path, exist_ok=True)

        if base_name is None:
            base_name = self.component_name

        file_paths = {}
        extensions = {
            SectionType.REQUIREMENTS: "md",
            SectionType.DESIGN: "md",
            SectionType.DOCUMENTATION: "md",
            SectionType.IMPLEMENTATION: self._guess_extension(sections.get(SectionType.IMPLEMENTATION, "")),
            SectionType.TESTING: self._guess_extension(sections.get(SectionType.TESTING, ""))
        }

        for section_type, content in sections.items():
            if section_type == SectionType.UNKNOWN:
                continue

            ext = extensions.get(section_type, "txt")
            file_name = f"{base_name}_{section_type.value}.{ext}"
            file_path = os.path.join(base_path, file_name)

            # Add documentation header based on file type
            documented_content = self._add_documentation_header(
                content,
                section_type,
                base_name,
                ext
            )

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(documented_content)

            file_paths[section_type] = file_path

        return file_paths

    def extract_implementation(self, content: str) -> str:
        """
        Extract only the implementation section from a CodeDrop.

        Args:
            content: String containing the CodeDrop content

        Returns:
            The implementation code as a string

        Raises:
            ValueError: If no implementation section is found
        """
        sections = self.extract_from_string(content)
        if SectionType.IMPLEMENTATION not in sections:
            raise ValueError("No implementation section found in the CodeDrop")

        return sections[SectionType.IMPLEMENTATION]


    def _add_documentation_header(self, content: str, section_type: SectionType,
                                 component_name: str, extension: str) -> str:
        """
        Add appropriate documentation header to the content based on file type.

        Args:
            content: The section content
            section_type: Type of section
            component_name: Name of the component
            extension: File extension

        Returns:
            Content with documentation header
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if extension == "py":
            header = f'''"""
{component_name.replace('_', ' ').title()} - {section_type.value.title()}

Generated from CodeDrop: {self.source_file}
Section: {section_type.value}
Generated on: {timestamp}
"""

'''
        elif extension == "js":
            header = f'''/**
 * {component_name.replace('_', ' ').title()} - {section_type.value.title()}
 *
 * Generated from CodeDrop: {self.source_file}
 * Section: {section_type.value}
 * Generated on: {timestamp}
 */

'''
        elif extension in ["c", "cpp", "java"]:
            header = f'''/**
 * {component_name.replace('_', ' ').title()} - {section_type.value.title()}
 *
 * Generated from CodeDrop: {self.source_file}
 * Section: {section_type.value}
 * Generated on: {timestamp}
 */

'''
        elif extension == "md":
            header = f'''# {component_name.replace('_', ' ').title()} - {section_type.value.title()}

*Generated from CodeDrop: {self.source_file}*
*Section: {section_type.value}*
*Generated on: {timestamp}*
---
'''
        else:
            header = f'''// {component_name.replace('_', ' ').title()} - {section_type.value.title()}
// Generated from CodeDrop: {self.source_file}
// Section: {section_type.value}
// Generated on: {timestamp}

'''

        return header + content

    def _guess_extension(self, content: str) -> str:
        """
        Guess the file extension based on content.

        Args:
            content: The content to analyze

        Returns:
            A file extension (without the dot)
        """
        # Simple heuristics to guess the language
        if re.search(r'def\s+\w+\s*\(', content) or 'import ' in content:
            return 'py'
        elif re.search(r'function\s+\w+\s*\(', content) or 'console.log' in content:
            return 'js'
        elif re.search(r'public\s+class', content) or re.search(r'public\s+static\s+void\s+main', content):
            return 'java'
        elif '#include' in content or re.search(r'int\s+main\s*\(', content):
            return 'c' if not re.search(r'std::', content) else 'cpp'
        else:
            return 'txt'

# Testing
def run_tests():
    """Run unit tests for the CodeDropExtractor."""
    # Test data
    test_code_drop = """
    # Fibonacci Generator

    ## Requirements:
    - Generate Fibonacci numbers in sequence
    - Support arbitrary sequence length

    ## Design:
    - Use iterative approach
    - Return as a list

    ## Implementation:
    def generate_fibonacci(count):
        if count < 0:
            raise ValueError("Count cannot be negative")

        fibonacci = [0] if count > 0 else []
        if count > 1:
            fibonacci.append(1)

        for i in range(2, count):
            fibonacci.append(fibonacci[i-1] + fibonacci[i-2])

        return fibonacci

    ## Testing:
    assert generate_fibonacci(5) == [0, 1, 1, 2, 3]
    """

    # Create extractor
    extractor = CodeDropExtractor()

    # Test extraction
    sections = extractor.extract_from_string(test_code_drop, "fibonacci_generator")

    # Verify all sections are extracted
    assert SectionType.REQUIREMENTS in sections
    assert SectionType.DESIGN in sections
    assert SectionType.IMPLEMENTATION in sections
    assert SectionType.TESTING in sections

    # Verify content
    assert "Generate Fibonacci numbers" in sections[SectionType.REQUIREMENTS]
    assert "Use iterative approach" in sections[SectionType.DESIGN]
    assert "def generate_fibonacci" in sections[SectionType.IMPLEMENTATION]
    assert "assert generate_fibonacci" in sections[SectionType.TESTING]

    # Test implementation extraction
    impl = extractor.extract_implementation(test_code_drop)
    assert "def generate_fibonacci" in impl

    print("All tests passed!")

# Example usage
if __name__ == "__main__":
    import sys

    run_tests()

    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        try:
            extractor = CodeDropExtractor()
            sections = extractor.extract_from_file(file_path)

            # Get output directory (default to current directory)
            output_dir = "."
            if len(sys.argv) > 2:
                output_dir = sys.argv[2]

            # Get base name from file
            base_name = os.path.splitext(os.path.basename(file_path))[0]

            # Save sections to files
            file_paths = extractor.save_sections_to_files(sections, output_dir, base_name)

            print(f"Extracted {len(sections)} sections from {file_path}")
            for section_type, path in file_paths.items():
                print(f"  - {section_type.value}: {path}")

        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            sys.exit(1)
    else:
        print("Usage: python code_drop_extractor.py <code_drop_file> [output_directory]")
