import math
from typing import List, Dict, Any, Tuple
import numpy as np
import cv2
from app.utils.image_utils import encode_cv2_to_base64_data_uri

def detect_copy_move(cv_bgr: np.ndarray, cv_gray: np.ndarray) -> dict:
    """
    Detects potential copy-move (cloning) forgery using ORB feature detection,
    internal descriptor cross-matching, spatial distance filtering, and displacement vector clustering.
    
    Returns structured evidence including:
    - candidate_matches: total raw cross-matches
    - verified_matches: spatially separated valid descriptor matches
    - geometric_cluster_evidence: vector consistency metrics and cluster details
    """
    h, w = cv_gray.shape[:2]
    max_score = 30
    vis = cv_bgr.copy()
    
    # 1. ORB Keypoint detection (up to 2000 features)
    orb = cv2.ORB_create(
        nfeatures=2000,
        scaleFactor=1.2,
        nlevels=8,
        edgeThreshold=15,
        fastThreshold=12
    )
    
    keypoints, descriptors = orb.detectAndCompute(cv_gray, None)
    
    if keypoints is None or descriptors is None or len(keypoints) < 15:
        vis_empty = encode_cv2_to_base64_data_uri(vis, "png")
        return {
            "score": 0,
            "max_score": max_score,
            "status": "INSUFFICIENT KEYPOINTS",
            "finding": "Image contains insufficient texture or keypoints for reliable feature matching.",
            "explanation": (
                "ORB feature extraction identified too few stable keypoints (e.g. due to smooth uniform colors "
                "or heavy blur). Copy-move analysis requires rich local feature descriptors."
            ),
            "metrics": {
                "keypoint_count": len(keypoints) if keypoints else 0,
                "candidate_matches": 0,
                "verified_matches": 0,
                "coherent_clusters": 0,
                "dominant_cluster_size": 0,
                "geometric_cluster_evidence": "Insufficient keypoints detected."
            },
            "visualization": vis_empty
        }

    # 2. Descriptor matching within the image
    # Query top 6 nearest neighbors for each descriptor
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
    raw_matches = bf.knnMatch(descriptors, descriptors, k=min(6, len(descriptors)))
    
    total_raw_candidates = sum(len(m) for m in raw_matches if m)

    # 3. Spatial & Descriptor Filtering
    min_spatial_distance = max(40.0, min(h, w) * 0.05)  # Spatial separation threshold
    max_hamming_dist = 36  # High-confidence descriptor match threshold
    
    valid_pairs = []
    seen_pairs = set()

    for m_list in raw_matches:
        if not m_list:
            continue
        query_idx = m_list[0].queryIdx
        pt1 = keypoints[query_idx].pt
        
        for m in m_list:
            train_idx = m.trainIdx
            # Filter self-match
            if query_idx == train_idx:
                continue
            pair_key = tuple(sorted((query_idx, train_idx)))
            if pair_key in seen_pairs:
                continue
            seen_pairs.add(pair_key)
            
            # Check descriptor distance
            if m.distance > max_hamming_dist:
                continue
                
            pt2 = keypoints[train_idx].pt
            
            # Compute Euclidean spatial distance
            dx = pt2[0] - pt1[0]
            dy = pt2[1] - pt1[1]
            dist_px = math.hypot(dx, dy)
            
            if dist_px < min_spatial_distance:
                # Discard touching / adjacent keypoints of the same contour
                continue
                
            # Canonicalize direction so dx > 0 (or dx == 0 and dy > 0)
            # This ensures translation vectors between source and destination align consistently
            p_src, p_dst = pt1, pt2
            if dx < 0 or (dx == 0 and dy < 0):
                dx = -dx
                dy = -dy
                p_src, p_dst = pt2, pt1
                
            angle_rad = math.atan2(dy, dx)
            valid_pairs.append({
                "pt1": p_src,
                "pt2": p_dst,
                "dx": dx,
                "dy": dy,
                "dist": dist_px,
                "angle": angle_rad,
                "hamming": m.distance
            })

    verified_matches_count = len(valid_pairs)

    # 4. Displacement Vector Clustering
    # In genuine cloning/copy-move, a region is translated by a uniform vector (dx, dy).
    # Natural repetitive textures (bricks, grass, waves) have scattered, random vectors.
    clusters = []
    vector_tolerance = max(18.0, min(h, w) * 0.03)  # Spatial displacement tolerance
    
    used_indices = set()
    for i, p1 in enumerate(valid_pairs):
        if i in used_indices:
            continue
        current_cluster = [p1]
        for j, p2 in enumerate(valid_pairs):
            if i == j or j in used_indices:
                continue
            
            # Direct canonical displacement vector difference
            diff = math.hypot(p1["dx"] - p2["dx"], p1["dy"] - p2["dy"])
            
            if diff < vector_tolerance:
                current_cluster.append(p2)
                used_indices.add(j)
                
        if len(current_cluster) >= 3:
            clusters.append(current_cluster)

    # Sort clusters by size
    clusters.sort(key=lambda c: len(c), reverse=True)
    dominant_cluster_size = len(clusters[0]) if clusters else 0

    # 5. Localized Cloning vs Repeated Natural Texture / Lattice Assessment
    dominant_ratio = (dominant_cluster_size / verified_matches_count) if verified_matches_count > 0 else 0

    # In genuine localized copy-move forgery, a prominent cluster captures a substantial fraction
    # of all matches, indicating a concentrated source-target translation.
    is_localized_cloning = (
        (dominant_cluster_size >= 40 and dominant_ratio >= 0.25 and len(clusters) < 50) or
        (dominant_cluster_size >= 120 and dominant_ratio >= 0.20)
    )

    # In repeated natural textures or lattices (e.g. brick walls, window grids, foliage),
    # matches form a large number of diffuse clusters with low concentration ratio.
    is_diffuse_periodic_texture = (not is_localized_cloning) and (
        len(clusters) >= 20 or
        (len(clusters) >= 8 and dominant_ratio < 0.15) or
        (len(clusters) >= 4 and dominant_cluster_size < 12)
    )

    # 6. Geometric Evidence Summary
    cluster_evidence_desc = []
    if clusters:
        top_c = clusters[0]
        mean_dx = float(np.mean([p["dx"] for p in top_c]))
        mean_dy = float(np.mean([p["dy"] for p in top_c]))
        mean_dist = float(np.hypot(mean_dx, mean_dy))
        cluster_evidence_desc.append(
            f"Dominant cluster contains {len(top_c)} verified pairs with mean displacement vector "
            f"({mean_dx:.1f}px, {mean_dy:.1f}px) across distance {mean_dist:.1f}px."
        )
    else:
        cluster_evidence_desc.append("No coherent geometric clusters formed among verified matches.")

    # 7. Visualization Generation
    if clusters and dominant_cluster_size >= 4 and not is_diffuse_periodic_texture:
        # Draw the top candidate clusters
        for cl_idx, cl in enumerate(clusters[:3]):
            pts1 = []
            pts2 = []
            for item in cl:
                p1 = (int(round(item["pt1"][0])), int(round(item["pt1"][1])))
                p2 = (int(round(item["pt2"][0])), int(round(item["pt2"][1])))
                pts1.append(p1)
                pts2.append(p2)
                
                # Connecting line (Primary Blue in BGR)
                cv2.line(vis, p1, p2, (235, 99, 37), 1, cv2.LINE_AA)
                # Source circle (Cyan in BGR)
                cv2.circle(vis, p1, 4, (178, 145, 8), -1, cv2.LINE_AA)
                cv2.circle(vis, p1, 5, (255, 255, 255), 1, cv2.LINE_AA)
                # Destination circle (Blue in BGR)
                cv2.circle(vis, p2, 4, (216, 78, 29), -1, cv2.LINE_AA)
                cv2.circle(vis, p2, 5, (255, 255, 255), 1, cv2.LINE_AA)

            # Draw bounding convex hulls around clustered source and target regions
            if len(pts1) >= 3:
                hull1 = cv2.convexHull(np.array(pts1))
                hull2 = cv2.convexHull(np.array(pts2))
                cv2.polylines(vis, [hull1], True, (178, 145, 8), 2, cv2.LINE_AA)
                cv2.polylines(vis, [hull2], True, (216, 78, 29), 2, cv2.LINE_AA)
    elif valid_pairs:
        # If no dense cluster, draw top subtle candidate pairs faintly
        for item in valid_pairs[:10]:
            p1 = (int(round(item["pt1"][0])), int(round(item["pt1"][1])))
            p2 = (int(round(item["pt2"][0])), int(round(item["pt2"][1])))
            cv2.line(vis, p1, p2, (210, 210, 210), 1, cv2.LINE_AA)
            cv2.circle(vis, p1, 3, (160, 160, 160), -1, cv2.LINE_AA)
            cv2.circle(vis, p2, 3, (160, 160, 160), -1, cv2.LINE_AA)

    # 8. Evaluation & Initial Evidence Weight
    if is_localized_cloning:
        status = "POSSIBLE DUPLICATED REGION"
        score = 22
        finding = f"Dense cluster of {dominant_cluster_size} spatially consistent keypoint pairs detected."
        explanation = (
            f"A prominent cluster of {dominant_cluster_size} feature matches shares a unified displacement vector. "
            "This geometric alignment strongly suggests a cloned or duplicated image patch, though natural repetitive textures "
            "(such as architectural tiling, windows, or repeated foliage) should be cross-examined."
        )
    elif is_diffuse_periodic_texture:
        status = "REPEATED NATURAL TEXTURE"
        score = 4
        finding = f"Diffuse periodic matching ({len(clusters)} scattered groups) consistent with natural repetitive patterns."
        explanation = (
            "Multiple small groups of matching features were detected across repetitive visual elements (e.g., windows, foliage, tiling). "
            "Because vectors are multidirectional across periodic structures, this indicates natural scene repetition rather than localized cloning."
        )
    elif dominant_cluster_size >= 12 and not is_diffuse_periodic_texture:
        status = "WEAK CLUSTER EVIDENCE"
        score = 8
        finding = f"Moderate grouping of {dominant_cluster_size} feature matches with similar displacement."
        explanation = (
            "A small cluster of similar feature descriptors was observed with comparable translation distances. "
            "Evidence is inconclusive and could correspond to either localized stamp cloning or regular geometric patterns."
        )
    else:
        status = "NO DUPLICATED REGIONS DETECTED"
        score = 0
        finding = "No statistically significant feature duplication clusters identified."
        explanation = (
            "Descriptor cross-matching did not discover coherent displacement vectors across spatially separated areas. "
            "Insufficient evidence of copy-move cloning."
        )

    vis_data_uri = encode_cv2_to_base64_data_uri(vis, "png")

    return {
        "score": score,
        "max_score": max_score,
        "status": status,
        "finding": finding,
        "explanation": explanation,
        "metrics": {
            "keypoints_detected": len(keypoints),
            "candidate_matches": total_raw_candidates,
            "verified_matches": verified_matches_count,
            "coherent_clusters": len(clusters),
            "dominant_cluster_size": dominant_cluster_size,
            "geometric_cluster_evidence": "; ".join(cluster_evidence_desc)
        },
        "visualization": vis_data_uri
    }
