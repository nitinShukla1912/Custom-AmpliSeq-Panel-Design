# AMR Custom AmpliSeq Panel Design

Pipeline for preparing a multi-organism, multi-gene AMR (antimicrobial resistance) FASTA collection for upload to the Ion AmpliSeq Designer portal as a custom gene panel.

## Overview

Input genes are Prokka-annotated, gene-wise FASTA sequences pooled from multiple organisms, and are of uneven length. This pipeline clusters redundant sequences, selects a representative (longest) sequence per cluster, validates reading frames, standardizes headers, and produces a BED file describing target regions — the format required by the AmpliSeq Designer for a custom reference panel.

#### I hope this detailed document will help in your research. Please cite this repository if you have used concepts from it to understand and expand your knowledge regarding panel design.

```https://github.com/nitinShukla1912/Custom-AmpliSeq-Panel-Design```

## Workflow

```
Multi-gene, multi-organism FASTA (Prokka-annotated)
        │
        ▼
1. cd-hit-90.sh                         # cluster sequences at 90% identity
        │
        ▼
2. extract_longest_sequences.py         # keep longest sequence per cluster
        │
        ▼
3. check_codons.py /                    # verify start/stop codons,
   process_fasta_and_check_codons.sh    # annotate headers with source file info
        │
        ▼
4. rename_headers_and_combine_with_log.py   # (optional) standardize + merge headers
        │
        ▼
5. fasta_to_bed.py                      # generate BED file for target regions
        │
        ▼
   Upload FASTA + BED to AmpliSeq Designer
```

## Scripts

| Script | Purpose |
|---|---|
| `cd-hit-90.sh` | Runs CD-HIT at 90% identity to cluster/de-duplicate input FASTA sequences |
| `extract_longest_sequences.py` | Extracts the longest sequence from each CD-HIT cluster (`python3 extract_longest_sequences.py . Long_Seq`) |
| `check_codons.py` | Checks each sequence for valid start/stop codons and tags headers with source file info |
| `process_fasta_and_check_codons.sh` | Shell wrapper that runs the FASTA processing + codon check step end-to-end |
| `rename_headers_and_combine_with_log.py` | *(Optional)* Renames FASTA headers to a standardized format, combines files, and logs the changes |
| `fasta_to_bed.py` | Converts the final FASTA into a tab-separated BED file for AmpliSeq target regions |

## Usage

```bash
# 1. Cluster sequences
./cd-hit-90.sh

# 2. Extract longest sequence per cluster
python3 extract_longest_sequences.py . Long_Seq

# 3. Validate codons and tag headers
python3 check_codons.py
# — or —
./process_fasta_and_check_codons.sh

# 4. (Optional) Standardize/rename headers
python3 rename_headers_and_combine_with_log.py

# 5. Generate BED file
python3 fasta_to_bed.py
```

## BED File Format

Tab-separated, with **50 bp trimmed from the start and end** of each region before upload:

```
AcrAB_TolC_1     50    3126    AcrAB_TolC_1
AcrAD_TolC_1     50    3063    AcrAD_TolC_1
AcrEF_TolC_1     50    3063    AcrEF_TolC_1
Alr_1            50    2055    Alr_1
Ddl_1            50    1143    Ddl_1
```

> **Note:** Remember to remove the 50 bp padding from both the start and end coordinates before uploading.

## Uploading to AmpliSeq Designer

1. Log in (or create an account) at [ampliseq.com](https://www.ampliseq.com/login/login.action).
2. From the dashboard, add a **Custom Reference** (e.g. `genes.fasta`).
3. Go to **Custom Panel**.
4. Select design parameters:
   - **Application Type:** DNA Gene Designs (multi pool)
   - **DNA Type:** Standard DNA (275 bp)
   - **Genome to use:** Custom Reference
   - Add a name and details for the panel
5. Add target region details manually, or upload the generated `.bed` file.
6. Submit the design and download the resulting panel results as a ZIP once ready.

## Requirements

- [CD-HIT](https://github.com/weizhongli/cdhit)
- Python 3
- Biopython (for FASTA parsing in the Python scripts)

## Repository Structure

```
.
├── cd-hit-90.sh
├── extract_longest_sequences.py
├── check_codons.py
├── process_fasta_and_check_codons.sh
├── rename_headers_and_combine_with_log.py
├── fasta_to_bed.py
└── README.md
```

## DESIGNING Panel

### Step 1: Login here or create new credentials

https://www.ampliseq.com/login/login.action

### Step 2: You will land here

<img width="1035" height="503" alt="image" src="https://github.com/user-attachments/assets/0539d7cc-60a6-421c-871a-4915ed23c210" />

### Step 3. Add a custom reference (example: genes.fasta)

<img width="944" height="213" alt="image" src="https://github.com/user-attachments/assets/b81311ed-359d-4b8d-be84-817e3a156273" />

### Step 4. Click on Custom panel

<img width="1039" height="505" alt="image" src="https://github.com/user-attachments/assets/b8d4e97f-0160-4af7-b57b-503459638f46" />

### Step 5. Select parameters based on sequencing chemistry and target host

<img width="944" height="449" alt="image" src="https://github.com/user-attachments/assets/f06a3b5e-f047-439a-8fa2-c975d3a8cc46" />
<img width="944" height="390" alt="image" src="https://github.com/user-attachments/assets/fdae1f65-3bb3-40b0-a64e-4b79b713fd9e" />
<img width="944" height="341" alt="image" src="https://github.com/user-attachments/assets/c4c5bdd9-1974-4a2d-9a4c-4a6bffc11cc2" />

### Select and add your information

1. In Application Type:
Select: DNA Gene Designs (multi pool)
2. DNA Type
Select: Standard DNA (275 bp)
3. Select genome to use
Select: Custom Reference
Leave 4.
5. Add name & Details

### Step 6. Add regions details

<img width="944" height="301" alt="image" src="https://github.com/user-attachments/assets/39fa6fe9-97c6-49b1-a16f-c29acbf91e7a" />

#### You can manually add details or upload a bed file

<img width="944" height="317" alt="image" src="https://github.com/user-attachments/assets/f2c10c97-73cb-4705-ac7b-11f40b06f033" />


File.bed (tab separated) example
```
AcrAB_TolC_1	50	3126	AcrAB_TolC_1
AcrAD_TolC_1	50	3063	AcrAD_TolC_1
AcrEF_TolC__1	50	3063	AcrEF_TolC__1
Alr_1	50	2055	Alr_1
Ddl_1	50	1143	Ddl_1
```

#### Note: Remember to remove 50 bp from start and end.

#### Results: You can download the results in zip file and explore

#### Cite: https://github.com/nitinShukla1912/Custom-AmpliSeq-Panel-Design
#### MIT-liscence
