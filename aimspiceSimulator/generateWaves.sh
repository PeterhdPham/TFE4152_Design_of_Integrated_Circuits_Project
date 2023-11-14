#!/bin/bash

# List of all corner, temperature, and wave scenario combinations
corners=("FF" "FS" "SF" "SS" "TT")
temperatures=("00" "27" "70")
wave_scenarios=("W1" "W2" "W3")

for corner in "${corners[@]}"; do
  for temp in "${temperatures[@]}"; do
    for wave in "${wave_scenarios[@]}"; do
      csv_file="${corner}${temp}${wave}.csv"

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
      xdotool type ".include wave${wave}.cir"
      xdotool key Return
      xdotool type ".tran 0.001n 200n 10n" 

      # Check if the wave scenario is W3 and include v(Reset) if it is
      if [ "$wave" == "W3" ]; then
        xdotool type ".plot v(Data) v(Clk) v(Out) v(Reset)"
      else
        xdotool type ".plot v(Data) v(Clk) v(Out)"
      fi
      xdotool key Return

      # Save and run the simulation
      xdotool key ctrl+s	
      xdotool key ctrl+r
      sleep 0.5

      # Close Aimspice
      xdotool key alt+F4
      sleep 0.5
    done
  done
done




python3 plotdff.py



