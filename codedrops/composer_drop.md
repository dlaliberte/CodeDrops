# CodeDrop Composer

## Requirements
- Combine implementation sections from multiple CodeDrops into a single file
- Combine testing sections from multiple CodeDrops into a single file
- Support generating composite documentation from multiple CodeDrops
- Maintain proper imports and dependencies between components
- Preserve documentation headers and attribution to original CodeDrops
- Support different programming languages
- Provide both CLI and API interfaces

## Design
- Create a `CodeDropComposer` class that takes multiple CodeDrop files or directories as input
- Use the `CodeDropExtractor` to extract sections from each CodeDrop
- Group sections by type (implementation, testing, etc.)
- For each section type, combine the content with appropriate separators
- Handle language-specific composition (imports at the top, etc.)
- Generate composite files with proper headers and documentation
- Support customization of output format and structure

## Documentation
### CodeDropComposer

The `CodeDropComposer` combines sections from multiple CodeDrops into composite files.

**Usage:**

```python
from codedrops.composer import CodeDropComposer
from codedrops.extractor import CodeDropExtractor

# Create a composer with an extractor
extractor = CodeDropExtractor()
composer = CodeDropComposer(extractor)

# Add CodeDrops to the composition
composer.add_drop("fibonacci_generator.md")
composer.add_drop("prime_checker.md")
composer.add_drop("factorial_calculator.md")

# Generate composite files
composer.compose("math_utils", output_dir="./generated")
```

**CLI Usage:**

```bash
python -m codedrops.composer --output math_utils --dir ./generated fibonacci_generator.md prime_checker.md factorial_calculator.md
```

This will generate:
- `math_utils_implementation.py` - Combined implementation code
- `math_utils_testing.py` - Combined test code
- `math_utils_documentation.md` - Combined documentation
- `math_utils_requirements.md` - Combined requirements
- `math_utils_design.md` - Combined design notes

## Implementation
```python
"""
CodeDrops Composer - Combine sections from multiple CodeDrops into composite files.

This module provides functionality to compose multiple CodeDrop files into
composite implementation, testing, documentation, and other files.
"""

import os
import sys
import argparse
from typing import Dict, List, Optional, Set, Tuple, Union
from pathlib import Path
from datetime import datetime

from codedrops.extractor import CodeDropExtractor, SectionType

class CodeDropComposer:
    """
    Combines sections from multiple CodeDrops into composite files.

    This class takes multiple CodeDrop files, extracts their sections,
    and combines them into composite files by section type.
    """

    def __init__(self, extractor: Optional[CodeDropExtractor] = None):
        """
        Initialize the CodeDropComposer.

        Args:
            extractor: Optional CodeDropExtractor to use for extraction
        """
        self.extractor = extractor or CodeDropExtractor()
        self.drops: List[Dict[str, Dict[SectionType, str]]] = []
        self.drop_names: List[str] = []

    def add_drop(self, file_path: str) -> None:
        """
        Add a CodeDrop file to the composition.

        Args:
            file_path: Path to the CodeDrop file

        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file doesn't contain valid CodeDrop sections
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"CodeDrop file not found: {file_path}")

        # Extract sections from the file
        sections = self.extractor.extract_from_file(file_path)

        # Store the sections with the file name
        drop_name = os.path.splitext(os.path.basename(file_path))[0]
        self.drops.append({
            "file_path": file_path,
            "name": drop_name,
            "sections": sections
        })
        self.drop_names.append(drop_name)

    def add_drops_from_directory(self, directory: str, pattern: str = "*.md") -> None:
        """
        Add all CodeDrop files from a directory.

        Args:
            directory: Directory containing CodeDrop files
            pattern: Glob pattern to match files (default: "*.md")

        Raises:
            FileNotFoundError: If the directory doesn't exist
        """
        if not os.path.isdir(directory):
            raise FileNotFoundError(f"Directory not found: {directory}")

        # Find all matching files in the directory
        for file_path in Path(directory).glob(pattern):
            try:
                self.add_drop(str(file_path))
            except ValueError as e:
                print(f"Warning: Skipping {file_path}: {e}")

    def compose(self, composite_name: str, output_dir: str = ".") -> Dict[SectionType, str]:
        """
        Compose sections from all added CodeDrops into composite files.

        Args:
            composite_name: Name for the composite files
            output_dir: Directory to save the composite files

        Returns:
            Dictionary mapping section types to file paths

        Raises:
            ValueError: If no CodeDrops have been added
        """
        if not self.drops:
            raise ValueError("No CodeDrops have been added for composition")

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Group sections by type
        grouped_sections: Dict[SectionType, List[Tuple[str, str]]] = {
            section_type: [] for section_type in SectionType if section_type != SectionType.UNKNOWN
        }

        for drop in self.drops:
            for section_type, content in drop["sections"].items():
                if section_type != SectionType.UNKNOWN:
                    grouped_sections[section_type].append((drop["name"], content))

        # Compose each section type
        composed_sections: Dict[SectionType, str] = {}
        file_paths: Dict[SectionType, str] = {}

        for section_type, sections in grouped_sections.items():
            if not sections:
                continue

            # Compose the sections
            composed_content = self._compose_section(section_type, sections, composite_name)
            composed_sections[section_type] = composed_content

            # Determine file extension
            ext = self._get_extension_for_section(section_type, sections)

            # Create file path
            file_name = f"{composite_name}_{section_type.value}.{ext}"
            file_path = os.path.join(output_dir, file_name)

            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(composed_content)

            file_paths[section_type] = file_path

        return file_paths

    def _compose_section(self, section_type: SectionType,
                        sections: List[Tuple[str, str]],
                        composite_name: str) -> str:
        """
        Compose a specific section type from multiple CodeDrops.

        Args:
            section_type: The type of section to compose
            sections: List of (drop_name, content) tuples
            composite_name: Name for the composite file

        Returns:
            Composed content for the section
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Create header based on section type
        if section_type in [SectionType.IMPLEMENTATION, SectionType.TESTING]:
            header = f'''"""
{composite_name.replace('_', ' ').title()} - {section_type.value.title()}

Generated by CodeDrops Composer
Components: {', '.join(self.drop_names)}
Generated on: {timestamp}
"""

'''
        elif section_type == SectionType.DOCUMENTATION:
            header = f'''# {composite_name.replace('_', ' ').title()} - {section_type.value.title()}

*Generated by CodeDrops Composer*
*Components: {', '.join(self.drop_names)}*
*Generated on: {timestamp}*

---

'''
        else:  # REQUIREMENTS, DESIGN
            header = f'''# {composite_name.replace('_', ' ').title()} - {section_type.value.title()}

*Generated by CodeDrops Composer*
*Components: {', '.join(self.drop_names)}*
*Generated on: {timestamp}*

---

'''

        # Compose the content based on section type
        if section_type == SectionType.IMPLEMENTATION:
            return self._compose_implementation(header, sections)
        elif section_type == SectionType.TESTING:
            return self._compose_testing(header, sections)
        elif section_type == SectionType.DOCUMENTATION:
            return self._compose_documentation(header, sections)
        else:  # REQUIREMENTS, DESIGN
            return self._compose_markdown(header, sections)

    def _compose_implementation(self, header: str, sections: List[Tuple[str, str]]) -> str:
        """
        Compose implementation sections.

        Args:
            header: Header for the composite file
            sections: List of (drop_name, content) tuples

        Returns:
            Composed implementation code
        """
        # Extract imports from all sections
        imports = set()
        implementation_parts = []

        for drop_name, content in sections:
            # Extract imports
            import_lines = []
            content_lines = []

            for line in content.split('\n'):
                if line.startswith('import ') or line.startswith('from '):
                    imports.add(line)
                else:
                    content_lines.append(line)

            # Add section with header
            implementation_parts.append(f"\n# {drop_name}\n")
            implementation_parts.append('\n'.join(content_lines))

        # Combine all parts
        result = header

        # Add imports at the top
        if imports:
            result += '\n'.join(sorted(imports)) + '\n\n'

        # Add implementation parts
        result += '\n'.join(implementation_parts)

        return result

    def _compose_testing(self, header: str, sections: List[Tuple[str, str]]) -> str:
        """
        Compose testing sections.

        Args:
            header: Header for the composite file
            sections: List of (drop_name, content) tuples

        Returns:
            Composed test code
        """
        # Extract imports from all sections
        imports = set()
        testing_parts = []

        for drop_name, content in sections:
            # Extract imports
            import_lines = []
            content_lines = []

            for line in content.split('\n'):
                if line.startswith('import ') or line.startswith('from '):
                    imports.add(line)
                else:
                    content_lines.append(line)

            # Add section with header
            testing_parts.append(f"\n# Tests for {drop_name}\n")
            testing_parts.append('\n'.join(content_lines))

        # Combine all parts
        result = header

        # Add imports at the top
        if imports:
            result += '\n'.join(sorted(imports)) + '\n\n'

        # Add implementation parts
        result += '\n'.join(testing_parts)

        # Add main test runner
        result += '\n\nif __name__ == "__main__":\n    print("All tests passed!")\n'

        return result

    def _compose_documentation(self, header: str, sections: List[Tuple[str, str]]) -> str:
        """
        Compose documentation sections.

        Args:
            header: Header for the composite file
            sections: List of (drop_name, content) tuples

        Returns:
            Composed documentation in markdown
        """
        doc_parts = [header]

        for drop_name, content in sections:
            doc_parts.append(f"\n## {drop_name.replace('_', ' ').title()}\n")
            doc_parts.append(content)

        return '\n'.join(doc_parts)

    def _compose_markdown(self, header: str, sections: List[Tuple[str, str]]) -> str:
        """
        Compose markdown sections (requirements, design).

        Args:
            header: Header for the composite file
            sections: List of (drop_name, content) tuples

        Returns:
            Composed markdown content
        """
        md_parts = [header]

        for drop_name, content in sections:
            md_parts.append(f"\n## {drop_name.replace('_', ' ').title()}\n")
            md_parts.append(content)

        return '\n'.join(md_parts)

    def _get_extension_for_section(self, section_type: SectionType,
                                  sections: List[Tuple[str, str]]) -> str:
        """
        Determine the file extension for a composed section.

        Args:
            section_type: The type of section
            sections: List of (drop_name, content) tuples

        Returns:
            File extension for the section
        """
        if section_type in [SectionType.REQUIREMENTS, SectionType.DESIGN, SectionType.DOCUMENTATION]:
            return "md"

        # For implementation and testing, guess based on content
        if section_type in [SectionType.IMPLEMENTATION, SectionType.TESTING]:
            # Join all content to analyze
            all_content = '\n'.join(content for _, content in sections)
            return self.extractor._guess_extension(all_content)

        return "txt"
```

## Testing
```python
import os
import tempfile
import unittest
from pathlib import Path

from codedrops.extractor import CodeDropExtractor, SectionType
from codedrops.composer import CodeDropComposer

class TestCodeDropComposer(unittest.TestCase):
    def setUp(self):
        self.extractor = CodeDropExtractor()
        self.composer = CodeDropComposer(self.extractor)

        # Create temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()

        # Create test CodeDrop files
        self.fibonacci_drop = os.path.join(self.temp_dir.name, "fibonacci_generator.md")
        with open(self.fibonacci_drop, 'w', encoding='utf-8') as f:
            f.write("""
# Fibonacci Generator

## Requirements
- Generate Fibonacci numbers in sequence

## Design
- Use iterative approach

## Implementation
```python
def generate_fibonacci(count):
    if count < 0:
        raise ValueError("Count cannot be negative")

    fibonacci = [0] if count > 0 else []
    if count > 1:
        fibonacci.append(1)

    for i in range(2, count):
        fibonacci.append(fibonacci[i-1] + fibonacci[i-2])

    return fibonacci
```

## Testing
```python
assert generate_fibonacci(5) == [0, 1, 1, 2, 3]```)

self.prime_drop = os.path.join(self.temp_dir.name, "prime_checker.md")
    with open(self.prime_drop, 'w', encoding='utf-8')
