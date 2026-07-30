from Bio import SeqIO

fasta_file = "combined_all_genes.fa"
bed_file = "combined_all_genes.bed"

with open(bed_file, "w") as bed:
    for record in SeqIO.parse(fasta_file, "fasta"):
        chrom = record.id
        start = 0
        end = len(record.seq)

        # BED6 format
        bed.write(f"{chrom}\t{start}\t{end}\t{chrom}\t0\t+\n")

print(f"BED file written to: {bed_file}")

