# utils_memory.py
import psutil
import torch

def get_system_memory():
    """返回系统内存使用信息"""
    mem = psutil.virtual_memory()
    return {
        "total_GB": round(mem.total / (1024**3), 2),
        "used_GB": round(mem.used / (1024**3), 2),
        "percent": mem.percent
    }

def get_gpu_memory(device=0):
    """返回GPU显存信息（如果有CUDA）"""
    if not torch.cuda.is_available():
        return {"available": False, "message": "CUDA not available"}
    gpu_mem = torch.cuda.memory_reserved(device)
    gpu_alloc = torch.cuda.memory_allocated(device)
    gpu_total = torch.cuda.get_device_properties(device).total_memory
    return {
        "gpu_total_GB": round(gpu_total / (1024**3), 2),
        "gpu_reserved_GB": round(gpu_mem / (1024**3), 2),
        "gpu_allocated_GB": round(gpu_alloc / (1024**3), 2),
        "percent_used": round(100 * gpu_alloc / gpu_total, 1)
    }

def print_memory_report():
    """打印系统和GPU内存情况"""
    sys_mem = get_system_memory()
    gpu_mem = get_gpu_memory()

    print("=== System Memory ===")
    for k, v in sys_mem.items():
        print(f"{k:20s}: {v}")

    print("\n=== GPU Memory ===")
    for k, v in gpu_mem.items():
        print(f"{k:20s}: {v}")
