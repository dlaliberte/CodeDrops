# Fibonacci Generator - Documentation

*Generated from CodeDrop: string input*
*Section: documentation*
*Generated on: 2025-04-29 08:08:41*
---
### generate_fibonacci

Generate a list containing the Fibonacci sequence.

The Fibonacci sequence starts with 0 and 1, where each subsequent number
is the sum of the two preceding ones: 0, 1, 1, 2, 3, 5, 8, 13, ...

**Parameters:**
- `count`: Number of Fibonacci numbers to generate

**Returns:**
- List of Fibonacci numbers

**Raises:**
- `ValueError`: If count is negative

**Examples:**
```python
>>> generate_fibonacci(5)
[0, 1, 1, 2, 3]

>>> generate_fibonacci(0)
[]
```