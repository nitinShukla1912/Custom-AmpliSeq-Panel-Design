#!/bin/bash

# Script to:
# 1. Rename FASTA sequence headers with filename
# 2. Combine all FASTA files into one
# 3. Check start and stop codons

# Configuration
INPUT_DIR="${1:-.}"  # First argument or current directory
OUTPUT_COMBINED="combined_sequences.fasta"
REPORT_FILE="codon_check_report.txt"

echo "=========================================="
echo "FASTA File Processing and Codon Checking"
echo "=========================================="
echo "Input directory: $INPUT_DIR"
echo ""

# Remove old output files if they exist
rm -f "$OUTPUT_COMBINED" "$REPORT_FILE"

# Counter for files processed
file_count=0

# Find and process all FASTA files
for fasta_file in "$INPUT_DIR"/*.fa "$INPUT_DIR"/*.fasta "$INPUT_DIR"/*.fna; do
    # Check if file exists (glob might not match anything)
    [ -f "$fasta_file" ] || continue
    
    # Extract basename and gene name
    basename=$(basename "$fasta_file")
    genename="${basename%.cdhit*}"
    genename="${genename%.fa*}"
    
    echo "Processing: $basename -> Gene: $genename"
    
    # Process the file and rename headers
    awk -v gene="$genename" '
        /^>/ {
            # Extract any existing ID after the >
            original_id = substr($0, 2)
            # Create new header with gene name
            print ">" gene "_" original_id
            next
        }
        {
            print
        }
    ' "$fasta_file" >> "$OUTPUT_COMBINED"
    
    ((file_count++))
done

if [ $file_count -eq 0 ]; then
    echo "No FASTA files found in $INPUT_DIR"
    echo "Looking for files with extensions: .fa, .fasta, .fna"
    exit 1
fi

echo ""
echo "Combined $file_count FASTA files into: $OUTPUT_COMBINED"
echo ""
echo "=========================================="
echo "Checking Start and Stop Codons"
echo "=========================================="

# Call Python script for codon checking
python3 << 'PYTHON_SCRIPT'
import sys
from collections import defaultdict

def check_codons(fasta_file, report_file):
    # Valid start and stop codons
    valid_starts = ['ATG', 'GTG', 'TTG']  # ATG is most common, GTG and TTG are alternative starts
    valid_stops = ['TAA', 'TAG', 'TGA']
    
    sequences = {}
    current_seq_id = None
    current_seq = []
    
    # Read FASTA file
    try:
        with open(fasta_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('>'):
                    # Save previous sequence
                    if current_seq_id:
                        sequences[current_seq_id] = ''.join(current_seq).upper()
                    # Start new sequence
                    current_seq_id = line[1:]  # Remove '>'
                    current_seq = []
                elif line:
                    current_seq.append(line)
            
            # Save last sequence
            if current_seq_id:
                sequences[current_seq_id] = ''.join(current_seq).upper()
    
    except FileNotFoundError:
        print(f"Error: File {fasta_file} not found")
        return
    
    # Statistics
    total_seqs = len(sequences)
    correct_both = 0
    incorrect_start = []
    incorrect_stop = []
    incorrect_both = []
    short_seqs = []
    
    # Open report file
    with open(report_file, 'w') as report:
        report.write("=" * 80 + "\n")
        report.write("CODON CHECK REPORT\n")
        report.write("=" * 80 + "\n\n")
        
        report.write(f"Total sequences analyzed: {total_seqs}\n")
        report.write(f"Valid start codons: {', '.join(valid_starts)}\n")
        report.write(f"Valid stop codons: {', '.join(valid_stops)}\n\n")
        
        # Check each sequence
        for seq_id, seq in sequences.items():
            seq_len = len(seq)
            
            # Skip sequences too short to have start and stop codons
            if seq_len < 6:
                short_seqs.append((seq_id, seq_len))
                continue
            
            # Extract start and stop codons
            start_codon = seq[:3]
            stop_codon = seq[-3:]
            
            # Check validity
            start_valid = start_codon in valid_starts
            stop_valid = stop_codon in valid_stops
            
            if start_valid and stop_valid:
                correct_both += 1
            elif not start_valid and not stop_valid:
                incorrect_both.append((seq_id, start_codon, stop_codon, seq_len))
            elif not start_valid:
                incorrect_start.append((seq_id, start_codon, seq_len))
            else:  # not stop_valid
                incorrect_stop.append((seq_id, stop_codon, seq_len))
        
        # Write summary
        report.write("=" * 80 + "\n")
        report.write("SUMMARY\n")
        report.write("=" * 80 + "\n")
        report.write(f"Sequences with correct start AND stop codons: {correct_both}\n")
        report.write(f"Sequences with incorrect start codon only: {len(incorrect_start)}\n")
        report.write(f"Sequences with incorrect stop codon only: {len(incorrect_stop)}\n")
        report.write(f"Sequences with incorrect BOTH codons: {len(incorrect_both)}\n")
        report.write(f"Sequences too short (< 6 bp): {len(short_seqs)}\n\n")
        
        # Detailed reports
        if incorrect_start:
            report.write("=" * 80 + "\n")
            report.write("SEQUENCES WITH INCORRECT START CODON\n")
            report.write("=" * 80 + "\n")
            for seq_id, start, length in incorrect_start:
                report.write(f"\n>>> {seq_id}\n")
                report.write(f"    Length: {length} bp\n")
                report.write(f"    Start codon: {start} (INCORRECT - Expected: {', '.join(valid_starts)})\n")
        
        if incorrect_stop:
            report.write("\n" + "=" * 80 + "\n")
            report.write("SEQUENCES WITH INCORRECT STOP CODON\n")
            report.write("=" * 80 + "\n")
            for seq_id, stop, length in incorrect_stop:
                report.write(f"\n>>> {seq_id}\n")
                report.write(f"    Length: {length} bp\n")
                report.write(f"    Stop codon: {stop} (INCORRECT - Expected: {', '.join(valid_stops)})\n")
        
        if incorrect_both:
            report.write("\n" + "=" * 80 + "\n")
            report.write("SEQUENCES WITH INCORRECT START AND STOP CODONS\n")
            report.write("=" * 80 + "\n")
            for seq_id, start, stop, length in incorrect_both:
                report.write(f"\n>>> {seq_id}\n")
                report.write(f"    Length: {length} bp\n")
                report.write(f"    Start codon: {start} (INCORRECT - Expected: {', '.join(valid_starts)})\n")
                report.write(f"    Stop codon: {stop} (INCORRECT - Expected: {', '.join(valid_stops)})\n")
        
        if short_seqs:
            report.write("\n" + "=" * 80 + "\n")
            report.write("SEQUENCES TOO SHORT FOR ANALYSIS\n")
            report.write("=" * 80 + "\n")
            for seq_id, length in short_seqs:
                report.write(f"\n>>> {seq_id}\n")
                report.write(f"    Length: {length} bp (Too short - need at least 6 bp)\n")
    
    # Print summary to console
    print(f"\nTotal sequences: {total_seqs}")
    print(f"✓ Correct start AND stop: {correct_both}")
    print(f"✗ Incorrect start only: {len(incorrect_start)}")
    print(f"✗ Incorrect stop only: {len(incorrect_stop)}")
    print(f"✗ Incorrect BOTH: {len(incorrect_both)}")
    print(f"⚠ Too short: {len(short_seqs)}")
    print(f"\nDetailed report written to: {report_file}")

# Run the check
check_codons('combined_sequences.fasta', 'codon_check_report.txt')
PYTHON_SCRIPT

echo ""
echo "=========================================="
echo "Processing Complete!"
echo "=========================================="
echo "Output files:"
echo "  - Combined sequences: $OUTPUT_COMBINED"
echo "  - Codon check report: $REPORT_FILE"
