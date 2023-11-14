#!/bin/bash

# List of all corner, temperature, and wave scenario combinations
corners=("FF" "FS" "SF" "SS" "TT")
temperatures=("00" "27" "70")


for corner in "${corners[@]}"; do
  for temp in "${temperatures[@]}"; do
      csv_file="${corner}${temp}SC.csv"

      # Generate an empty CSV file
      touch "$csv_file"

      # Run Aimspice
      ./aimspice64 "$csv_file" &

      # Wait for Aimspice to open (adjust sleep duration as needed)
      sleep 0.5

      # Simulate keyboard input using xdotool (or similar tool)
      xdotool type ".include DFF${corner}.cir"
      xdotool key Return
      xdotool type ".option temp=${temp}"
      xdotool key Return
      xdotool type ".include waveW1.cir"
      xdotool key Return
      xdotool type ".tran 0.001n 130n 100n"
      xdotool key Return
      xdotool type ".plot v(Data) v(Clk) v(Out)"
      xdotool key Return

      # Save and run the simulation
      xdotool key ctrl+s	
      xdotool key ctrl+r
      sleep 0.7

      # Close Aimspice
      xdotool key alt+F4
      sleep 0.5
  done
done




python3 plotdffsingle.py



