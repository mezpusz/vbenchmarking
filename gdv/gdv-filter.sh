
set -euo "pipefail"

pushd results
mkdir $1
unzip -q $1.logfiles.zip
pushd $1.logfiles/
for f in $(grep -lr 'Refutation found' .)
do
    tail -n +7 $f > ../$1/$f
done
popd
popd
