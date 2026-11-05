import torch


def get_gpu_memory_mb():
    if not torch.cuda.is_available():
        return None

    total = torch.cuda.get_device_properties(0).total_memory / (1024 ** 2)
    free, _ = torch.cuda.mem_get_info()
    free = free / (1024 ** 2)
    return {
        "total_mb": total,
        "free_mb": free,
    }


print("PyTorch version:", torch.__version__)
print("CUDA available:", torch.cuda.is_available())
print("CUDA version:", torch.version.cuda)

if torch.cuda.is_available():
    print("GPU name:", torch.cuda.get_device_name(0))
    gpu_memory = get_gpu_memory_mb()
    if gpu_memory is not None:
        print(f"GPU memory: {gpu_memory['total_mb']:.0f} MB total, {gpu_memory['free_mb']:.0f} MB free")
else:
    print("GPU name: CPU")
    print("GPU memory: not available on CPU")
