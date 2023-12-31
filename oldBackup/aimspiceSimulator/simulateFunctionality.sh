#!/bin/bash

# Function to update param.cir file
update_param_cir() {
    cat << EOF > param.cir
.param vdd_value = $1
* Device parameters for N-MOSFETs
.param N_Width= $2 
.param N_Length = $3

* Device parameters for P-MOSFETs
.param P_Width= $4                   
.param P_Length = $5
EOF
}

# List of all corner and temperature combinations
# corners=("FF" "FS" "SF" "SS" "TT")
# temperatures=("00" "27" "70")
# wave_scenarios=("W1" "W2" "W3")

corners=("FF" "TT")
temperatures=("00" "27" "70")
wave_scenarios=("W1")
# Copy initial command to clipboard


# # Define specific scenarios
# scenarios=(
#     # "0.50 0.1u 0.1u 0.2u 0.1u"
#     # "0.55 0.1u 0.1u 0.2u 0.1u"
#     # "0.60 0.1u 0.1u 0.2u 0.1u"
#     # "0.65 0.1u 0.1u 0.2u 0.1u"
#     # "0.75 0.1u 0.1u 0.4u 0.1u"
#     # "0.75 0.1u 0.1u 0.1u 0.1u"
#     # "0.75 0.1u 0.1u 0.3u 0.1u"''
# )

# Define specific scenarios
scenarios=(
    # "0.50 0.1u 0.1u 0.2u 0.1u"
    # "0.55 0.1u 0.1u 0.2u 0.1u"
    # "0.60 0.1u 0.1u 0.2u 0.1u"
    # "0.65 0.1u 0.1u 0.2u 0.1u"
    # "0.75 0.1u 0.1u 0.4u 0.1u"
    # "0.75 0.1u 0.1u 0.1u 0.1u"
    # "0.75 0.1u 0.1u 0.3u 0.1u"''
)

total_iterations=$(( ${#scenarios[@]} * ${#corners[@]} * ${#temperatures[@]} * ${#wave_scenarios[@]} ))
current_iteration=0
# Loop through scenarios
for scenario in "${scenarios[@]}"; do
    read -r vdd n_width n_length p_width p_length <<< "$scenario"
	scenario_dir=$(echo "$scenario" | tr ' ' '_')

    # MODIFICATION: Create the necessary directories
    mkdir -p "../figures/aimspice/${scenario_dir}/CSV/functionality"  
    # Update param.cir file
    update_param_cir "$vdd" "$n_width" "$n_length" "$p_width" "$p_length"

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
	      sleep 0.03
	      xdotool type ".option temp=${temp}"
	      xdotool key Return
	      sleep 0.03
	      xdotool type ".include wave${wave}.cir"
	      xdotool key Return
	      sleep 0.03
	      # Check if the wave scenario is W3 and include v(Reset) if it is
	      if [ "$wave" == "W3" ]; then
		  xdotool type ".plot v(Data) v(Clk) v(Out) v(Reset)"
	      else
		  xdotool type ".plot v(Data) v(Clk) v(Out)"
	      fi
	      xdotool key Return
	      sleep 0.03

	      # Save and run the simulation
	      xdotool key ctrl+s
	      sleep 0.03	
	      xdotool key ctrl+r
	      sleep 0.5

	      # Close Aimspice
	      xdotool key alt+F4
	      sleep 0.5
          # MODIFICATION: Move the CSV file to the appropriate directory
          mv "$csv_file" "../figures/aimspice/${scenario_dir}/CSV/functionality"		  
	      current_iteration=$((current_iteration + 1))
          percentage=$(echo "scale=2; $current_iteration / $total_iterations * 100" | bc)
          echo "$current_iteration / $total_iterations"
		  echo "Progress: $percentage% completed."
	    done
	    sleep 0.03
	  done
	done
done
echo "Script completed."

