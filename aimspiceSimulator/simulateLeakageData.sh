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
corners=("FF" "TT")
temperatures=("00" "27" "70")
static_scenarios=("I05" "I07" "I09" "I11")

# Define specific scenarios
scenarios=(
    "0.400 0.1u 0.1u 0.3u 0.1u"
    "0.450 0.1u 0.1u 0.3u 0.1u"
    "0.475 0.1u 0.1u 0.3u 0.1u"
    "0.500 0.1u 0.1u 0.3u 0.1u"
    "0.525 0.1u 0.1u 0.3u 0.1u"
    "0.550 0.1u 0.1u 0.3u 0.1u"
    "0.575 0.1u 0.1u 0.3u 0.1u"
    "0.600 0.1u 0.1u 0.3u 0.1u"
    "0.625 0.1u 0.1u 0.3u 0.1u"
    "0.650 0.1u 0.1u 0.3u 0.1u"
    "0.675 0.1u 0.1u 0.3u 0.1u"
    "0.700 0.1u 0.1u 0.3u 0.1u"
    "0.725 0.1u 0.1u 0.3u 0.1u"
    "0.750 0.1u 0.1u 0.3u 0.1u"
    "0.775 0.1u 0.1u 0.3u 0.1u"
    "0.800 0.1u 0.1u 0.3u 0.1u"
    "0.600 0.1u 0.1u 0.100u 0.1u"
    "0.600 0.1u 0.1u 0.125u 0.1u"
    "0.600 0.1u 0.1u 0.150u 0.1u"
    "0.600 0.1u 0.1u 0.175u 0.1u"
    "0.600 0.1u 0.1u 0.200u 0.1u"
    "0.600 0.1u 0.1u 0.225u 0.1u"
    "0.600 0.1u 0.1u 0.250u 0.1u"
    "0.600 0.1u 0.1u 0.275u 0.1u"
    "0.600 0.1u 0.1u 0.300u 0.1u"
    "0.600 0.1u 0.1u 0.325u 0.1u"
    "0.600 0.1u 0.1u 0.350u 0.1u"
    "0.600 0.1u 0.1u 0.375u 0.1u"
    "0.600 0.1u 0.1u 0.400u 0.1u"
    "0.600 0.1u 0.1u 0.425u 0.1u"
    "0.600 0.1u 0.1u 0.450u 0.1u"
    "0.600 0.1u 0.1u 0.475u 0.1u"
    "0.600 0.1u 0.1u 0.500u 0.1u"
    "0.600 0.1u 0.1u 0.525u 0.1u"
    "0.600 0.1u 0.1u 0.550u 0.1u"
    "0.600 0.1u 0.1u 0.575u 0.1u"
)

total_iterations=$(( ${#scenarios[@]} * ${#corners[@]} * ${#temperatures[@]}* ${#static_scenarios[@]}))
current_iteration=0
# Loop through scenarios
for scenario in "${scenarios[@]}"; do
    read -r vdd n_width n_length p_width p_length <<< "$scenario"
    # MODIFICATION: Convert spaces to underscores for directory naming
    scenario_dir=$(echo "$scenario" | tr ' ' '_')

    # MODIFICATION: Create the necessary directories
    mkdir -p "../figures/aimspice/${scenario_dir}/CSV/leakage_current"    
    # Update param.cir file
    update_param_cir "$vdd" "$n_width" "$n_length" "$p_width" "$p_length"

    # Run simulations for each corner and temperature
    for corner in "${corners[@]}"; do
        for temp in "${temperatures[@]}"; do
            for static in "${static_scenarios[@]}"; do
                csv_file="${corner}${temp}${static}.csv"
                touch "$csv_file"
                sleep 0.2
                ./aimspice64 "$csv_file" &
                sleep 0.5
                xdotool key Return
                sleep 0.03
                xdotool type ".include DFF${corner}.cir"
                xdotool key Return
                sleep 0.03
                xdotool type ".include ${static}.cir"
                xdotool key Return
                sleep 0.03
                xdotool type ".option temp=${temp}"
                xdotool key Return
                sleep 0.03
                xdotool type ".plot i(vdd)"
                xdotool key Return
                sleep 0.03
                xdotool key ctrl+s
                sleep 0.03
                xdotool key ctrl+r
                sleep 0.5
                xdotool key alt+F4
                sleep 0.5
                # # MODIFICATION: Move the CSV file to the appropriate directory
                rm "${corner}${temp}${static}.log"
                mv "$csv_file" "../figures/aimspice/${scenario_dir}/CSV/leakage_current"	            
                current_iteration=$((current_iteration + 1))
                percentage=$(echo "scale=2; $current_iteration / $total_iterations * 100" | bc)
                echo "$current_iteration / $total_iterations"
                echo "Progress: $percentage% completed."
                echo "${scenario_dir}"
            done
        done
    done
done


