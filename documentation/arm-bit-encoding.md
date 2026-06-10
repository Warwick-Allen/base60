# Arm Bit Encoding

| Bit      | Decimal value | Angle | Sign | Elbow direction | Tip position        | ASCII representation |
|:---------|--------------:|------:|:----:|:----------------|:--------------------|:--------------------:|
| 2⁰ (LSB) |             1 |    0  |   -  | down            | ( 0.5,   0) – right |        ` .v`         |
| 2¹       |             2 |    0  |   +  | up              | ( 0.5,   0) – right |        ` .^`         |
| 2²       |             4 |  π/2  |   -  | right-facing    | (   0, 0.5) – top   |        ` .>`         |
| 2³       |             8 |  π/2  |   +  | left-facing     | (   0, 0.5) – top   |        `<. `         |
| 2⁴       |            16 |    π  |   -  | up              | (-0.5,   0) – left  |        `^. `         |
| 2⁵ (MSB) |            32 |    π  |   +  | down            | (-0.5,   0) – left  |        `v. `         |
