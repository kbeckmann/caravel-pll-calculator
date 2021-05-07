# SPDX-License-Identifier: Apache-2.0
# Copyright 2021 Konrad Beckmann

import argparse
import sys
import json

"""

This tool generates a PLL clock configuration for the Caravel management core.

The PLL multiplies clkin with the feedback divisor register.

clkin -> PLL -> no phase shift -> output divisor 1 -> clkout
             \> phase shift 90 -> output divisor 2 -> clkout90

"""


VERBOSE = False

def vprint(*args, **kwargs):
    if VERBOSE:
        print(*args, **kwargs)

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def generate_pll(clkin, clkout, pll_low_limit, pll_high_limit, multiplier=0, allow_deviation=False):
    configs = []
    ideal_configs = []
    m_min = 1
    m_max = 2**5

    if multiplier != 0:
        m_min = multiplier
        m_max = multiplier + 1

    # Iterate over the valid feedback divisor values
    for m in range(m_min, m_max):
        multiplied = clkin * m
        if (multiplied < pll_low_limit or multiplied > pll_high_limit):
            continue
        for d in range(1, 2**3):
            divided = multiplied / d
            deviation = divided - clkout
            configs.append({"m":m, "d":d, "deviation": deviation})
            if divided == clkout:
                ideal_configs.append({"m":m, "d":d})
                vprint(f"Found a config without deviation: m={m}, d={d}")

    # Find the config where the multiplied frequency is closest to the center of the pll limits
    best_config = None
    best_freq = 1e9
    center_freq = pll_low_limit + (pll_high_limit - pll_low_limit) / 2
    for c in ideal_configs:
        freq = c["m"] * clkin
        if abs(freq - center_freq) < abs(best_freq - center_freq):
            vprint(f"Found a better config: m={c['m']}, d={c['d']}, pllfreq={freq}")
            best_config = c
            best_freq = freq

    # If deviation is allowed, find the config with the lowest.
    if best_config == None and allow_deviation:
        best_deviation = 1e9
        for c in configs:
            freq = c["m"] * clkin / c["d"]
            deviation = abs(freq - clkout)
            if deviation < best_deviation:
                vprint(f"Found a better deviating config: m={c['m']}, d={c['d']}, deviation={freq}")
                best_config = c
                best_deviation = deviation

    return best_config

def generate_config(args):
    clkin = args.clkin
    clkout = args.clkout
    clkout90 = clkout if not args.clkout90 else args.clkout90
    pll_low_limit = args.pll_low_limit
    pll_high_limit = args.pll_high_limit
    allow_deviation = args.allow_deviation

    clkout_conf = generate_pll(clkin, clkout, pll_low_limit, pll_high_limit, allow_deviation=allow_deviation)
    if clkout_conf == None:
        eprint("Failed to find a configuration for clkout")
        exit(1)

    clkout90_conf = generate_pll(clkin, clkout90, pll_low_limit, pll_high_limit, multiplier=clkout_conf["m"], allow_deviation=allow_deviation)
    if clkout90_conf == None:
        eprint("Failed to find a configuration for clkout90")
        exit(1)

    reg0x11 = (clkout_conf["d"] & 0b111) | ((clkout90_conf["d"] & 0b111) << 3)
    reg0x12 = (clkout_conf["m"] & 0b11111)

    if args.json:
        print(json.dumps({
            "clkin":    clkin,
            "clkout":   args.clkin * clkout_conf["m"] / clkout_conf["d"],
            "clkout90": args.clkin * clkout90_conf["m"] / clkout90_conf["d"],
            "fbdiv":    clkout_conf["m"],
            "div1":     clkout_conf["d"],
            "div2":     clkout90_conf["d"],
            "reg0x11":  reg0x11,
            "reg0x12":  reg0x12,
        }))
    else:
        print(f"""PLL Parameters:

clkin:    {args.clkin:#.2f} MHz
clkout:   {(args.clkin * clkout_conf["m"] / clkout_conf["d"]):#.2f} MHz
clkout90: {(args.clkin * clkout90_conf["m"] / clkout90_conf["d"]):#.2f} MHz

PLL Feedback Divider: {clkout_conf["m"]}
PLL Output Divider 1: {clkout_conf["d"]}
PLL Output Divider 2: {clkout90_conf["d"]}

Register 0x11: {reg0x11:#04x}
Register 0x12: {reg0x12:#04x}""")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate a PLL configuration for the Caravel management core. All frequencies are specified in MHz.')
    parser = argparse.ArgumentParser()
    parser.add_argument('--clkin', '-i',     type=float, default=10,             help='Frequency (MHz) of the input clock')
    parser.add_argument('--clkout', '-o',    type=float, required=True,          help='Frequency (MHz) of the first output clock')
    parser.add_argument('--clkout90',        type=float,                         help='Frequency (MHz) of the second, 90 degrees phase shifted, output clock')
    parser.add_argument('--allow-deviation', action='store_true', default=False, help='Allow deviation from the requested frequencies')
    parser.add_argument('--pll-low-limit',   type=float, default=90,             help='Low limit of the allowed PLL output frequency')
    parser.add_argument('--pll-high-limit',  type=float, default=214,            help='High limit of the allowed PLL output frequency')
    parser.add_argument('--json',            action='store_true', default=False, help='Output as JSON')
    parser.add_argument('--verbose',         action='store_true', default=False, help='Enable verbose prints')
    args = parser.parse_args()

    VERBOSE = args.verbose

    generate_config(args)
