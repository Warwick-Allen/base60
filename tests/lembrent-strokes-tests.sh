#!/bin/bash -ex

url="http://127.0.0.1:8000"
curl -s $url >/dev/null 2>&1 || {
  pip install -r api/requirements.txt
  ( uvicorn api.app:app --reload --port 8000 & )
}

for method in api local; do
  for format in png svg; do
    for radix in 60 64; do
      for e in {0..5}; do
        digit=$((2**e))
        fname=~/test-r$radix$(printf 'd%02d' $digit).$method.$format
        if [ $method == local ]; then
          glyphs --clean --scheme $radix --digit $digit --$format $fname
        else
          curl -s "http://127.0.0.1:8000/lembrent/$radix/$digit?png=0&svg=0&$format=1" |
          jq -r .$format[0] |
          if [ $format == png ]; then
            base64 -d
          else
            cat
          fi >$fname
        fi
        firefox $fname
      done
    done
  done
done
