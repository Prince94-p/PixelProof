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
        del vis
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

    # 6. RANSAC Geometric Verification (Affine-Partial: Scale + Rotation + Translation)
    # Evaluates whether feature matches adhere to a coherent geometric transformation,
    # enabling detection of cloned patches that have been rotated or scaled.
    ransac_model = "affine_partial"
    ransac_inliers = 0
    ransac_inlier_ratio = 0.0
    ransac_rotation_deg = 0.0
    ransac_scale = 1.0
    ransac_tx = 0.0
    ransac_ty = 0.0
    ransac_verified = False
    ransac_inlier_pairs = []

    # Test candidate pairs for RANSAC geometric consistency
    # We test either the dominant cluster or all verified pairs if clusters were fragmented by rotation/scaling
    candidate_pts_src = []
    candidate_pts_dst = []
    candidate_pair_refs = []

    if dominant_cluster_size >= 6:
        # Test dominant cluster pairs
        for p in clusters[0]:
            candidate_pts_src.append(p["pt1"])
            candidate_pts_dst.append(p["pt2"])
            candidate_pair_refs.append(p)
    elif len(valid_pairs) >= 8:
        # Test spatially separated valid pairs
        for p in valid_pairs[:120]:  # Cap to top matches for speed & robustness
            candidate_pts_src.append(p["pt1"])
            candidate_pts_dst.append(p["pt2"])
            candidate_pair_refs.append(p)

    if len(candidate_pts_src) >= 6:
        try:
            src_arr = np.array(candidate_pts_src, dtype=np.float32)
            dst_arr = np.array(candidate_pts_dst, dtype=np.float32)
            reproj_thresh = max(4.0, min(h, w) * 0.01)

            M_est, inliers_mask = cv2.estimateAffinePartial2D(
                src_arr, dst_arr,
                method=cv2.RANSAC,
                ransacReprojThreshold=reproj_thresh,
                maxIters=2000,
                confidence=0.99
            )

            if M_est is not None and inliers_mask is not None:
                inlier_indices = np.where(inliers_mask.ravel() == 1)[0]
                ransac_inliers = len(inlier_indices)
                ransac_inlier_ratio = ransac_inliers / float(len(candidate_pts_src))

                # Extract scale, rotation angle, and translation
                a = M_est[0, 0]
                b = M_est[1, 0]
                ransac_scale = float(np.sqrt(a * a + b * b))
                ransac_rotation_deg = float(np.degrees(np.arctan2(b, a)))
                ransac_tx = float(M_est[0, 2])
                ransac_ty = float(M_est[1, 2])
                t_dist = float(np.hypot(ransac_tx, ransac_ty))

                # Validate non-degeneracy:
                # - Reasonable scale (0.35x to 2.8x)
                # - Sufficient translation distance (> min_spatial_distance * 0.7)
                # - Sufficient inliers and ratio
                # - Spread of inliers across 2D plane (not collinear / point collapse)
                inlier_pts1 = [candidate_pts_src[idx] for idx in inlier_indices]
                inlier_pts2 = [candidate_pts_dst[idx] for idx in inlier_indices]

                box_w = max(p[0] for p in inlier_pts1) - min(p[0] for p in inlier_pts1) if inlier_pts1 else 0
                box_h = max(p[1] for p in inlier_pts1) - min(p[1] for p in inlier_pts1) if inlier_pts1 else 0
                is_spatially_spread = (box_w >= 20 or box_h >= 20)

                if (
                    0.35 <= ransac_scale <= 2.8
                    and t_dist >= (min_spatial_distance * 0.6)
                    and ransac_inliers >= 10
                    and ransac_inlier_ratio >= 0.18
                    and is_spatially_spread
                    and not is_diffuse_periodic_texture
                ):
                    ransac_verified = True
                    ransac_inlier_pairs = [candidate_pair_refs[idx] for idx in inlier_indices]
        except Exception:
            pass

    geometric_verification_info = {
        "performed": len(candidate_pts_src) >= 6,
        "model": ransac_model,
        "inliers": ransac_inliers,
        "total_matches": len(candidate_pts_src),
        "inlier_ratio": round(float(ransac_inlier_ratio), 3),
        "rotation_degrees": round(float(ransac_rotation_deg), 1),
        "scale": round(float(ransac_scale), 2),
        "translation_x": round(float(ransac_tx), 1),
        "translation_y": round(float(ransac_ty), 1),
        "verified": ransac_verified
    }

    # 7. Geometric Evidence Summary
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

    if ransac_verified:
        cluster_evidence_desc.append(
            f"RANSAC geometric verification confirmed affine correspondence with {ransac_inliers} inliers "
            f"(rotation: {ransac_rotation_deg:.1f}°, scale: {ransac_scale:.2f}x)."
        )

    # 8. Visualization Generation
    rendered_visual = False
    if clusters and dominant_cluster_size >= 4 and not is_diffuse_periodic_texture:
        rendered_visual = True
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

    elif ransac_verified and ransac_inlier_pairs:
        rendered_visual = True
        pts1 = []
        pts2 = []
        for item in ransac_inlier_pairs:
            p1 = (int(round(item["pt1"][0])), int(round(item["pt1"][1])))
            p2 = (int(round(item["pt2"][0])), int(round(item["pt2"][1])))
            pts1.append(p1)
            pts2.append(p2)
            cv2.line(vis, p1, p2, (235, 99, 37), 1, cv2.LINE_AA)
            cv2.circle(vis, p1, 4, (178, 145, 8), -1, cv2.LINE_AA)
            cv2.circle(vis, p1, 5, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.circle(vis, p2, 4, (216, 78, 29), -1, cv2.LINE_AA)
            cv2.circle(vis, p2, 5, (255, 255, 255), 1, cv2.LINE_AA)

        if len(pts1) >= 3:
            hull1 = cv2.convexHull(np.array(pts1))
            hull2 = cv2.convexHull(np.array(pts2))
            cv2.polylines(vis, [hull1], True, (178, 145, 8), 2, cv2.LINE_AA)
            cv2.polylines(vis, [hull2], True, (216, 78, 29), 2, cv2.LINE_AA)

    elif valid_pairs and not rendered_visual:
        # If no dense cluster, draw top subtle candidate pairs faintly
        for item in valid_pairs[:10]:
            p1 = (int(round(item["pt1"][0])), int(round(item["pt1"][1])))
            p2 = (int(round(item["pt2"][0])), int(round(item["pt2"][1])))
            cv2.line(vis, p1, p2, (210, 210, 210), 1, cv2.LINE_AA)
            cv2.circle(vis, p1, 3, (160, 160, 160), -1, cv2.LINE_AA)
            cv2.circle(vis, p2, 3, (160, 160, 160), -1, cv2.LINE_AA)

    # 9. Evaluation & Initial Evidence Weight
    is_transformed_cloning = ransac_verified and (abs(ransac_rotation_deg) >= 8.0 or abs(ransac_scale - 1.0) >= 0.12)

    if is_localized_cloning:
        status = "POSSIBLE DUPLICATED REGION"
        score = 24 if ransac_verified else 22
        finding = f"Dense cluster of {dominant_cluster_size} spatially consistent keypoint pairs detected."
        explanation = (
            f"A prominent cluster of {dominant_cluster_size} feature matches shares a unified displacement vector. "
            "This geometric alignment strongly suggests a cloned or duplicated image patch, though natural repetitive textures "
            "(such as architectural tiling, windows, or repeated foliage) should be cross-examined."
        )
        if ransac_verified:
            explanation += f" RANSAC verified affine consistency with {ransac_inliers} inliers."
    elif is_transformed_cloning:
        status = "POSSIBLE DUPLICATED REGION"
        score = 22
        finding = (
            f"Transformed duplicated region verified via RANSAC ({ransac_inliers} inliers, "
            f"rotation: {ransac_rotation_deg:.1f}°, scale: {ransac_scale:.2f}x)."
        )
        explanation = (
            f"Geometric verification confirmed {ransac_inliers} feature correspondences aligned under affine transformation "
            f"(rotation: {ransac_rotation_deg:.1f}°, scale: {ransac_scale:.2f}x). This indicates a cloned patch with rotation or scaling."
        )
    elif is_diffuse_periodic_texture:
        status = "REPEATED NATURAL TEXTURE"
        score = 4
        finding = f"Diffuse periodic matching ({len(clusters)} scattered groups) consistent with natural repetitive patterns."
        explanation = (
            "Multiple small groups of matching features were detected across repetitive visual elements (e.g., windows, foliage, tiling). "
            "Because vectors are multidirectional across periodic structures, this indicates natural scene repetition rather than localized cloning."
        )
    elif (dominant_cluster_size >= 12 or (ransac_verified and ransac_inliers >= 8)) and not is_diffuse_periodic_texture:
        status = "WEAK CLUSTER EVIDENCE"
        score = 8
        finding = f"Moderate grouping of {max(dominant_cluster_size, ransac_inliers)} feature matches with similar displacement."
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

    score = min(max_score, max(0, score))
    vis_data_uri = encode_cv2_to_base64_data_uri(vis, "png")
    del vis

    return {
        "score": score,
        "max_score": max_score,
        "status": status,
        "finding": finding,
        "explanation": explanation,
        "geometric_verification": geometric_verification_info,
        "metrics": {
            "keypoints_detected": len(keypoints),
            "candidate_matches": total_raw_candidates,
            "verified_matches": verified_matches_count,
            "coherent_clusters": len(clusters),
            "dominant_cluster_size": dominant_cluster_size,
            "geometric_cluster_evidence": "; ".join(cluster_evidence_desc),
            "ransac_inliers": ransac_inliers,
            "ransac_rotation_deg": round(float(ransac_rotation_deg), 1),
            "ransac_scale": round(float(ransac_scale), 2),
            "ransac_verified": ransac_verified,
            "geometric_verification": geometric_verification_info
        },
        "visualization": vis_data_uri
    }
