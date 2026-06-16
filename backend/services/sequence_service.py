from Bio.Seq import Seq
from Bio import pairwise2
from typing import List, Dict

VALID_DNA = set("ACGTNacgtn")

def analyze_sequence(seq: str) -> Dict:
    seq = seq.strip().replace("\n", "").upper()
    if not seq or not set(seq).issubset(set("ACGTN")):
        raise ValueError("Sequence must be DNA (A/C/G/T/N).")
    s = Seq(seq)
    gc = (seq.count("G") + seq.count("C")) / len(seq) * 100
    protein = str(s.translate(to_stop=False))
    orfs = find_orfs(seq)
    return {
        "length": len(seq),
        "gc_content": round(gc, 2),
        "translation": protein,
        "orfs": orfs[:10],
        "reverse_complement": str(s.reverse_complement()),
    }

def find_orfs(seq: str, min_len: int = 30) -> List[Dict]:
    orfs = []
    for frame in range(3):
        i = frame
        while i < len(seq) - 2:
            codon = seq[i:i+3]
            if codon == "ATG":
                j = i
                while j < len(seq) - 2:
                    c = seq[j:j+3]
                    if c in ("TAA", "TAG", "TGA"):
                        if j - i >= min_len:
                            orfs.append({"frame": frame + 1, "start": i, "end": j+3, "length": j+3-i})
                        i = j
                        break
                    j += 3
            i += 3
    return orfs

def align_sequences(a: str, b: str) -> Dict:
    a = a.strip().upper(); b = b.strip().upper()
    aln = pairwise2.align.globalxx(a, b, one_alignment_only=True)[0]
    return {"seqA": aln.seqA, "seqB": aln.seqB, "score": aln.score,
            "start": aln.start, "end": aln.end}
