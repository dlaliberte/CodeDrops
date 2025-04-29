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
import sys
from enum import Enum
from bs4 import BeautifulSoup
import argparse
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime

class SectionType(str, Enum):
    """Enumeration of possible sections in a CodeDrop."""
    REQUIREMENTS = "requirements"
    DESIGN = "design"
    IMPLEMENTATION = "implementation"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    UNKNOWN = "unknown"
    HTML_SECTIONS = "html_sections"  # Special type for HTML section mapping

class CodeDropExtractor:
    """
    Extracts different sections from a CodeDrop file.

    A CodeDrop file contains requirements, design, implementation, and testing
    all in a single file. This class parses such files and extracts each section.
    """

    # Default section markers (can be customized)
    DEFAULT_MARKERS = {
        SectionType.REQUIREMENTS: [
            r"^#+\s*Requirements:?",
            r"^#+\s*Specification:?",
            r"/\*+\s*Requirements:?\s*\*+/",
            r"//+\s*Requirements:?",
            r"\"\"\"[\s\S]*?Requirements:?[\s\S]*?\"\"\""
        ],
        SectionType.DESIGN: [
            r"^#+\s*Design:?",
            r"^#+\s*Architecture:?",
            r"/\*+\s*Design:?\s*\*+/",
            r"//+\s*Design:?",
            r"\"\"\"[\s\S]*?Design:?[\s\S]*?\"\"\""
        ],
        SectionType.IMPLEMENTATION: [
            r"^#+\s*Implementation:?",
            r"^#+\s*Code:?",
            r"/\*+\s*Implementation:?\s*\*+/",
            r"//+\s*Implementation:?",
            r"\"\"\"[\s\S]*?Implementation:?[\s\S]*?\"\"\""
        ],
        SectionType.TESTING: [
            r"^#+\s*Testing:?",
            r"^#+\s*Tests:?",
            r"/\*+\s*Testing:?\s*\*+/",
            r"//+\s*Testing:?",
            r"\"\"\"[\s\S]*?Testing:?[\s\S]*?\"\"\""
        ],
        SectionType.DOCUMENTATION: [
            r"^#+\s*Documentation:?",
            r"/\*+\s*Documentation:?\s*\*+/",
            r"//+\s*Documentation:?",
            r"\"\"\"[\s\S]*?Documentation:?[\s\S]*?\"\"\""
        ],
        # HTML section IDs
        SectionType.HTML_SECTIONS: {
            "requirements": SectionType.REQUIREMENTS,
            "design": SectionType.DESIGN,
            "implementation": SectionType.IMPLEMENTATION,
            "testing": SectionType.TESTING,
            "documentation": SectionType.DOCUMENTATION
        }
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
        self.html_sections = self.DEFAULT_MARKERS.pop(SectionType.HTML_SECTIONS)

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

        # Check if this is an HTML file
        if file_path.lower().endswith('.html'):
            return self.extract_from_html(content)

        return self.extract_from_string(content)

    def extract_from_html(self, content: str) -> Dict[SectionType, str]:
        """
        Extract sections from an HTML CodeDrop.

        Args:
            content: String containing the HTML CodeDrop content

        Returns:
            Dictionary mapping section types to their content
        """
        result = {}

        try:
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')

            # Find all section divs
            for section_div in soup.find_all('div', class_='section'):
                # Get section ID
                section_id = section_div.get('id')
                if not section_id:
                    continue

                # Map section ID to SectionType
                if section_id in self.html_sections:
                    section_type = self.html_sections[section_id]

                    # Extract content based on section type
                    if section_type in [SectionType.IMPLEMENTATION, SectionType.TESTING]:
                        # For code sections, extract from <pre><code> elements
                        code_elements = section_div.find_all('code')
                        if code_elements:
                            section_content = '\n\n'.join(code.get_text() for code in code_elements)
                        else:
                            section_content = section_div.get_text().strip()
                    else:
                        # For other sections, get all text
                        # Skip the heading
                        heading = section_div.find(['h1', 'h2', 'h3'])
                        if heading:
                            heading.extract()
                        section_content = section_div.get_text().strip()

                    result[section_type] = section_content

        except Exception as e:
            print(f"Warning: Error parsing HTML: {e}")
            # Fall back to string extraction
            return self.extract_from_string(content)

        # Validate that we have the required sections
        missing_sections = set([SectionType.REQUIREMENTS, SectionType.DESIGN, SectionType.IMPLEMENTATION]) - set(result.keys())
        if missing_sections:
            missing = ", ".join(s.value for s in missing_sections)
            print(f"Warning: Missing sections in HTML CodeDrop: {missing}")

        return result

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
        missing_sections = set([SectionType.REQUIREMENTS, SectionType.DESIGN, SectionType.IMPLEMENTATION]) - set(result.keys())
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
        # Use a more robust regex approach for extracting code blocks

        # Pattern 1: Standard markdown code blocks with language specifier
        pattern1 = r'(?:python|js|java|cpp|c)?\s*\n([\s\S]*?)\n\s*'
        matches1 = re.findall(pattern1, content)

        if matches1:
            return '\n\n'.join(matches1)

        # Pattern 2: More lenient pattern for code blocks
        pattern2 = r'\s*([\s\S]*?)\s*'
        matches2 = re.findall(pattern2, content)

        if matches2:
            return '\n\n'.join(matches2)

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

def main():
    """Command line interface for the CodeDrop extractor."""
    parser = argparse.ArgumentParser(description='Extract sections from CodeDrop files')
    parser.add_argument('file', help='Path to the CodeDrop file')
    parser.add_argument('-o', '--output', help='Output directory for extracted sections (default: same directory as the code drop)', required=True)
    parser.add_argument('-n', '--name', help='Base name for output files (default: derived from input file)')
    parser.add_argument('--subdirs', action='store_true',
                        help='Create subdirectories for each section type (e.g., requirements/, implementation/)')
    parser.add_argument('--html', action='store_true', help='Force HTML parsing even for non-HTML files')
    parser.add_argument('--debug', action='store_true', help='Print debug information')
    parser.add_argument('-s', '--section', choices=[s.value for s in SectionType if s != SectionType.UNKNOWN],
                        help='Extract only a specific section')
    args = parser.parse_args()

    try:
        extractor = CodeDropExtractor()

        # Print the file we're processing to help debug
        if args.debug:
            print(f"Processing CodeDrop file: {os.path.abspath(args.file)}")

        # Extract all sections - use HTML parsing if specified or if file has .html extension
        if args.html or args.file.lower().endswith('.html'):
            with open(args.file, 'r', encoding='utf-8') as f:
                content = f.read()
            sections = extractor.extract_from_html(content)
        else:
            sections = extractor.extract_from_file(args.file)

        # Debug output
        if args.debug:
            print("\nExtracted sections:")
            for section_type, content in sections.items():
                print(f"\n--- {section_type.value} ---")
                print(content[:200] + "..." if len(content) > 200 else content)

        # If no specific section is requested, save all sections to files
        if not args.section:
            # Get base name from file or argument
            base_name = args.name or os.path.splitext(os.path.basename(args.file))[0]

            # Create subdirectories if requested
            if args.subdirs:
                section_dirs = {
                    section_type: os.path.join(args.output, section_type.value)
                    for section_type in SectionType if section_type != SectionType.UNKNOWN
                }
                for dir_path in section_dirs.values():
                    os.makedirs(dir_path, exist_ok=True)

                file_paths = {}
                for section_type, content in sections.items():
                    if section_type in section_dirs:
                        path = extractor.save_sections_to_files(
                            {section_type: content}, section_dirs[section_type], base_name
                        )
                        file_paths.update(path)
            else:
                # Save all sections to a single directory
                file_paths = extractor.save_sections_to_files(sections, args.output, base_name)

            if args.debug:
                print("\nSaved sections to files:")
                for section_type, path in file_paths.items():
                    print(f"  - {section_type.value}: {path}")
        else:
            # Output only the requested section
            section_type = SectionType(args.section)
            if section_type in sections:
                print(sections[section_type])
            else:
                print(f"Section '{args.section}' not found in {args.file}")
                sys.exit(1)

    except Exception as e:
        print(f"Error processing {args.file}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
