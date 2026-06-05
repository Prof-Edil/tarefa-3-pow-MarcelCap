import hashlib
import os

# --- Constantes do Exercício ---
INPUT_FILE = "data/ex02_txid_list.txt"
OUTPUT_FILE = "solutions/exercise02.txt"
TARGET_TX_HEX = "49ff8cccf1ca12179e9ae7a4760f550b5a18401b27e1e057604e27c3e10c08fb"


def sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def solve_merkle_tree():
    txids_hex = []
    with open(INPUT_FILE, "r") as f:
        for line in f:
            tx = line.strip()
            if tx:
                txids_hex.append(tx)

    current_level = [bytes.fromhex(tx) for tx in txids_hex]
    target_bytes = bytes.fromhex(TARGET_TX_HEX)

    try:
        target_index = current_level.index(target_bytes)
    except ValueError:
        print("Erro: A transação alvo não foi encontrada na lista!")
        return

    proof_siblings = []

    # Construção da Árvore e Extração da Prova
    while len(current_level) > 1:
        next_level = []

        # Se a camada for ímpar, duplica o último elemento
        if len(current_level) % 2 != 0:
            current_level.append(current_level[-1])

        # Processar em pares (saltando de 2 em 2)
        for i in range(0, len(current_level), 2):
            left = current_level[i]
            right = current_level[i + 1]

            combined_hash = sha256(left + right)
            next_level.append(combined_hash)

            # Lógica de Captura da Prova (Merkle Proof)
            # Se o nosso alvo faz parte deste par, salvamos o irmão dele
            if target_index == i:  # Alvo está na esquerda
                proof_siblings.append(right)
            elif target_index == i + 1:  # Alvo está na direita
                proof_siblings.append(left)

        current_level = next_level
        target_index = target_index // 2

    merkle_root = current_level[0]

    # Geração do Arquivo de Saída
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        f.write(merkle_root.hex() + "\n")
      
        for sibling in proof_siblings:
            f.write(sibling.hex() + "\n")

    print("--- Construção da Árvore de Merkle Concluída ---")
    print(f"Merkle Root : {merkle_root.hex()}")
    print(f"Tamanho da Prova : {len(proof_siblings)} hashes")


if __name__ == "__main__":
    solve_merkle_tree()
