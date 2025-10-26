"""Clustering utilities (e.g., TF-IDF + KMeans helpers)."""

from __future__ import annotations
from typing import Sequence, Any

from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer


def build_tfidf_matrix(texts: Sequence[str]) -> Any:
    """Create a TF-IDF matrix from a list of texts."""
    vec = TfidfVectorizer()
    return vec.fit_transform(texts)


def kmeans_labels(data_matrix: Any, k: int) -> list[int]:
    """Run KMeans on a precomputed matrix and return cluster labels."""
    model = KMeans(n_clusters=k, n_init="auto", random_state=42)
    return list(model.fit_predict(data_matrix))
