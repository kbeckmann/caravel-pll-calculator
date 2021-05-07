# Caravel PLL configuration generator

This tool generates a PLL clock configuration for the Caravel management core.

The PLL multiplies clkin with the feedback divisor register.

```
clkin -> PLL -> no phase shift -> output divisor 1 -> clkout
             \> phase shift 90 -> output divisor 2 -> clkout90
```

Simple example:
```
$ python caravel_pll.py generate --clkin 16 --clkout 48
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
$ python caravel_pll.py generate --clkin 16 --clkout 48 --clkout90 90 --allow-deviation
PLL Parameters:

clkin:    16.00 MHz
clkout:   48.00 MHz
clkout90: 72.00 MHz

PLL Feedback Divider: 9
PLL Output Divider 1: 3
PLL Output Divider 2: 2

Register 0x11: 0x13
Register 0x12: 0x09
```

JSON output is also supported:
```
$ python caravel_pll.py generate --clkin 16 --clkout 48 --clkout90 90 --allow-deviation --json | jq
{
  "clkin": 16,
  "clkout": 48,
  "clkout90": 72,
  "fbdiv": 9,
  "div1": 3,
  "div2": 2,
  "reg0x11": 19,
  "reg0x12": 9
}
```

You can also list valid configurations for a given input clock frequency:
```
$ python caravel_pll.py list --clkin 48
clkout		fbdiv	div	pllfreq
  13.714 MHz	2	7	 96.0 MHz
  16.000 MHz	2	6	 96.0 MHz
  19.200 MHz	2	5	 96.0 MHz
  20.571 MHz	3	7	144.0 MHz
  24.000 MHz	2	4	 96.0 MHz
  24.000 MHz	3	6	144.0 MHz
  27.429 MHz	4	7	192.0 MHz
  28.800 MHz	3	5	144.0 MHz
  32.000 MHz	2	3	 96.0 MHz
  32.000 MHz	4	6	192.0 MHz
  36.000 MHz	3	4	144.0 MHz
  38.400 MHz	4	5	192.0 MHz
  48.000 MHz	2	2	 96.0 MHz
  48.000 MHz	3	3	144.0 MHz
  48.000 MHz	4	4	192.0 MHz
  64.000 MHz	4	3	192.0 MHz
  72.000 MHz	3	2	144.0 MHz
  96.000 MHz	2	1	 96.0 MHz
  96.000 MHz	4	2	192.0 MHz
 144.000 MHz	3	1	144.0 MHz
 192.000 MHz	4	1	192.0 MHz
```

## License

The project is licensed under Apache 2.0
