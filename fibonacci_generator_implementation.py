"""
Fibonacci Generator - Implementation

Generated from CodeDrop: string input
Section: implementation
Generated on: 2025-04-29 08:08:41
"""

def generate_fibonacci(count):
    """
    Generate a list containing the Fibonacci sequence.

    Args:
        count: Number of Fibonacci numbers to generate

    Returns:
        List of Fibonacci numbers

    Raises:
        ValueError: If count is negative
    """
    if count < 0:
        raise ValueError("Count cannot be negative")

    if count == 0:
        return []

    # Initialize with first two Fibonacci numbers
    fibonacci = [0]

    if count > 1:
        fibonacci.append(1)

    # Generate subsequent numbers
    for i in range(2, count):
        fibonacci.append(fibonacci[i-1] + fibonacci[i-2])

    return fibonacci