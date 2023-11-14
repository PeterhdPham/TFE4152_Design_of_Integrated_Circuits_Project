#!/bin/bash

# List of all corner, temperature, and wave scenario combinations
corners=("FF" "FS" "SF" "SS" "TT")
temperatures=("00" "27" "70")

echo ".plot id(m:nand_2:mn1:1) id(m:nand_3:mn1:1)" | xclip -selection clipboard

for corner in "${corners[@]}"; do
  for temp in "${temperatures[@]}"; do
    csv_file="${corner}${temp}I.csv"
      # Generate an empty CSV file
      touch "$csv_file"

      # Run Aimspice
      ./aimspice64 "$csv_file" &

      # Wait for Aimspice to open (adjust sleep duration as needed)
      sleep 0.5

      # Simulate keyboard input using xdotool (or similar tool)
      xdotool type ".include NAND${corner}.cir"
      xdotool key Return
      

      xdotool type ".option temp=${temp}"
      xdotool key Return      
      
      xdotool key ctrl+v
      xdotool key Return
      

      # Save and run the simulation
      xdotool key ctrl+s
      
      xdotool key ctrl+r
      sleep 1

      # Close Aimspice
      xdotool key alt+F4
      sleep 0.2
    done
  done

python3 leakage_current.py



