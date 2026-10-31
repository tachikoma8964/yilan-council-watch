#!/bin/sh
# Publish site/ to the gh-pages branch, which GitHub Pages serves. Run with GH_TOKEN set for the account that owns origin.
set -e
root=$(git rev-parse --show-toplevel)
origin=$(git -C "$root" remote get-url origin)
name=$(git -C "$root" config user.name)
email=$(git -C "$root" config user.email)
tmp=$(mktemp -d)
cp -R "$root/site/." "$tmp/"
rm -rf "$tmp/style-sample"
touch "$tmp/.nojekyll"
cd "$tmp"
git init -q -b gh-pages
git add -A
git -c user.name="$name" -c user.email="$email" commit -q -m "Publish site"
git -c credential.helper='!gh auth git-credential' push -f "$origin" gh-pages
