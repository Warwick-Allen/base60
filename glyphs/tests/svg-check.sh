#!/bin/bash -e

mk-glyph() {
  svg=; [ $1 == svg ] && svg=--svg
  glyphs --clean --force --scheme $radix --digit $digit $svg -o $name-$1.$1
}
dump-png() {
  n=$name-$1
  convert $n.png -geometry 480x480 $n.mono
  xxd -p $n.mono $n.hex
  perl -pe 's/([0-9a-f])/printf "%04b",eval"0x$1"/ge' $n.hex >$n.bin
}
for radix in 60 64; do
  for digit in 0 1 2 3 4 5 8 9 16 17 32 33 $((radix - 1)); do
    name=$(printf 'r%02d_d%02d' $radix $digit)
    find . -regex '.*'$name'.*\.\(bin\|hex\|mono\|ppm\|png\|raw\|svg\)' \
      -exec rm -v {} +
    (
      set -x
      mk-glyph png
      dump-png png
      mk-glyph svg
      convert $name-svg.{sv,pn}g
      dump-png svg
      diff $name-{pn,sv}g.bin >$name.diff ||:
    )
  done
done
