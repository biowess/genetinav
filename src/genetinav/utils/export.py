"""Export utilities for GenetiNav."""

def format_fasta(header: str, sequence: str, line_length: int = 60) -> str:
    """Format a sequence into a valid FASTA format.
    
    Args:
        header: The header string (without the leading '>').
        sequence: The sequence to format.
        line_length: The maximum length of sequence lines.
    
    Returns:
        A fully formatted FASTA string.
    """
    seq = sequence.upper()
    lines = [f">{header}"]
    lines.extend([seq[i:i + line_length] for i in range(0, len(seq), line_length)])
    return "\n".join(lines) + "\n"
