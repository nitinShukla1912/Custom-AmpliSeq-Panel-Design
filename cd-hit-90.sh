#!/bin/bash
set -euo pipefail

# Output directory
OUTDIR="cdhit_90"
mkdir -p "$OUTDIR"

# Run CD-HIT on each fasta file
for f in *.fa *.fasta ; do
    [ -e "$f" ] || continue   # skip if no match

    base=$(basename "$f")
    prefix="${base%.*}"

    echo "Running CD-HIT on: $f"

    cd-hit \
      -i "$f" \
      -o "$OUTDIR/${prefix}.cdhit95.fa" \
      -c 0.90 \
      -n 5 \
      -M 50000 \
      -d 0 \
      -T 50

    echo "Done: $OUTDIR/${prefix}.cdhit95.fa"
    echo "-------------------------------"
done

echo "? All files clustered at 95% identity. Output in: $OUTDIR/"
