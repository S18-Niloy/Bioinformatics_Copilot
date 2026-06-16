"""Train the toy GCN and save checkpoint."""
import torch
import torch.nn.functional as F
from gnn_model import GCN, DATA, CKPT

def main(epochs: int = 200):
    model = GCN()
    opt = torch.optim.Adam(model.parameters(), lr=0.01, weight_decay=5e-4)
    model.train()
    for ep in range(1, epochs + 1):
        opt.zero_grad()
        out = model(DATA.x, DATA.edge_index)
        loss = F.cross_entropy(out, DATA.y)
        loss.backward(); opt.step()
        if ep % 50 == 0:
            acc = (out.argmax(-1) == DATA.y).float().mean().item()
            print(f"epoch {ep:3d}  loss {loss.item():.4f}  acc {acc:.3f}")
    torch.save(model.state_dict(), CKPT)
    print(f"saved → {CKPT}")

if __name__ == "__main__":
    main()
