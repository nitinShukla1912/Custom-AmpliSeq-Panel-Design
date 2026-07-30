#!/usr/bin/env python3
"""
Extract the longest sequence from each FASTA file.
Files with only one sequence are kept as-is.
Output files are saved with .longest.fa suffix.
"""

import os
import sys
from pathlib import Path

def read_fasta(filename):
    """
    Read a FASTA file and return a list of (header, sequence) tuples.
    """
    sequences = []
    current_header = None
    current_seq = []
    
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('>'):
                # Save previous sequence if exists
                if current_header is not None:
                    sequences.append((current_header, ''.join(current_seq)))
                # Start new sequence
                current_header = line
                current_seq = []
            else:
                current_seq.append(line)
        
        # Save last sequence
        if current_header is not None:
            sequences.append((current_header, ''.join(current_seq)))
    
    return sequences

def write_fasta(filename, header, sequence):
    """
    Write a single sequence to a FASTA file.
    """
    with open(filename, 'w') as f:
        f.write(f"{header}\n")
        # Write sequence in lines of 80 characters
        for i in range(0, len(sequence), 80):
            f.write(f"{sequence[i:i+80]}\n")

def get_longest_sequence(sequences):
    """
    Return the sequence with the longest length.
    """
    if not sequences:
        return None, None
    
    longest = max(sequences, key=lambda x: len(x[1]))
    return longest

def process_fasta_files(input_dir, output_dir=None):
    """
    Process all .fa files in the input directory.
    Extract longest sequence from each file.
    """
    if output_dir is None:
        output_dir = input_dir
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Find all .fa files
    fasta_files = list(Path(input_dir).glob('*.fa'))
    
    if not fasta_files:
        print(f"No .fa files found in {input_dir}")
        return
    
    print(f"Found {len(fasta_files)} FASTA files")
    print("=" * 80)
    
    stats = {
        'total': 0,
        'single_seq': 0,
        'multiple_seq': 0,
        'processed': 0,
        'errors': 0
    }
    
    for fasta_file in sorted(fasta_files):
        stats['total'] += 1
        filename = fasta_file.name
        
        try:
            # Read all sequences from the file
            sequences = read_fasta(fasta_file)
            
            if not sequences:
                print(f"⚠️  {filename}: Empty file, skipping")
                stats['errors'] += 1
                continue
            
            num_seqs = len(sequences)
            
            # Determine output filename
            output_file = Path(output_dir) / filename.replace('.fa', '.longest.fa')
            
            if num_seqs == 1:
                # File has only one sequence, keep as-is
                header, sequence = sequences[0]
                write_fasta(output_file, header, sequence)
                stats['single_seq'] += 1
                print(f"✓ {filename}: 1 sequence (length: {len(sequence)}) -> kept as-is")
            else:
                # File has multiple sequences, extract longest
                longest_header, longest_seq = get_longest_sequence(sequences)
                write_fasta(output_file, longest_header, longest_seq)
                stats['multiple_seq'] += 1
                
                # Show info about all sequences
                seq_lengths = [len(seq) for _, seq in sequences]
                print(f"✓ {filename}: {num_seqs} sequences found")
                print(f"  Lengths: {sorted(seq_lengths, reverse=True)}")
                print(f"  Longest: {len(longest_seq)} bp -> extracted")
            
            stats['processed'] += 1
            
        except Exception as e:
            print(f"❌ {filename}: Error - {str(e)}")
            stats['errors'] += 1
    
    print("=" * 80)
    print("\nSummary:")
    print(f"  Total files found: {stats['total']}")
    print(f"  Successfully processed: {stats['processed']}")
    print(f"    - Single sequence files: {stats['single_seq']}")
    print(f"    - Multiple sequence files: {stats['multiple_seq']}")
    print(f"  Errors: {stats['errors']}")
    print(f"\nOutput files saved with '.longest.fa' suffix in: {output_dir}")

if __name__ == "__main__":
    # Get input directory from command line or use current directory
    if len(sys.argv) > 1:
        input_dir = sys.argv[1]
    else:
        input_dir = "."
    
    # Get output directory from command line (optional)
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
    else:
        output_dir = None  # Same as input directory
    
    print(f"Processing FASTA files in: {input_dir}")
    if output_dir:
        print(f"Output directory: {output_dir}")
    print()
    
    process_fasta_files(input_dir, output_dir)
