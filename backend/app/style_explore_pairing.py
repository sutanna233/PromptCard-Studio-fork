"""Fixed artists and exhaustive one-partner rounds for style exploration."""

from __future__ import annotations

import math
import random
from dataclasses import replace

from . import style_explore_algorithm as algorithm


def normalize_options(raw: dict) -> dict:
    mode = raw.get("pairing_mode", "random")
    if mode not in {"random", "sequential"}:
        raise ValueError("搭配模式必须是 random 或 sequential")
    if raw.get("seed_mode", "increment") not in {"increment", "fixed"}:
        raise ValueError("种子模式必须是 increment 或 fixed")
    entries = raw.get("fixed_artists", [])
    if not isinstance(entries, list) or len(entries) > 29:
        raise ValueError("固定画师必须为列表，最多 29 个")
    fixed = []
    seen = set()
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("id"), str):
            raise ValueError("每个固定画师必须填写 ID 和权重")
        artist_id = entry["id"].strip()
        if not artist_id or any(char in artist_id for char in "\r\n,") or "::" in artist_id:
            raise ValueError("固定画师 ID 不能为空，也不能包含逗号、换行或权重语法")
        if artist_id in seen:
            raise ValueError(f"固定画师重复：{artist_id}")
        try:
            weight = float(entry.get("weight", 0.8))
        except (ValueError, TypeError) as exc:
            raise ValueError("固定画师权重必须是 -3 到 3 的有限数字") from exc
        if not math.isfinite(weight) or not -3 <= weight <= 3:
            raise ValueError("固定画师权重必须是 -3 到 3 的有限数字")
        if abs(weight * 10 - round(weight * 10)) > 1e-8:
            raise ValueError("固定画师权重必须以 0.1 为步长")
        seen.add(artist_id)
        fixed.append({"id": artist_id, "weight": weight})
    try:
        samples = int(raw.get("samples_per_artist", 1))
    except (ValueError, TypeError, OverflowError) as exc:
        raise ValueError("每位搭配画师的图片数必须为 1 到 20 的整数") from exc
    if not 1 <= samples <= 20 or samples != raw.get("samples_per_artist", 1):
        raise ValueError("每位搭配画师的图片数必须为 1 到 20 的整数")
    return {**raw, "fixed_artists": fixed, "pairing_mode": mode, "samples_per_artist": samples, "seed_mode": raw.get("seed_mode", "increment")}


def freeze_comparison_seed(options: dict, params: dict) -> dict:
    options = dict(options)
    if options["seed_mode"] == "fixed":
        base_seed = int(params.get("seed", -1))
        options["comparison_seed"] = base_seed if base_seed >= 0 else random.SystemRandom().randrange(2**32)
    else:
        options.pop("comparison_seed", None)
    return options


def partner_pool(pool: list[str], options: dict) -> list[str]:
    fixed_ids = {entry["id"] for entry in options["fixed_artists"]}
    partners = [artist_id for artist_id in pool if artist_id not in fixed_ids]
    if not partners:
        raise ValueError("排除固定画师后，ArtistPool 没有可搭配的画师")
    return partners


def round_count(pool: list[str], requested: int, options: dict) -> int:
    if options["pairing_mode"] != "sequential":
        return requested
    count = len(partner_pool(pool, options)) * options["samples_per_artist"]
    if count > 1000:
        raise ValueError(f"逐个搭配需生成 {count} 张，超过每轮 1000 张上限；请减少画师池或每位图片数")
    return count


def fixed_weights(options: dict) -> tuple[algorithm.ArtistWeight, ...]:
    return tuple(algorithm.ArtistWeight(entry["id"], entry["weight"]) for entry in options["fixed_artists"])


def generate_basic(pool, minimum, count, config, rng, maximum, options):
    partners = partner_pool(pool, options)
    fixed = fixed_weights(options)
    if not 1 <= maximum <= algorithm.MAX_ARTIST_COUNT - len(fixed):
        raise ValueError("固定画师与最多搭配画师之和不能超过 30")
    if options["pairing_mode"] == "sequential":
        # Exactly one partner per image, exhaustively in the saved pool order.
        expected = round_count(pool, count, options)
        if count != expected:
            raise ValueError("逐个搭配的图片数与画师池不一致")
        candidates = [
            algorithm.generate_basic_candidate([artist_id], 1, config, rng, 1)
            for artist_id in partners
            for _ in range(options["samples_per_artist"])
        ]
    else:
        candidates = algorithm.generate_basic_candidates(partners, minimum, count, config, rng, maximum)
    return [
        algorithm.BasicCandidate(fixed + candidate.artist_weights, algorithm.build_artist_string(fixed + candidate.artist_weights))
        for candidate in candidates
    ]


def generate_deep(parents, pool, count, config, rng, maximum, options):
    fixed = fixed_weights(options)
    if not 1 <= maximum <= algorithm.MAX_ARTIST_COUNT - len(fixed):
        raise ValueError("固定画师与最多搭配画师之和不能超过 30")
    fixed_ids = {item.artist_id for item in fixed}
    variable_parents = [
        replace(parent, artist_weights=tuple(item for item in parent.artist_weights if item.artist_id not in fixed_ids))
        for parent in parents
    ]
    candidates = algorithm.generate_deep_candidates(variable_parents, partner_pool(pool, options), count, config, rng, maximum)
    return [
        replace(candidate, artist_weights=fixed + candidate.artist_weights,
                artist_string=algorithm.build_artist_string(fixed + candidate.artist_weights))
        for candidate in candidates
    ]
