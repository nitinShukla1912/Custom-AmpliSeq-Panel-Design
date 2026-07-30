import os
from Bio import SeqIO

input_dir = "."
output_fasta = "combined_all_genes.fa"
log_file = "header_rename.log"

with open(output_fasta, "w") as fasta_out, open(log_file, "w") as log:
    log.write("source_file\told_header\tnew_header\tlength_bp\n")

    for fname in sorted(os.listdir(input_dir)):
        if not fname.endswith(".cdhit90.longest.fa"):
            continue

        gene = fname.replace(".cdhit90.longest.fa", "")
        fpath = os.path.join(input_dir, fname)

        count = 1
        for record in SeqIO.parse(fpath, "fasta"):
            old_id = record.id
            new_id = f"{gene}_{count}"
            seq_len = len(record.seq)

            # Update FASTA header
            record.id = new_id
            record.name = ""
            record.description = ""

            # Write FASTA
            SeqIO.write(record, fasta_out, "fasta")

            # Write log
            log.write(f"{fname}\t{old_id}\t{new_id}\t{seq_len}\n")

            count += 1

print("Done:")
print(f" - Combined FASTA : {output_fasta}")
print(f" - Rename log     : {log_file}")
