# Lembrent

***Lembrent*** is a system for naming and drawing base-60 (***Lembrent-60***)
and base-64 (***Lembrent-64***) numbers.

`lembrent` is a command-line Perl utility that converts non-negative integers
into their spoken names under the *Lembrent-60* and *Lembrent-64*
number-naming schemes—these schemes constitute a novel, positional, phonetically
encoded representation of base-60 and base-64 numbers.

The Lembrent system also specifies glyphs for each base-60 and base-64 digit.
The glyph generation is outside of the scope of this utility.  More information
about the glyph generation can be found at
[github.com/Warwick-Allen/base60/glyphs].

---

## Table of Contents

- [Lembrent](#lembrent)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [The Lembrent Number-Naming Scheme](#the-lembrent-number-naming-scheme)
    - [The Consonant Bit Map](#the-consonant-bit-map)
    - [Digit Structure](#digit-structure)
    - [Multi-Digit Numbers: Length Digits and Significant Digits](#multi-digit-numbers-length-digits-and-significant-digits)
    - [The Zero Digit](#the-zero-digit)
    - [Single-Digit Numbers and the Optional Length Digit](#single-digit-numbers-and-the-optional-length-digit)
    - [Digit Reference Table](#digit-reference-table)
    - [Pronunciation](#pronunciation)
      - [Letter Sounds](#letter-sounds)
      - [Syllable Structure](#syllable-structure)
      - [Clarity of Consonants](#clarity-of-consonants)
      - [Consonant Clusters](#consonant-clusters)
      - [Vowel Tolerance](#vowel-tolerance)
      - [Consonant Tolerance](#consonant-tolerance)
  - [The `lembrent` Utility](#the-lembrent-utility)
    - [Requirements](#requirements)
    - [Usage](#usage)
      - [Synopsis](#synopsis)
      - [Arguments](#arguments)
    - [Examples](#examples)
      - [Base-60 Examples](#base-60-examples)
      - [Base-64 Examples](#base-64-examples)
      - [Step-by-Step Worked Example: 70 in Lembrent-60](#step-by-step-worked-example-70-in-lembrent-60)
    - [Installation](#installation)
    - [How It Works (Implementation Notes)](#how-it-works-implementation-notes)
  - [Licence](#licence)

---

## Overview

`lembrent` is a Perl script that accepts a base (60 or 64) and one or more
non-negative integers, then prints the Lembrent name for each number.  The
scheme is designed so that the value of any digit can be computed directly from
the consonants present in its name, making it both human-pronounceable and
algorithmically unambiguous.

---

## The Lembrent Number-Naming Scheme

### The Consonant Bit Map

The name **"lembrent"** itself encodes the scheme: each of the six consonants in
the word carries a unique, fixed bit value.  The two vowels (`e`) serve purely
as phonetic scaffolding and carry no numerical value.

| Consonant | Bit position | Decimal value |
|-----------|-------------|---------------|
| `l`       | 2⁵          | 32            |
| `m`       | 2⁴          | 16            |
| `b`       | 2³          | 8             |
| `r`       | 2²          | 4             |
| `n`       | 2¹          | 2             |
| `t`       | 2⁰          | 1             |

The value of a digit is the **sum of the bit values of all consonants present**
in its name.  Because these six bits together span values 0–63, the scheme
naturally supports bases up to 64.

### Digit Structure

Every digit follows a strict template derived from the word **"lembrent"**:

```
[l] e [m] [b] [r] e [n] [t]
```

- The two `e` vowels are always present as fixed positional markers.
- `l` (when present) precedes the first `e`.
- `m`, `b`, and `r` appear between the two `e` vowels.
- `n` and `t` follow the second `e`.
- Consonants are always written in the fixed order `l`, `m`, `b`, `r`, `n`, `t`;
  a consonant is simply omitted when its bit is not set.

**Example:**
The digit `leme` has value 2⁵ + 2⁴ = 48.  It contains `l` (32) and `m` (16), but
not `b`, `r`, `n`, or `t`.

**Example:**
The digit `emrent` has value 2⁴ + 2² + 2¹ + 2⁰ = 16 + 4 + 2 + 1 = 23.

### Multi-Digit Numbers: Length Digits and Significant Digits

A Lembrent number name is composed of two parts:

1. **A length digit** —
   a single Lembrent digit, prefixed with a base indicator, that encodes how
   many significant digits follow.
2. **The significant digits** —
   the actual base-60 or base-64 digits of the number, each prefixed with a
   hyphen (`-`).

The base indicator prefix is:

| Base | Prefix |
|------|--------|
| 60   | `s`    |
| 64   | `k`    |

**Structure of a full Lembrent number name:**

```
<base-prefix><length-digit>-<digit₁>-<digit₂>-...-<digitₙ>
```

Where `<digit₁>` is the most significant digit and `<digitₙ>` is the least
significant digit (units).

### The Zero Digit

A digit with value zero is written as `ee`: the two vowels with no consonants
present.

### Single-Digit Numbers and the Optional Length Digit

For numbers whose value is less than 64 (i.e., numbers that require only a
single significant digit), the length digit is **optional**.  Such a number may
be written either in full multi-digit form or as a bare digit name.

The number zero may be written in any of the following ways:

- `see` (Lembrent-60: a zero length digit with no significant digits)
- `kee` (Lembrent-64: a zero length digit with no significant digits)
- `ee` (bare, base-agnostic)

### Digit Reference Table

The following table lists all 64 possible digit values and their Lembrent names.

| Value | Name       | Value | Name       | Value | Name       | Value | Name       |
|-------|------------|-------|------------|-------|------------|-------|------------|
| 0     | `ee`       | 16    | `eme`      | 32    | `le`       | 48    | `leme`     |
| 1     | `eet`      | 17    | `emet`     | 33    | `leet`     | 49    | `lemet`    |
| 2     | `een`      | 18    | `emen`     | 34    | `leen`     | 50    | `lemen`    |
| 3     | `eent`     | 19    | `ement`    | 35    | `leent`    | 51    | `lement`   |
| 4     | `ere`      | 20    | `emre`     | 36    | `lere`     | 52    | `lemre`    |
| 5     | `eret`     | 21    | `emret`    | 37    | `leret`    | 53    | `lemret`   |
| 6     | `eren`     | 22    | `emren`    | 38    | `leren`    | 54    | `lemren`   |
| 7     | `erent`    | 23    | `emrent`   | 39    | `lerent`   | 55    | `lemrent`  |
| 8     | `ebe`      | 24    | `embe`     | 40    | `lebe`     | 56    | `lembe`    |
| 9     | `ebet`     | 25    | `embet`    | 41    | `lebet`    | 57    | `lembet`   |
| 10    | `eben`     | 26    | `emben`    | 42    | `leben`    | 58    | `lemben`   |
| 11    | `ebent`    | 27    | `embent`   | 43    | `lebent`   | 59    | `lembent`  |
| 12    | `ebre`     | 28    | `embre`    | 44    | `lebre`    | 60    | `lembre`   |
| 13    | `ebret`    | 29    | `embret`   | 45    | `lebret`   | 61    | `lembret`  |
| 14    | `ebren`    | 30    | `embren`   | 46    | `lebren`   | 62    | `lembren`  |
| 15    | `ebrent`   | 31    | `embrent`  | 47    | `lebrent`  | 63    | `lembrent` |

**Note:**
Values 60–63 are valid only in Lembrent-64.
In Lembrent-60, digits 0–59 are used.

### Pronunciation

#### Letter Sounds

Each letter in the Lembrent scheme has a single, consistent pronunciation
regardless of its position within a word.  The only exception is the vowel `e`,
which changes depending on whether it appears as a doubled pair (`ee`) or as a
single character (`e`).

| Letter(s) | IPA          | Approximate sound          |
|-----------|--------------|----------------------------|
| `ee`      | /ɪə/         | As in "here" or "ear"      |
| `e`       | /ɛ/          | As in "bed" or "set"       |
| `b`       | /b/          | As in "bed"                |
| `k`       | /k/          | As in "key"                |
| `l`       | /l/          | As in "leg"                |
| `m`       | /m/          | As in "map"                |
| `n`       | /n/          | As in "net"                |
| `r`       | /r/          | As in "run"                |
| `t`       | /t/          | As in "top"                |

#### Syllable Structure

The syllable structure of each digit is determined by the consonants present
between the two `e`s (i.e., `m`, `b`, and `r`):

- **If at least one consonant is present between the two `e`s**, there is a
  syllable break between them.  That break falls immediately after the `m` (or
  immediately after the initial `e` if no `m` is present).
- **If no consonant is present between the two `e`s**, the digit is
  monosyllabic.

The syllables of each digit are evenly stressed, unless a schwa has been
inserted (see [Consonant Clusters](#consonant-clusters) below).

Some examples illustrating these rules:

| Digit      | Value | Syllabification  | Notes                                                                |
|------------|-------|------------------|----------------------------------------------------------------------|
| `ee`       |     0 | /ɪə/             | No inter-vowel consonants; monosyllabic                              |
| `eet`      |     1 | /ɪənt/           | No inter-vowel consonants; monosyllabic                              |
| `leent`    |    35 | /lɪənt/          | No inter-vowel consonants; monosyllabic despite the `l` prefix       |
| `eme`      |    16 | /ɛm ɛ/           | `m` is present between the `e`s; break falls after `m`               |
| `lembrent` |    63 | /lɛm brɛnt/      | Break falls after `m`; `b` and `r` begin the second syllable         |

#### Clarity of Consonants

Because every consonant is semantically significant and the scheme contains no
phonetic redundancy, it is essential that every consonant is
**clearly and distinctly enunciated**.  Speakers accustomed to dialects that
soften or drop final consonants—in particular, final `t`—must take especial care
to pronounce each consonant fully.  Omitting or obscuring any consonant risks
the digit being misidentified.

#### Consonant Clusters

Speakers who find certain consonant clusters difficult (for example, `br`) are
permitted to insert a schwa (/ə/) to separate the consonants.  Where a schwa is
inserted, the syllable containing it is unstressed. For example:

> `lembrent` may be pronounced as /lɛm brɛnt/ **or** as /'lɛm bə 'rɛnt/

#### Vowel Tolerance

Because the vowels carry no semantic weight, some variation in vowel
pronunciation can be tolerated; the intended sounds (`/ɪə/` for `ee` and `/ɛ/`
for `e`) remain the targets, but slight deviation will not alter the meaning of
a digit.  Consonant accuracy is always the priority.

#### Consonant Tolerance

The fixed positional ordering of consonants makes the scheme inherently
resistant to certain consonant mispronunciations.  For example, a speaker who
renders `r` as /l/, or `t` as /d/, will still be understood correctly, provided
that the consonant is actually, and unambiguously, pronounced.  The listener can
resolve the correct value from the consonant's position alone.

## The `lembrent` Utility

### Requirements

- **Perl 5** (any reasonably modern version)

No non-core Perl modules are required.
The script uses only built-in Perl features.

### Usage

#### Synopsis

```
lembrent BASE [NUMBER...]
```

#### Arguments

| Argument   | Description                                                                              |
|------------|------------------------------------------------------------------------------------------|
| `BASE`     | The numeric base to use. Must be either `60` or `64`.                                    |
| `NUMBER`   | One or more non-negative integers to convert. Shell arithmetic expressions are accepted. |

If no `NUMBER` arguments are supplied, the script produces no output.

### Examples

#### Base-60 Examples

```bash
$ ./lembrent 60 1 2 3 59 3623 $((3*60**3 + 2*60**2 + 60))
seet-eet
seet-een
seet-eent
seet-lembent
seent-eet-ee-emrent
sere-eent-een-eet-ee
```

#### Base-64 Examples

```bash
$ ./lembrent 64 1 2 3 63 $((3*64**3 + 2*64**2 + 64))
keet-eet
keet-een
keet-eent
keet-lembrent
kere-eent-een-eet-ee
```

#### Step-by-Step Worked Example: 70 in Lembrent-60

The decimal number **70** expressed in base 60 requires two significant digits:

- **60¹ place:** 70 ÷ 60 = 1 remainder 10 → most significant digit = 1
- **60⁰ place:** remainder = 10 → least significant digit = 10

Mapping each digit value to its Lembrent name:

| Digit value | Lembrent name | Derivation            |
|-------------|---------------|-----------------------|
| 1           | `eet`         | 2⁰ = 1                |
| 10          | `eben`        | 2³ + 2¹ = 8 + 2 = 10  |

The number has **two** significant digits, so the length digit has value 2:

| Length value | Lembrent name | Derivation |
|--------------|---------------|------------|
| 2            | `een`         | 2¹ = 2     |

Assembling the full name for base-60 (prefix `s`):

```
s  +  een  +  -eet  +  -eben
= seen-eet-eben
```

### Installation

1. Clone or download the repository:

   ```bash
   git clone https://github.com/Warwick-Allen/base60.git
   cd base60/lembrent
   ```

2. Ensure the script is executable:

   ```bash
   chmod +x lembrent
   ```

3. Optionally, place it on your `PATH`:

   ```bash
   sudo cp lembrent /usr/local/bin/lembrent
   ```

4. Invoke it directly:

   ```bash
   ./lembrent 60 42
   ```

### How It Works (Implementation Notes)

The script is written in idiomatic, compact Perl.
Its core logic comprises two subroutines:

**`a($n)`** —
Converts a single digit value (0–63) to its Lembrent name.
It iterates over the characters of the string `"lembrent"`,
keeping each character if it is the vowel `e`,
or if the corresponding bit is set in `$n`
(tested by shifting a sentinel value through the bits).
The result is the phonetic name of the digit.

**`b($d)`** —
Recursively decomposes a number into its base-60 or base-64 digits
(most significant first),
calling `a()` on each digit and joining them with hyphens.

The main loop then:

1. Calls `b()` to obtain the significant-digit string.
2. Counts the number of significant digits (by counting hyphens).
3. Constructs the length digit using `b()` again on that count.
4. Prepends the appropriate base prefix (`s` or `k`) in place of the first
   hyphen.
5. Handles the special case of zero, printing `<prefix>ee` directly.

---

## Licence

This project is released under the [MIT Licence](../LICENCE).

Copyright © 2026 Warwick Allen

[github.com/Warwick-Allen/base60/glyphs]:
https://github.com/Warwick-Allen/base60/blob/main/glyphs/README.md
