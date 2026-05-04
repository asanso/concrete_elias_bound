#!/usr/bin/env python3
import math
import argparse

# ---------- Defaults (Koala-style) ----------

# Base field B = F_q with q = 2^31 - 2^24 + 1
q_B = 2**31 - 2**24 + 1
# Default extension degree e; using 5
e = 5  # extension degree, |F| = |B|^e

ln_qB = math.log(q_B)          # ln(|B|)
ln_F = e * ln_qB               # ln(|F|) = ln(|B|^e)


def H_q(delta: float, q: int) -> float:
    """
    q-ary entropy H_q(delta):

        H_q(x) = x * log_q(q - 1) - x * log_q(x) - (1 - x) * log_q(1 - x)

    implemented using natural logs (then divided by ln(q)).
    """
    if not (0.0 < delta < 1.0):
        raise ValueError("delta must be in (0,1)")

    ln_q = math.log(q)
    term1 = delta * (math.log(q - 1) - math.log(delta))
    term2 = (1.0 - delta) * math.log(1.0 - delta)
    # divide by ln(q) to get log base q
    return (term1 - term2) / ln_q


def ln_elias_list_size(n: int, k: int, delta: float) -> float:
    """
    Natural log of the Elias/entropy-based lower bound on |Λ(C_B, δ)|:

        |Λ(C_B, δ)| >= |B|^{ n(ρ - 1 + H_{|B|}(δ)) } / sqrt(8 n δ (1-δ))

    returns ln(|Λ(C_B, δ)|) using logs only (no huge exponentiation).
    """
    rho = k / n
    H = H_q(delta, q_B)                           # H_{|B|}(δ)
    exponent = n * (rho - 1.0 + H)                # exponent in base |B|
    ln_num = exponent * ln_qB                     # ln(|B|^{exponent})
    ln_den = 0.5 * math.log(8.0 * n * delta * (1.0 - delta))
    return ln_num - ln_den                        # ln(L)


def logaddexp(a: float, b: float) -> float:
    """
    Stable computation of ln(exp(a) + exp(b)).
    """
    if a > b:
        return a + math.log1p(math.exp(b - a))
    else:
        return b + math.log1p(math.exp(a - b))


def ln_soundness_delta(n: int, k: int, delta: float, t: int) -> float:
    """
    Natural log of the soundness lower bound for a fixed δ:

      soundness(δ) >= L / (|F| + L - 1) * (1 - δ)^t

    where L is the Elias-based lower bound on |Λ(C, δ)|.
    All done in log-space.
    """
    ln_L = ln_elias_list_size(n, k, delta)

    # ln(|F| + L - 1) ≈ ln(exp(ln_F) + exp(ln_L))
    ln_D = logaddexp(ln_F, ln_L)  # -1 negligible at this scale

    ln_first = ln_L - ln_D
    ln_second = t * math.log(1.0 - delta)
    return ln_first + ln_second   # ln(soundness)


def maximize_ln_soundness(n: int, k: int, t: int, steps: int = 2000):
    """
    Grid search over δ ∈ (0,1) to approximate:

        max_{δ ∈ (0,1)} ln(soundness(δ))

    Returns (best_delta, best_ln_soundness).
    """
    best_delta = None
    best_ln_val = -math.inf

    eps = 1e-4
    for i in range(1, steps):
        delta = eps + (1.0 - 2.0 * eps) * (i / steps)
        try:
            ln_val = ln_soundness_delta(n, k, delta, t)
        except ValueError:
            continue
        if ln_val > best_ln_val:
            best_ln_val = ln_val
            best_delta = delta

    return best_delta, best_ln_val


def auto_t_for_rate(rho: float) -> int:
    """
    Choose t depending on the rate rho:
      - rho = 1/2  -> t = 128
      - rho = 1/4  -> t = 64
      - rho = 1/8  -> t = 43
      - rho = 1/16 -> t = 32
    """
    eps = 1e-9
    if abs(rho - 1/2) < eps:
        return 128
    if abs(rho - 1/4) < eps:
        return 64
    if abs(rho - 1/8) < eps:
        return 43
    if abs(rho - 1/16) < eps:
        return 32
    raise ValueError(f"no automatic t configured for rate rho = {rho}")


def main():
    global q_B, e, ln_qB, ln_F

    parser = argparse.ArgumentParser(
        description="Concrete Elias-bound soundness: outputs delta* and log2(soundness)."
    )
    parser.add_argument(
        "--n", type=int, default=2**21,
        help="Block length n (default: 2^21)"
    )
    parser.add_argument(
        "--k", type=int, default=2**20,
        help="Dimension k (default: 2^20)"
    )
    parser.add_argument(
        "--t", type=int, default=0,
        help="Number of checks t; if 0, choose t from the rate (default: 0 = auto)"
    )
    parser.add_argument(
        "--steps", type=int, default=2000,
        help="Grid steps over δ (default: 2000)"
    )
    parser.add_argument(
        "--qB", type=int, default=None,
        help="Override base field size |B|"
    )
    parser.add_argument(
        "--e", type=int, default=None,
        help="Override extension degree e"
    )
    parser.add_argument(
        "--koala", action="store_true",
        help="Use Koala defaults for q_B and e (q_B = 2^31 - 2^24 + 1, e = 5)"
    )
    parser.add_argument(
        "--M31", action="store_true",
        help="Use M31 for q_B (q_B = 2^32 - 1)"
    )
    parser.add_argument(
        "--goldilocks", action="store_true",
        help="Use Goldilocks prime for q_B (q_B = 2^64 - 2^32 + 1)"
    )
    parser.add_argument(
        "--babybear", action="store_true",
        help="Use babybear prime for q_B (q_B = 2^31 - 2^27 + 1)"
    )
    parser.add_argument(
        "--fermat", action="store_true",
        help="Use Fermat prime for q_B (q_B = 2^16 + 1)"
    )

    args = parser.parse_args()
    n, k, t, steps = args.n, args.k, args.t, args.steps

    # ----- configure q_B and e -----
    preset_flags = [args.koala, args.M31, args.goldilocks, args.babybear, args.fermat]
    if sum(bool(f) for f in preset_flags) > 1:
        raise ValueError("Use at most one of --koala, --M31, --goldilocks, --babybear, --fermat")

    if args.koala:
        q_B = 2**31 - 2**24 + 1
        e = 5
    else:
        if args.M31:
            q_B = 2**32 - 1  # M31
        if args.goldilocks:
            q_B = 2**64 - 2**32 + 1  # Goldilocks
        if args.babybear:
            q_B = 2**31 - 2**27 + 1  # babybear
        if args.fermat:
            q_B = 2**16 + 1  # Fermat prime
        if args.qB is not None:
            q_B = args.qB
        if args.e is not None:
            e = args.e

    # Recompute logs after any override
    ln_qB = math.log(q_B)
    ln_F = e * ln_qB

    rho = k / n

    # Auto-select t if not provided (t <= 0)
    if t <= 0:
        t = auto_t_for_rate(rho)

    best_delta, best_ln_sound = maximize_ln_soundness(n, k, t, steps)

    # Convert ln(soundness) to base-2 exponent: soundness ≈ 2^exp2
    exp2 = best_ln_sound / math.log(2.0)

    print("q_B", q_B)
    print("e", e)
    print("rate", rho)
    print("t", t)
    print("best delta", best_delta)
    print("soundeness", exp2)


if __name__ == "__main__":
    main()
