import csv
import os

# --- Protocol constants ---
MAX_WEIGHT = 4000000
MANDATORY_TX = "4c50e3dad7f98bceb6441f96b23748dea84fbdb7cedd603441e6ea4a574d04a6"
MEMPOOL_FILE = "data/mempool.csv"
OUTPUT_FILE = "solutions/exercise01.txt"


def parse_mempool(filepath):
    """Lê o arquivo CSV e constrói um dicionário mapeando txid -> {fee, weight, parents}."""
    mempool = {}
    with open(filepath, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            if row[1] == "fee":  # Pula a linha de cabeçalho, se existir
                continue
            txid = row[0]
            fee = int(row[1])
            weight = int(row[2])
            parents = row[3].split(";") if row[3] else []
            mempool[txid] = {"fee": fee, "weight": weight, "parents": parents}
    return mempool


def get_unincluded_ancestors(txid, mempool, included_txs):
    """
    Retorna uma lista de ancestrais (incluindo a própria transação)
    que ainda não estão no bloco. A lista é retornada em ordem topológica válida.
    """
    ancestors_to_add = []
    visited = set()

    def dfs(current_txid):
        # Se já foi processado nesta busca ou já está no bloco, ignora.
        if current_txid in included_txs or current_txid in visited:
            return
        visited.add(current_txid)

        # Visita todos os pais antes de adicionar o filho (Post-order DFS)
        for parent in mempool[current_txid]["parents"]:
            if parent in mempool:
                dfs(parent)

        ancestors_to_add.append(current_txid)

    dfs(txid)
    return ancestors_to_add


def solve():
    mempool = parse_mempool(MEMPOOL_FILE)

    included_txs_set = set() 
    block_txs = [] 
    current_weight = 0
    total_fees = 0

    def add_tx_and_ancestors(txid):
        """Tenta adicionar uma transação e seus ancestrais ausentes ao bloco."""
        nonlocal current_weight, total_fees
        ancestors = get_unincluded_ancestors(txid, mempool, included_txs_set)

        total_pkg_weight = sum(mempool[anc]["weight"] for anc in ancestors)

        if current_weight + total_pkg_weight > MAX_WEIGHT:
            return False  # Não cabe no bloco

        for anc in ancestors:
            included_txs_set.add(anc)
            block_txs.append(anc)
            current_weight += mempool[anc]["weight"]
            total_fees += mempool[anc]["fee"]
        return True

    if MANDATORY_TX in mempool:
        add_tx_and_ancestors(MANDATORY_TX)

    candidates = []
    for txid in mempool:
        if txid in included_txs_set:
            continue

        ancestors = get_unincluded_ancestors(txid, mempool, included_txs_set)
        pkg_fee = sum(mempool[anc]["fee"] for anc in ancestors)
        pkg_weight = sum(mempool[anc]["weight"] for anc in ancestors)

        fee_rate = pkg_fee / pkg_weight if pkg_weight > 0 else 0

        candidates.append({"txid": txid, "fee_rate": fee_rate})

    candidates.sort(key=lambda x: x["fee_rate"], reverse=True)

    for candidate in candidates:
        if candidate["txid"] not in included_txs_set:
            add_tx_and_ancestors(candidate["txid"])

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        for txid in block_txs:
            f.write(txid + "\n")

    print("--- Mineração Concluída ---")
    print(f"Transações no Bloco : {len(block_txs)}")
    print(f"Peso Total          : {current_weight} (Max: {MAX_WEIGHT})")
    print(f"Taxas Arrecadadas   : {total_fees} sats")


if __name__ == "__main__":
    solve()
