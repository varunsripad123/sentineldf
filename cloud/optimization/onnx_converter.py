"""
ONNX Model Conversion and Optimization for SentinelDF Cloud.

Converts Sentence-Transformers models to:
- ONNX format for faster inference
- INT8 quantization for 3-4x speedup
- Optimized graph for CPU execution

This enables high-throughput ML inference without GPUs.
"""
import os
from typing import Optional, Tuple
from pathlib import Path

try:
    import torch
    import onnx
    import onnxruntime as ort
    from sentence_transformers import SentenceTransformer
    from optimum.onnxruntime import ORTModelForFeatureExtraction, ORTQuantizer
    from optimum.onnxruntime.configuration import AutoQuantizationConfig
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False
    print("⚠️  ONNX dependencies not installed. Install with:")
    print("   pip install torch sentence-transformers onnx onnxruntime optimum[onnxruntime]")

# ============================================================================
# MODEL CONVERSION
# ============================================================================

def convert_to_onnx(
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    output_dir: str = "./models/onnx",
    quantize: bool = True
) -> str:
    """
    Convert Sentence-Transformers model to ONNX format.
    
    Args:
        model_name: HuggingFace model name or path
        output_dir: Output directory for ONNX model
        quantize: Whether to apply INT8 quantization
    
    Returns:
        Path to converted model directory
    """
    if not DEPENDENCIES_AVAILABLE:
        raise RuntimeError("ONNX dependencies not available")
    
    print(f"🔄 Converting {model_name} to ONNX...")
    
    # Create output directory
    output_path = Path(output_dir) / model_name.replace("/", "_")
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Load model
    print("📥 Loading model...")
    model = SentenceTransformer(model_name)
    
    # Export to ONNX
    print("🔧 Exporting to ONNX...")
    onnx_path = output_path / "model.onnx"
    
    # Get dummy input
    dummy_input = model.tokenize(["This is a sample sentence."])
    
    # Export
    torch.onnx.export(
        model[0].auto_model,  # Transformer model
        (dummy_input["input_ids"], dummy_input["attention_mask"]),
        onnx_path,
        input_names=['input_ids', 'attention_mask'],
        output_names=['last_hidden_state'],
        dynamic_axes={
            'input_ids': {0: 'batch', 1: 'sequence'},
            'attention_mask': {0: 'batch', 1: 'sequence'},
            'last_hidden_state': {0: 'batch', 1: 'sequence'}
        },
        opset_version=14
    )
    
    print(f"✅ ONNX model saved to {onnx_path}")
    
    # Quantize if requested
    if quantize:
        print("🔧 Applying INT8 quantization...")
        quantized_path = quantize_model(str(onnx_path), str(output_path / "model_int8.onnx"))
        print(f"✅ Quantized model saved to {quantized_path}")
        return str(output_path)
    
    return str(output_path)

def quantize_model(
    onnx_model_path: str,
    output_path: str,
    quantization_mode: str = "IntegerOps"
) -> str:
    """
    Apply INT8 quantization to ONNX model.
    
    Args:
        onnx_model_path: Path to ONNX model
        output_path: Output path for quantized model
        quantization_mode: Quantization mode (IntegerOps or QLinearOps)
    
    Returns:
        Path to quantized model
    """
    if not DEPENDENCIES_AVAILABLE:
        raise RuntimeError("ONNX dependencies not available")
    
    from onnxruntime.quantization import quantize_dynamic, QuantType
    
    print(f"🔧 Quantizing {onnx_model_path}...")
    
    # Quantize
    quantize_dynamic(
        onnx_model_path,
        output_path,
        weight_type=QuantType.QInt8
    )
    
    print(f"✅ Quantized model saved to {output_path}")
    return output_path

# ============================================================================
# INFERENCE
# ============================================================================

class ONNXEmbedder:
    """
    Fast ONNX-based embedding generator.
    
    3-4x faster than PyTorch on CPU.
    """
    
    def __init__(self, model_path: str, use_quantized: bool = True):
        """
        Initialize ONNX embedder.
        
        Args:
            model_path: Path to ONNX model directory
            use_quantized: Use INT8 quantized model if available
        """
        if not DEPENDENCIES_AVAILABLE:
            raise RuntimeError("ONNX dependencies not available")
        
        self.model_path = Path(model_path)
        
        # Load appropriate model
        if use_quantized and (self.model_path / "model_int8.onnx").exists():
            onnx_file = self.model_path / "model_int8.onnx"
            print(f"📦 Loading quantized ONNX model from {onnx_file}")
        else:
            onnx_file = self.model_path / "model.onnx"
            print(f"📦 Loading ONNX model from {onnx_file}")
        
        # Create ONNX Runtime session
        self.session = ort.InferenceSession(
            str(onnx_file),
            providers=['CPUExecutionProvider']
        )
        
        # Load tokenizer
        from transformers import AutoTokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            "sentence-transformers/all-MiniLM-L6-v2"
        )
        
        print("✅ ONNX embedder ready")
    
    def encode(self, texts: list[str], batch_size: int = 32) -> list:
        """
        Generate embeddings for texts.
        
        Args:
            texts: List of input texts
            batch_size: Batch size for processing
        
        Returns:
            List of embedding vectors
        """
        import numpy as np
        
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            
            # Tokenize
            inputs = self.tokenizer(
                batch,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors="np"
            )
            
            # Run inference
            outputs = self.session.run(
                None,
                {
                    "input_ids": inputs["input_ids"],
                    "attention_mask": inputs["attention_mask"]
                }
            )
            
            # Mean pooling
            last_hidden = outputs[0]
            attention_mask = inputs["attention_mask"]
            
            # Apply attention mask and compute mean
            mask_expanded = np.expand_dims(attention_mask, -1)
            sum_embeddings = np.sum(last_hidden * mask_expanded, axis=1)
            sum_mask = np.clip(np.sum(mask_expanded, axis=1), a_min=1e-9, a_max=None)
            batch_embeddings = sum_embeddings / sum_mask
            
            embeddings.extend(batch_embeddings)
        
        return embeddings
    
    def benchmark(self, num_samples: int = 100):
        """Run benchmark to measure performance."""
        import time
        
        texts = [f"This is sample text number {i}" for i in range(num_samples)]
        
        start = time.time()
        embeddings = self.encode(texts)
        duration = time.time() - start
        
        throughput = num_samples / duration
        
        print(f"\n📊 Benchmark Results:")
        print(f"   Samples: {num_samples}")
        print(f"   Duration: {duration:.2f}s")
        print(f"   Throughput: {throughput:.1f} texts/sec")
        print(f"   Latency: {duration/num_samples*1000:.1f}ms per text")
        
        return {
            "samples": num_samples,
            "duration_seconds": duration,
            "throughput_per_second": throughput,
            "latency_ms": duration/num_samples*1000
        }

# ============================================================================
# COMPARISON
# ============================================================================

def compare_models(
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    num_samples: int = 100
):
    """
    Compare PyTorch vs ONNX performance.
    
    Args:
        model_name: Model to benchmark
        num_samples: Number of samples to test
    """
    if not DEPENDENCIES_AVAILABLE:
        print("⚠️  Dependencies not available for comparison")
        return
    
    import time
    
    texts = [f"This is sample text number {i}" for i in range(num_samples)]
    
    # Benchmark PyTorch
    print("\n🔥 Benchmarking PyTorch model...")
    pytorch_model = SentenceTransformer(model_name)
    
    start = time.time()
    pytorch_embeddings = pytorch_model.encode(texts)
    pytorch_duration = time.time() - start
    pytorch_throughput = num_samples / pytorch_duration
    
    print(f"   Duration: {pytorch_duration:.2f}s")
    print(f"   Throughput: {pytorch_throughput:.1f} texts/sec")
    
    # Convert to ONNX if not exists
    onnx_path = f"./models/onnx/{model_name.replace('/', '_')}"
    if not Path(onnx_path).exists():
        print("\n🔄 Converting to ONNX...")
        convert_to_onnx(model_name, quantize=True)
    
    # Benchmark ONNX
    print("\n⚡ Benchmarking ONNX INT8 model...")
    onnx_embedder = ONNXEmbedder(onnx_path, use_quantized=True)
    results = onnx_embedder.benchmark(num_samples)
    
    # Compare
    speedup = pytorch_duration / results["duration_seconds"]
    
    print(f"\n📈 Comparison:")
    print(f"   PyTorch: {pytorch_throughput:.1f} texts/sec")
    print(f"   ONNX INT8: {results['throughput_per_second']:.1f} texts/sec")
    print(f"   Speedup: {speedup:.2f}x faster 🚀")

# ============================================================================
# CLI
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Convert models to ONNX")
    parser.add_argument("--model", default="sentence-transformers/all-MiniLM-L6-v2")
    parser.add_argument("--output", default="./models/onnx")
    parser.add_argument("--quantize", action="store_true", default=True)
    parser.add_argument("--benchmark", action="store_true")
    parser.add_argument("--compare", action="store_true")
    
    args = parser.parse_args()
    
    if args.compare:
        compare_models(args.model)
    elif args.benchmark:
        onnx_path = f"./models/onnx/{args.model.replace('/', '_')}"
        embedder = ONNXEmbedder(onnx_path)
        embedder.benchmark()
    else:
        convert_to_onnx(args.model, args.output, args.quantize)
