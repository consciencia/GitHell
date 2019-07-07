#!/bin/env bash

MY_PATH="`dirname \"$0\"`"
MY_PATH="`( cd \"$MY_PATH\" && pwd )`"
if [ -z "$MY_PATH" ] ; then
  exit 1  # fail
fi
MY_PATH=$MY_PATH/githell.py
MY_PATH=${MY_PATH//\/.\//\/}
while [[ $MY_PATH =~ ([^/][^/]*/\.\./) ]]; do
    MY_PATH=${MY_PATH/${BASH_REMATCH[0]}/}
done
echo "Origin is $MY_PATH."

TARGET="/usr/bin/githell"

echo "Generating executable file in $TARGET..."
cat > ./TEMP <<- EOM
#!/bin/env bash

source ~/.bash_profile
export PYTHONDONTWRITEBYTECODE=1

python $MY_PATH \$@
EOM
sudo cp ./TEMP $TARGET
rm ./TEMP

echo "Adding +x flag..."
sudo chmod +x $TARGET

echo "Done"
