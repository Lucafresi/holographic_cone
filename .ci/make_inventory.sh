set -euo pipefail
mkdir -p .ci/inventory
for b in $(git for-each-ref --format='%(refname:short)' refs/remotes/origin); do
  bn="${b#origin/}"                # togli 'origin/'
  safe="${bn//\//__}"              # rimpiazza '/' con '__'
  git ls-tree -r --name-only "$b" > ".ci/inventory/files-${safe}.txt" || true
done
wc -l .ci/inventory/files-*.txt | sort -n
