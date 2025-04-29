
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
