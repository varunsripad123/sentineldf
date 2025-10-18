"""Streamlit web application for SentinelDF.

This module provides an interactive web interface for:
- Scanning datasets for threats
- Visualizing risk analysis results
- Managing MBOM records
- Exploring embeddings with UMAP
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import streamlit as st

# Add parent directory to path for backend imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import backend functions to reuse logic
try:
    from backend.app import (
        DocumentInput,
        DocumentResult,
        _analyze_document,
        _generate_batch_id,
        _sign_mbom,
        HEUR_CACHE,
        EMB_CACHE,
    )
    from backend.utils.config import get_config
except ImportError as e:
    st.error(f"Failed to import backend modules: {e}")
    st.stop()

# Global time budget for UMAP (seconds)
UMAP_TIME_BUDGET = 30
UMAP_MAX_DOCS = 1000


def load_text_files(path: Path) -> List[tuple[str, str]]:
    """Load text files from path.
    
    Args:
        path: Directory or file path.
    
    Returns:
        List of (filename, content) tuples.
    """
    files = []
    if path.is_dir():
        for file_path in sorted(path.glob("*.txt")):
            try:
                content = file_path.read_text(encoding="utf-8")
                files.append((file_path.name, content))
            except Exception as e:
                st.warning(f"Could not read {file_path.name}: {e}")
    elif path.is_file():
        content = path.read_text(encoding="utf-8")
        files.append((path.name, content))
    return files


@st.cache_data(ttl=3600)
def compute_umap_embeddings(texts: List[str], doc_ids: List[str]) -> Optional[pd.DataFrame]:
    """Compute UMAP 2D projection of embeddings.
    
    Args:
        texts: List of text content.
        doc_ids: List of document IDs.
    
    Returns:
        DataFrame with x, y, doc_id columns, or None if computation fails/skipped.
    """
    if len(texts) > UMAP_MAX_DOCS:
        st.warning(
            f"⏭️ Skipping UMAP: {len(texts)} documents exceeds limit of {UMAP_MAX_DOCS}"
        )
        return None
    
    try:
        import umap
        from sentence_transformers import SentenceTransformer
        
        start_time = time.time()
        
        # Load model and encode
        with st.spinner("Computing embeddings for UMAP..."):
            model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
            embeddings = model.encode(texts, show_progress_bar=False, batch_size=32)
        
        # Check time budget
        if time.time() - start_time > UMAP_TIME_BUDGET:
            st.warning("⏭️ Skipping UMAP: Time budget exceeded")
            return None
        
        # Compute UMAP
        with st.spinner("Computing UMAP projection..."):
            reducer = umap.UMAP(n_components=2, random_state=42, n_neighbors=min(15, len(texts) - 1))
            projection = reducer.fit_transform(embeddings)
        
        return pd.DataFrame({
            "x": projection[:, 0],
            "y": projection[:, 1],
            "doc_id": doc_ids,
        })
    
    except ImportError:
        st.info("📦 Install umap-learn to enable UMAP visualization: pip install umap-learn")
        return None
    except Exception as e:
        st.error(f"UMAP computation failed: {e}")
        return None


def render_sidebar() -> Dict[str, Any]:
    """Render sidebar controls and return configuration.
    
    Returns:
        Dictionary with configuration settings.
    """
    st.sidebar.title("⚙️ Configuration")
    
    # File/Folder picker
    st.sidebar.subheader("📁 Data Source")
    input_method = st.sidebar.radio(
        "Input method:",
        ["Local folder path", "Upload files"],
        help="Choose how to provide input data"
    )
    
    files = []
    if input_method == "Local folder path":
        folder_path = st.sidebar.text_input(
            "Folder or file path:",
            value="data/samples",
            help="Path to folder containing .txt files or single .txt file"
        )
        path = Path(folder_path)
        if path.exists():
            files = load_text_files(path)
            if files:
                st.sidebar.success(f"✓ Loaded {len(files)} file(s)")
            else:
                st.sidebar.warning("No .txt files found")
        else:
            st.sidebar.error("Path does not exist")
    else:
        uploaded = st.sidebar.file_uploader(
            "Upload .txt files:",
            type=["txt"],
            accept_multiple_files=True,
            help="Upload one or more text files"
        )
        if uploaded:
            for f in uploaded:
                content = f.read().decode("utf-8")
                files.append((f.name, content))
            st.sidebar.success(f"✓ Uploaded {len(files)} file(s)")
    
    # Threshold sliders
    st.sidebar.subheader("🎚️ Detection Thresholds")
    
    quarantine_threshold = st.sidebar.slider(
        "Quarantine threshold (0-100):",
        min_value=0,
        max_value=100,
        value=70,
        help="Risk score above which documents are quarantined"
    )
    
    st.sidebar.markdown("**Detector Weights** (must sum to 1.0):")
    heuristic_weight = st.sidebar.slider(
        "Heuristic weight:",
        min_value=0.0,
        max_value=1.0,
        value=0.4,
        step=0.05,
        help="Weight for pattern-based detection"
    )
    
    embedding_weight = st.sidebar.slider(
        "Embedding weight:",
        min_value=0.0,
        max_value=1.0,
        value=0.6,
        step=0.05,
        help="Weight for outlier-based detection"
    )
    
    # Validate weights sum to 1.0
    weight_sum = heuristic_weight + embedding_weight
    if abs(weight_sum - 1.0) > 0.01:
        st.sidebar.error(f"⚠️ Weights sum to {weight_sum:.2f}, must equal 1.0")
    else:
        st.sidebar.success(f"✓ Weights valid (sum = {weight_sum:.2f})")
    
    # Control buttons
    st.sidebar.subheader("🎮 Actions")
    
    col1, col2 = st.sidebar.columns(2)
    scan_button = col1.button("🔍 Scan", use_container_width=True, type="primary")
    
    if col2.button("🗑️ Clear Cache", use_container_width=True):
        HEUR_CACHE.clear()
        EMB_CACHE.clear()
        st.cache_data.clear()
        st.sidebar.success("✓ Cache cleared")
        st.experimental_rerun()
    
    # Load sample corpus
    if st.sidebar.button("📂 Load Sample Corpus", use_container_width=True):
        sample_path = Path("data/samples")
        if sample_path.exists():
            files = load_text_files(sample_path)
            st.sidebar.success(f"✓ Loaded {len(files)} samples")
        else:
            st.sidebar.error("Sample corpus not found at data/samples")
    
    # Cache stats
    st.sidebar.subheader("💾 Cache Statistics")
    st.sidebar.text(f"Heuristic cache: {HEUR_CACHE.size()} entries")
    st.sidebar.text(f"Embedding cache: {EMB_CACHE.size()} entries")
    
    return {
        "files": files,
        "quarantine_threshold": quarantine_threshold,
        "heuristic_weight": heuristic_weight,
        "embedding_weight": embedding_weight,
        "scan_triggered": scan_button,
    }


def analyze_documents(files: List[tuple[str, str]], config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Analyze documents and return results.
    
    Args:
        files: List of (filename, content) tuples.
        config: Configuration dictionary.
    
    Returns:
        List of result dictionaries.
    """
    try:
        cfg = get_config()
        # Override with UI settings
        cfg.risk_quarantine_threshold = config["quarantine_threshold"]
        cfg.heuristic_weight = config["heuristic_weight"]
        cfg.embedding_weight = config["embedding_weight"]
    except Exception as e:
        st.error(f"Failed to load configuration: {e}")
        return []
    
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    start_time = time.time()
    
    for idx, (filename, content) in enumerate(files):
        try:
            doc_id = f"{filename}_{hashlib.md5(content.encode()).hexdigest()[:8]}"
            doc = DocumentInput(id=doc_id, content=content, metadata={"filename": filename})
            
            result = _analyze_document(doc, cfg)
            results.append(result.dict())
            
            # Update progress
            progress = (idx + 1) / len(files)
            progress_bar.progress(progress)
            status_text.text(f"Processing: {filename} ({idx + 1}/{len(files)})")
        
        except Exception as e:
            st.error(f"Error analyzing {filename}: {e}")
            results.append({
                "doc_id": filename,
                "risk": 0,
                "quarantine": False,
                "reasons": [f"Analysis failed: {str(e)}"],
                "signals": {"heuristic": 0.0, "embedding": 0.0},
                "action": "allow",
            })
    
    elapsed = time.time() - start_time
    progress_bar.empty()
    status_text.success(f"✓ Analyzed {len(files)} documents in {elapsed:.2f}s")
    
    return results


def render_summary_cards(results: List[Dict[str, Any]]) -> None:
    """Render summary statistics cards.
    
    Args:
        results: List of result dictionaries.
    """
    if not results:
        return
    
    # Calculate statistics
    total = len(results)
    quarantined = sum(1 for r in results if r["quarantine"])
    allowed = total - quarantined
    risks = [r["risk"] for r in results]
    avg_risk = np.mean(risks)
    p95_risk = np.percentile(risks, 95)
    max_risk = max(risks)
    
    # Display cards
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("📄 Total Documents", total)
    
    with col2:
        st.metric("✅ Allowed", allowed, delta=None, delta_color="normal")
    
    with col3:
        st.metric("🚫 Quarantined", quarantined, delta=None, delta_color="inverse")
    
    with col4:
        st.metric("📊 Avg Risk", f"{avg_risk:.1f}")
    
    with col5:
        st.metric("📈 P95 / Max Risk", f"{p95_risk:.0f} / {max_risk}")


def render_results_table(results: List[Dict[str, Any]]) -> None:
    """Render interactive results table.
    
    Args:
        results: List of result dictionaries.
    """
    if not results:
        st.info("No results to display. Click 'Scan' to analyze documents.")
        return
    
    # Create DataFrame
    df = pd.DataFrame(results)
    
    # Add quarantine toggles to session state
    if "quarantine_overrides" not in st.session_state:
        st.session_state.quarantine_overrides = {}
    
    # Display table with custom formatting
    st.subheader("📋 Analysis Results")
    
    # Table header
    cols = st.columns([2, 1, 2, 2, 1, 1])
    cols[0].markdown("**Document ID**")
    cols[1].markdown("**Risk**")
    cols[2].markdown("**Signals**")
    cols[3].markdown("**Reasons**")
    cols[4].markdown("**Quarantine**")
    cols[5].markdown("**Actions**")
    
    # Render rows
    for idx, row in df.iterrows():
        cols = st.columns([2, 1, 2, 2, 1, 1])
        
        # Document ID
        cols[0].text(row["doc_id"][:30] + "..." if len(row["doc_id"]) > 30 else row["doc_id"])
        
        # Risk bar
        risk = row["risk"]
        risk_color = "🟢" if risk < 30 else "🟡" if risk < 70 else "🔴"
        cols[1].markdown(f"{risk_color} {risk}")
        cols[1].progress(risk / 100)
        
        # Signals
        h_sig = row["signals"]["heuristic"]
        e_sig = row["signals"]["embedding"]
        cols[2].markdown(f"H: {h_sig:.2f} / E: {e_sig:.2f}")
        
        # Reasons (chips)
        reasons = row["reasons"][:2]  # Show first 2
        reason_text = ", ".join(reasons) if reasons else "No issues"
        cols[3].text(reason_text[:40] + "..." if len(reason_text) > 40 else reason_text)
        
        # Quarantine toggle
        doc_id = row["doc_id"]
        current_q = st.session_state.quarantine_overrides.get(doc_id, row["quarantine"])
        new_q = cols[4].checkbox(
            "Q",
            value=current_q,
            key=f"q_{idx}",
            label_visibility="collapsed"
        )
        if new_q != current_q:
            st.session_state.quarantine_overrides[doc_id] = new_q
            st.experimental_rerun()
        
        # View button
        if cols[5].button("👁️", key=f"view_{idx}", help="View details"):
            st.session_state[f"show_modal_{idx}"] = True
        
        # Modal for content viewing
        if st.session_state.get(f"show_modal_{idx}", False):
            with st.expander(f"📄 Document: {row['doc_id']}", expanded=True):
                st.markdown("**Risk Score:**")
                st.progress(risk / 100)
                st.text(f"{risk}/100")
                
                st.markdown("**Signals:**")
                st.json(row["signals"])
                
                st.markdown("**Reasons:**")
                for reason in row["reasons"]:
                    st.markdown(f"- {reason}")
                
                st.markdown("**Action:**")
                st.text(row["action"])
                
                if st.button("Close", key=f"close_{idx}"):
                    st.session_state[f"show_modal_{idx}"] = False
                    st.experimental_rerun()


def render_charts(results: List[Dict[str, Any]], files: List[tuple[str, str]]) -> None:
    """Render visualization charts.
    
    Args:
        results: List of result dictionaries.
        files: List of (filename, content) tuples.
    """
    if not results:
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Risk Distribution")
        risks = [r["risk"] for r in results]
        
        # Create histogram
        import plotly.express as px
        fig = px.histogram(
            x=risks,
            nbins=20,
            labels={"x": "Risk Score", "y": "Count"},
            title="Risk Score Histogram",
            color_discrete_sequence=["#1f77b4"]
        )
        fig.add_vline(x=70, line_dash="dash", line_color="red", annotation_text="Quarantine")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🗺️ UMAP Embeddings")
        
        if len(files) <= UMAP_MAX_DOCS:
            texts = [content for _, content in files]
            doc_ids = [r["doc_id"] for r in results]
            
            umap_df = compute_umap_embeddings(texts, doc_ids)
            
            if umap_df is not None:
                # Merge with risk scores
                umap_df["risk"] = [r["risk"] for r in results]
                umap_df["quarantine"] = [r["quarantine"] for r in results]
                
                import plotly.express as px
                fig = px.scatter(
                    umap_df,
                    x="x",
                    y="y",
                    color="risk",
                    hover_data=["doc_id"],
                    title="UMAP Projection (colored by risk)",
                    color_continuous_scale="RdYlGn_r",
                    labels={"x": "UMAP 1", "y": "UMAP 2", "risk": "Risk Score"}
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("UMAP visualization not available")
        else:
            st.warning(f"⏭️ UMAP skipped: {len(files)} docs > {UMAP_MAX_DOCS} limit")


def generate_mbom_download(results: List[Dict[str, Any]], approver: str) -> bytes:
    """Generate signed MBOM JSON for download.
    
    Args:
        results: List of result dictionaries.
        approver: Approver email/identifier.
    
    Returns:
        MBOM JSON as bytes.
    """
    batch_id = _generate_batch_id()
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    mbom_id = f"mbom_{hashlib.md5(f'{batch_id}{timestamp}'.encode()).hexdigest()[:16]}"
    
    # Calculate summary
    quarantined = sum(1 for r in results if r["quarantine"])
    allowed = len(results) - quarantined
    avg_risk = sum(r["risk"] for r in results) / len(results) if results else 0
    
    summary_data = {
        "total_docs": len(results),
        "quarantined": quarantined,
        "allowed": allowed,
        "avg_risk": round(avg_risk, 2),
    }
    
    # Create signable payload
    payload = {
        "mbom_id": mbom_id,
        "batch_id": batch_id,
        "approved_by": approver,
        "timestamp": timestamp,
        "summary": summary_data,
        "results_hash": hashlib.sha256(
            json.dumps(results, sort_keys=True).encode()
        ).hexdigest(),
    }
    
    # Sign
    signature = _sign_mbom(payload)
    
    # Prepare MBOM document
    mbom_doc = {
        "mbom_id": mbom_id,
        "batch_id": batch_id,
        "approved_by": approver,
        "timestamp": timestamp,
        "signature": signature,
        "summary": summary_data,
        "results": results,
        "metadata": {
            "source": "streamlit_dashboard",
            "tool_version": "1.0.0",
        },
    }
    
    return json.dumps(mbom_doc, indent=2).encode()


def main() -> None:
    """Main entry point for the Streamlit application."""
    st.set_page_config(
        page_title="SentinelDF - Data Firewall",
        page_icon="🛡️",
        layout="wide",
    )
    
    st.title("🛡️ SentinelDF - Data Firewall for LLM Training")
    st.markdown(
        "Scan documents for threats, analyze risk patterns, and generate signed audit trails."
    )
    
    # Render sidebar and get configuration
    config = render_sidebar()
    
    # Initialize session state
    if "results" not in st.session_state:
        st.session_state.results = []
    if "files" not in st.session_state:
        st.session_state.files = []
    if "quarantine_overrides" not in st.session_state:
        st.session_state.quarantine_overrides = {}
    
    # Handle scan trigger
    if config["scan_triggered"]:
        if not config["files"]:
            st.error("❌ No files to scan. Please provide input data.")
        elif abs(config["heuristic_weight"] + config["embedding_weight"] - 1.0) > 0.01:
            st.error("❌ Detector weights must sum to 1.0")
        else:
            with st.spinner("🔍 Analyzing documents..."):
                st.session_state.results = analyze_documents(config["files"], config)
                st.session_state.files = config["files"]
                st.session_state.quarantine_overrides = {}  # Reset overrides
            st.success("✅ Scan complete!")
            st.experimental_rerun()
    
    # Display results
    if st.session_state.results:
        # Apply quarantine overrides
        results = st.session_state.results.copy()
        for idx, r in enumerate(results):
            if r["doc_id"] in st.session_state.get("quarantine_overrides", {}):
                r["quarantine"] = st.session_state.quarantine_overrides[r["doc_id"]]
        
        # Summary cards
        render_summary_cards(results)
        
        st.markdown("---")
        
        # Results table
        render_results_table(results)
        
        st.markdown("---")
        
        # Charts
        render_charts(results, st.session_state.files)
        
        st.markdown("---")
        
        # MBOM generation
        st.subheader("📋 Generate MBOM")
        col1, col2, col3 = st.columns([2, 1, 1])
        
        approver = col1.text_input(
            "Approver email:",
            value="security@company.com",
            help="Email or identifier of the person approving this scan"
        )
        
        if col2.button("🔐 Generate MBOM", use_container_width=True, type="primary"):
            if not approver:
                st.error("Please provide approver email")
            else:
                try:
                    mbom_bytes = generate_mbom_download(results, approver)
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    
                    col3.download_button(
                        label="⬇️ Download MBOM",
                        data=mbom_bytes,
                        file_name=f"mbom_{timestamp}.json",
                        mime="application/json",
                        use_container_width=True,
                    )
                    st.success("✅ MBOM generated successfully!")
                except Exception as e:
                    st.error(f"Failed to generate MBOM: {e}")
    
    else:
        st.info("👈 Configure settings in the sidebar and click 'Scan' to begin analysis.")


if __name__ == "__main__":
    main()
