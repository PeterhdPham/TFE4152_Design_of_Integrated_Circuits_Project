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
corners=("FF" "FS" "SF" "SS" "TT")
temperatures=("00" "27" "70")

# Copy initial command to clipboard
echo ".plot id(m:nand_2:mn1:1) id(m:nand_3:mn1:1)" | xclip -selection clipboard

# Define specific scenarios
scenarios=(
    "0.45 0.1u 0.1u 0.2u 0.1u"
    "0.50 0.1u 0.1u 0.2u 0.1u"
    "0.55 0.1u 0.1u 0.2u 0.1u"
    "0.60 0.1u 0.1u 0.2u 0.1u"
    "0.65 0.1u 0.1u 0.2u 0.1u"
    "0.70 0.1u 0.1u 0.2u 0.1u"
    "0.75 0.1u 0.1u 0.2u 0.1u"
    "0.80 0.1u 0.1u 0.2u 0.1u"
    "0.85 0.1u 0.1u 0.2u 0.1u"
    "0.90 0.1u 0.1u 0.2u 0.1u"
    "0.60 0.1u 0.1u 0.1u 0.1u"
    "0.60 0.2u 0.2u 0.2u 0.2u"
    "0.60 0.1u 0.1u 0.3u 0.1u"
    "0.60 0.1u 0.1u 0.3u 0.2u"
    "0.60 0.1u 0.1u 0.4u 0.2u"
)

total_iterations=$(( ${#scenarios[@]} * ${#corners[@]} * ${#temperatures[@]}))
current_iteration=0
# Loop through scenarios
for scenario in "${scenarios[@]}"; do
    read -r vdd n_width n_length p_width p_length <<< "$scenario"
    
    # Update param.cir file
    update_param_cir "$vdd" "$n_width" "$n_length" "$p_width" "$p_length"

    # Run simulations for each corner and temperature
    for corner in "${corners[@]}"; do
        for temp in "${temperatures[@]}"; do
            csv_file="${corner}${temp}I.csv"
            touch "$csv_file"
            ./aimspice64 "$csv_file" &
            sleep 0.5
            xdotool type ".include NAND${corner}.cir"
            xdotool key Return
            sleep 0.03
            xdotool type ".option temp=${temp}"
            xdotool key Return
            sleep 0.03
            xdotool key ctrl+v
            sleep 0.03
            xdotool key ctrl+s
            sleep 0.03
            xdotool key ctrl+r
            sleep 0.5
            xdotool key alt+F4
            sleep 0.5
            current_iteration=$((current_iteration + 1))
            percentage=$(echo "scale=2; $current_iteration / $total_iterations * 100" | bc)
            echo "Progress: $percentage% completed."
        done
        sleep 0.03
    done
    # Run post-processing script
    python3 leakage_current.py
done


