# Caravel PLL configuration generator

This tool generates a PLL clock configuration for the Caravel management core.

The PLL multiplies clkin with the feedback divisor register.

```
clkin -> PLL -> no phase shift -> output divisor 1 -> clkout
             \> phase shift 90 -> output divisor 2 -> clkout90
```

Simple example:
```
$ python caravel_pll.py --clkin 16 --clkout 48
PLL Parameters:

clkin:    16.00 MHz
clkout:   48.00 MHz
clkout90: 48.00 MHz

PLL Feedback Divider: 9
PLL Output Divider 1: 3
PLL Output Divider 2: 3

Register 0x11: 0x1b
Register 0x12: 0x09
```

More complex example where clkout90 will deviate from the requested config:
```
$ python caravel_pll.py --clkin 16 --clkout 48 --clkout90 90 --allow-deviation
PLL Parameters:

clkin:    16.00 MHz
clkout:   48.00 MHz
clkout90: 88.00 MHz

PLL Feedback Divider: 9
PLL Output Divider 1: 3
PLL Output Divider 2: 2

Register 0x11: 0x13
Register 0x12: 0x09
```

JSON output is also supported:
```
$ python caravel_pll.py --clkin 16 --clkout 48 --clkout90 90 --allow-deviation --json | jq
{
  "clkin": 16,
  "clkout": 48,
  "clkout90": 88,
  "fbdiv": 9,
  "div1": 3,
  "div2": 2,
  "reg0x11": 19,
  "reg0x12": 9
}
```

## License

The project is licensed under Apache 2.0
