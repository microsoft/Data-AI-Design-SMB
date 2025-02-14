#!/usr/bin/env bash
set -euo pipefail
[[ ${DEBUG-} =~ ^1|yes|true$ ]] && set -o xtrace

tmpdir=$(mktemp -d)
pub_repository=https://github.com/francesco-sodano/itsarag.git
script_dir=$(dirname "$(readlink -f "$0")")
files_to_remove=(
    'src/chat-app/rag_assistant.py' 
    'src/chat-app/multi_agent_assistant.py' 
    'assets/docs/ITSARAG-Coach Guide.pptx'
)

cp -r -a its-a-rag $tmpdir/

cd $tmpdir/its-a-rag

for file in $(find ./ -name \*.ipynb)
do
    printf "  Removing solution from %s\n" ${file}
    python3 ${script_dir}/publish.py ${file}
done

for file in $(find ./ -name \*.md)
do 
    printf "  Removing solution from %s\n" ${file}
    sed -i -e '/<!-- BEGIN SOLUTION -->/,/<!-- END SOLUTION -->/d' ${file}
done

for file in $(find ./ -regex '.*[_-]solution\..*' )
do
    printf "  Removing %s\n" ${file}
    rm ${file}
done

for file in "${files_to_remove[@]}"
do
    printf "  Removing %s\n" "${file}"
    rm "${file}"
done

git init
git add . 
git commit -m "Initial commit"
git remote add origin "$pub_repository"

## Use diff when testing publication
# diff --color -r --ignore-trailing-space /tmp/itsarag/ $tmpdir/its-a-rag --exclude .git --exclude __pycache__ --exclude file::memory || true

echo "Are you sure you want to force push to $pub_repository? (y/n)"
read answer
if [ "$answer" != "${answer#[Yy]}" ] ;then
    echo "Pushing to $pub_repository..."
    git push -f -u origin main
else
    echo "Exiting"
    exit 1
fi