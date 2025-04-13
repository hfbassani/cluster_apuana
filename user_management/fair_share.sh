#!/bin/bash
# setup_fairshare.sh

INPUT="advisors.csv"

# Create parent accounts
sacctmgr -i add account founders Fairshare="840"
sacctmgr -i add account researchers Fairshare="160"

# Process each advisor
while IFS=, read -r advisor email group contribution; do
  if [ "$group" == "founder" ]; then
    parent="founders"
    # Special cases
    if [ "$email" == "tbl@cin.ufpe.br" ]; then
      shares=52  # Teresa
    elif [ "$email" == "fatc@cin.ufpe.br" ]; then
      shares=26  # Chico
    else
      shares=14  # Regular founders
    fi
  else
    parent="researchers"
    shares=4  # All researchers
  fi

  sacctmgr -i add account "${advisor}_group" parent="$parent" Fairshare="$shares"
  echo "Created ${advisor}_group under $parent with $shares shares"
done < "$INPUT"

# Verify
sacctmgr show assoc format=account,user,fairshare