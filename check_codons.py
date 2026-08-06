#!/usr/bin/env python3
"""
Script to check start and stop codons in FASTA sequences
Highlights sequences with incorrect codons
"""

import sys
import os
from pathlib import Path

# Standard genetic code
STANDARD_START_CODONS = {'ATG'}
ALTERNATIVE_START_CODONS = {'GTG', 'TTG', 'CTG'}  # Some bacteria use these
STOP_CODONS = {'TAA', 'TAG', 'TGA'}

def parse_fasta(fasta_file):
    """Parse FASTA file and return sequences"""
    sequences = {}
    current_id = None
    current_seq = []
    
    with open(fasta_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('>'):
                if current_id:
                    sequences[current_id] = ''.join(current_seq)
                current_id = line[1:]  # Remove '>'
                current_seq = []
            else:
                current_seq.append(line.upper())
        
        # Don't forget the last sequence
        if current_id:
            sequences[current_id] = ''.join(current_seq)
    
    return sequences

def check_codons(sequences, allow_alternative_start=False):
    """Check start and stop codons in sequences"""
    results = []
    
    for seq_id, sequence in sequences.items():
        seq_len = len(sequence)
        
        # Skip if sequence is too short
        if seq_len < 6:
            results.append({
                'id': seq_id,
                'length': seq_len,
                'start_codon': 'N/A',
                'stop_codon': 'N/A',
                'start_ok': False,
                'stop_ok': False,
                'issue': 'Sequence too short (< 6 bp)',
                'sequence': sequence
            })
            continue
        
        # Get start and stop codons
        start_codon = sequence[:3]
        stop_codon = sequence[-3:]
        
        # Check start codon
        if allow_alternative_start:
            start_ok = start_codon in (STANDARD_START_CODONS | ALTERNATIVE_START_CODONS)
            codon_type = 'standard/alternative'
        else:
            start_ok = start_codon in STANDARD_START_CODONS
            codon_type = 'standard (ATG)'
        
        # Check stop codon
        stop_ok = stop_codon in STOP_CODONS
        
        # Determine issues
        issues = []
        if not start_ok:
            issues.append(f'Invalid start codon: {start_codon} (expected {codon_type})')
        if not stop_ok:
            issues.append(f'Invalid stop codon: {stop_codon} (expected TAA/TAG/TGA)')
        
        results.append({
            'id': seq_id,
            'length': seq_len,
            'start_codon': start_codon,
            'stop_codon': stop_codon,
            'start_ok': start_ok,
            'stop_ok': stop_ok,
            'issue': '; '.join(issues) if issues else 'OK',
            'sequence': sequence
        })
    
    return results

def print_report(results, output_file=None, show_sequences=False):
    """Print detailed report"""
    
    # Prepare output
    lines = []
    lines.append("=" * 100)
    lines.append("CODON CHECK REPORT")
    lines.append("=" * 100)
    lines.append("")
    
    # Summary statistics
    total = len(results)
    correct_both = sum(1 for r in results if r['start_ok'] and r['stop_ok'])
    incorrect_start = sum(1 for r in results if not r['start_ok'])
    incorrect_stop = sum(1 for r in results if not r['stop_ok'])
    incorrect_both = sum(1 for r in results if not r['start_ok'] and not r['stop_ok'])
    
    lines.append("SUMMARY:")
    lines.append(f"  Total sequences: {total}")
    lines.append(f"  Correct start AND stop codons: {correct_both} ({correct_both/total*100:.1f}%)")
    lines.append(f"  Incorrect start codon: {incorrect_start} ({incorrect_start/total*100:.1f}%)")
    lines.append(f"  Incorrect stop codon: {incorrect_stop} ({incorrect_stop/total*100:.1f}%)")
    lines.append(f"  Incorrect both: {incorrect_both} ({incorrect_both/total*100:.1f}%)")
    lines.append("")
    lines.append("=" * 100)
    lines.append("")
    
    # Detailed results
    lines.append("DETAILED RESULTS:")
    lines.append("")
    
    # First show problematic sequences
    problematic = [r for r in results if not r['start_ok'] or not r['stop_ok']]
    if problematic:
        lines.append("*** SEQUENCES WITH ISSUES ***")
        lines.append("")
        for r in problematic:
            lines.append(f"Sequence ID: {r['id']}")
            lines.append(f"  Length: {r['length']} bp")
            lines.append(f"  Start codon: {r['start_codon']} {'✓' if r['start_ok'] else '✗ INCORRECT'}")
            lines.append(f"  Stop codon:  {r['stop_codon']} {'✓' if r['stop_ok'] else '✗ INCORRECT'}")
            lines.append(f"  Issue: {r['issue']}")
            if show_sequences:
                lines.append(f"  First 30bp: {r['sequence'][:30]}...")
                lines.append(f"  Last 30bp:  ...{r['sequence'][-30:]}")
            lines.append("")
    
    # Then show correct sequences
    correct = [r for r in results if r['start_ok'] and r['stop_ok']]
    if correct:
        lines.append("*** CORRECT SEQUENCES ***")
        lines.append("")
        for r in correct:
            lines.append(f"Sequence ID: {r['id']}")
            lines.append(f"  Length: {r['length']} bp | Start: {r['start_codon']} ✓ | Stop: {r['stop_codon']} ✓")
            lines.append("")
    
    # Print to console
    report = '\n'.join(lines)
    print(report)
    
    # Save to file if specified
    if output_file:
        with open(output_file, 'w') as f:
            f.write(report)
        print(f"\nReport saved to: {output_file}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python check_codons.py <fasta_file> [options]")
        print("\nOptions:")
        print("  --allow-alt-start    Allow alternative start codons (GTG, TTG, CTG)")
        print("  --show-sequences     Show sequence snippets in report")
        print("  --output <file>      Save report to file")
        print("\nExample:")
        print("  python check_codons.py sequences.fasta")
        print("  python check_codons.py sequences.fasta --allow-alt-start --output report.txt")
        sys.exit(1)
    
    fasta_file = sys.argv[1]
    
    # Check if file exists
    if not os.path.exists(fasta_file):
        print(f"Error: File '{fasta_file}' not found!")
        sys.exit(1)
    
    # Parse options
    allow_alt_start = '--allow-alt-start' in sys.argv
    show_sequences = '--show-sequences' in sys.argv
    output_file = None
    
    if '--output' in sys.argv:
        idx = sys.argv.index('--output')
        if idx + 1 < len(sys.argv):
            output_file = sys.argv[idx + 1]
    
    # Parse FASTA file
    print(f"Parsing FASTA file: {fasta_file}")
    sequences = parse_fasta(fasta_file)
    print(f"Found {len(sequences)} sequences")
    print("")
    
    # Check codons
    results = check_codons(sequences, allow_alt_start=allow_alt_start)
    
    # Print report
    print_report(results, output_file=output_file, show_sequences=show_sequences)

if __name__ == '__main__':
    main()
