# Soundness Bound Script

This repository contains a Python script for computing a concrete Elias-bound soundness estimate.

The script is called:

```bash
soundness.py
```

## Requirements

You need Python 3 installed.

Check that Python is available:

```bash
python3 --version
```

The script only uses the Python standard library, so no extra dependencies are required.

## Run with default parameters

From the repository root, run:

```bash
python3 soundness.py
```

## Optional: make it executable

The script starts with:

```python
#!/usr/bin/env python3
```

So you can make it executable:

```bash
chmod +x soundness.py
```

Then run it directly:

```bash
./soundness.py
```

## Command-line options

You can customize the computation using command-line arguments.

### Set `n` and `k`

```bash
python3 soundness.py --n 2097152 --k 1048576
```

### Set `t` manually

```bash
python3 soundness.py --t 128
```

If `--t` is omitted or set to `0`, the script automatically chooses `t` for supported rates.

### Increase grid-search precision

```bash
python3 soundness.py --steps 10000
```

The default is:

```text
steps = 2000
```

Higher values may give a more accurate result, but the script will take longer to run.

## Field presets

Use Koala defaults:

```bash
python3 soundness.py --koala
```

Use M31:

```bash
python3 soundness.py --M31
```

Use Goldilocks:

```bash
python3 soundness.py --goldilocks
```

Use BabyBear:

```bash
python3 soundness.py --babybear
```

Use Fermat:

```bash
python3 soundness.py --fermat
```

Only one field preset should be used at a time.

## Override field parameters manually

You can override the base field size `q_B` and extension degree `e`:

```bash
python3 soundness.py --qB 2147483647 --e 4
```

## Example

```bash
python3 soundness.py --n 2097152 --k 1048576 --t 128 --steps 5000 --koala
```

Example output:

```text
q_B 2130706433
e 5
rate 0.5
t 128
best delta 0.12345
soundeness -82.731
```

The final `soundeness` value is the base-2 logarithm of the soundness estimate:

```text
soundness ≈ 2^soundeness
```

For example, if the script prints:

```text
soundeness -80
```

then the estimated bound is approximately:

```text
2^-80
```

## Automatic `t` selection

If `--t` is omitted or set to `0`, the script chooses `t` based on the code rate `rho = k / n`.

The supported rates are:

```text
rho = 1/2   -> t = 128
rho = 1/4   -> t = 64
rho = 1/8   -> t = 43
rho = 1/16  -> t = 32
```

For other rates, pass `--t` explicitly.

Example:

```bash
python3 soundness.py --n 1024 --k 768 --t 128
```

## Notes

- All large quantities are handled in log-space.
- The script performs a grid search over `delta`.
- The `--steps` argument controls the grid-search resolution.
- Use only one field preset at a time.
- The output label `soundeness` is currently printed by the script as written.
